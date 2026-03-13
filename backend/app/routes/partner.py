from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from pydantic import BaseModel, EmailStr

# Importações do seu projeto
from app.database import get_db
from app.models.partner import Partner
from app.models.operation import Operation
from app.models.enum import MovementType, MovementEntityType # Certifique-se que PARTNER existe aqui
from app.core.dependencies import get_current_user
from app.services.movement_service import MovementService # Serviço de Logs
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse

router = APIRouter(prefix="/partners", tags=["Parceiros"])

# 1. LISTAR COM FILTROS E PAGINAÇÃO
@router.get("/", response_model=List[PartnerResponse])
def list_partners(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    type: Optional[str] = None, 
    active: Optional[bool] = None,
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # --- DEBUG START ---
    print("\n" + "="*30)
    print(f"🕵️ DEBUG: Solicitante: {current_user.email}")
    print(f"🕵️ DEBUG: Role: {current_user.role}")
    print(f"🕵️ DEBUG: Meu Company ID: {current_user.company_id}")
    
    # Lógica de Filtro
    user_role = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role).upper()

    if user_role == "SYSTEM_ADMIN":
        print("✅ Modo: SYSTEM_ADMIN (Vê tudo)")
        query = db.query(Partner)
        if company_id:
            query = query.filter(Partner.company_id == company_id)
    else:
        print(f"🔒 Modo: EMPRESA (Filtra por {current_user.company_id})")
        query = db.query(Partner).filter(Partner.company_id == current_user.company_id)

    # Conta quantos existem ANTES dos filtros de busca/texto
    total_in_company = query.count()
    print(f"📊 Total bruto na minha empresa: {total_in_company}")

    # Aplica Filtros de Texto/Tipo
    if search:
        print(f"🔎 Filtrando por texto: {search}")
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Partner.name.ilike(search_term),
                Partner.document.ilike(search_term),
                Partner.email.ilike(search_term)
            )
        )

    if type == "CUSTOMER":
        query = query.filter(Partner.is_customer == True)
    elif type == "SUPPLIER":
        query = query.filter(Partner.is_supplier == True)

    if active is not None:
        print(f"⚙️ Filtrando por Active: {active}")
        query = query.filter(Partner.active == active)

    results = query.order_by(desc(Partner.created_at)).offset(skip).limit(limit).all()
    
    print(f"🚀 Resultado final enviado: {len(results)} parceiros")
    print("="*30 + "\n")
    
    return results

# 2. CRIAR PARCEIRO
@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
def create_partner(
    request: Request,
    partner_in: PartnerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "SYSTEM_ADMIN" and partner_in.company_id and partner_in.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para criar parceiros para esta empresa.")
    
    if not partner_in.company_id:
        partner_in.company_id = current_user.company_id

    # Verificar se o documento já existe na mesma empresa
    existing = db.query(Partner).filter(
        Partner.document == partner_in.document,
        Partner.company_id == partner_in.company_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Este documento já está em uso.")

    new_partner = Partner(
        company_id=partner_in.company_id,
        name=partner_in.name,
        document=partner_in.document,
        email=partner_in.email,
        phone=partner_in.phone,
        city=partner_in.city,
        state=partner_in.state,
        address=partner_in.address,
        is_customer=partner_in.is_customer,
        is_supplier=partner_in.is_supplier
    )

    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)

    # --- REGISTRO DE MOVIMENTO ---
    MovementService.create_manual(
        db=db,
        company_id=partner_in.company_id,
        entity_type=MovementEntityType.PARTNER,
        entity_id=new_partner.id,
        movement_type=MovementType.CREATION,
        description=f"Parceiro '{new_partner.name}' criado.",
        created_by=current_user.id,
        ip_address=request.client.host
    )

    return new_partner

# 3. OBTER UM
@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(
    partner_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role == "SYSTEM_ADMIN":
        partner = db.query(Partner).filter(Partner.id == partner_id).first()

    partner = db.query(Partner).filter(
        Partner.id == partner_id, 
        Partner.company_id == current_user.company_id
    ).first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado.")
    return partner

# 4. ATUALIZAR
@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
    request: Request, # Adicionado para IP
    partner_id: UUID, 
    partner_in: PartnerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_role = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role).upper()

    query = db.query(Partner).filter(Partner.id == partner_id)

    if user_role != "SYSTEM_ADMIN":
        query = query.filter(Partner.company_id == current_user.company_id)

    partner = query.first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado.")

    update_data = partner_in.dict(exclude_unset=True)
    
    if 'document' in update_data and update_data['document'] != partner.document:
        existing = db.query(Partner).filter(
            Partner.document == update_data['document'],
            Partner.company_id == current_user.company_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Este documento já está em uso.")

    # Guardar nome antigo para log
    old_name = partner.name

    for key, value in update_data.items():
        setattr(partner, key, value)

    db.commit()
    db.refresh(partner)

    # --- REGISTRO DE MOVIMENTO ---
    MovementService.create_manual(
        db=db,
        company_id=current_user.company_id,
        entity_type=MovementEntityType.PARTNER,
        entity_id=partner.id,
        movement_type=MovementType.UPDATED,
        description=f"Parceiro '{old_name}' atualizado.",
        created_by=current_user.id,
        ip_address=request.client.host
    )

    return partner

# 5. TOGGLE ACTIVE
@router.patch("/{partner_id}/toggle-active")
def toggle_partner_active(
    request: Request,
    partner_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    partner = db.query(Partner).filter(
        Partner.id == partner_id,
        Partner.company_id == current_user.company_id
    ).first()

    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado")

    partner.active = not partner.active
    db.commit()

    # --- REGISTRO DE MOVIMENTO ---
    status_str = "ativado" if partner.active else "desativado"
    MovementService.create_manual(
        db=db,
        company_id=current_user.company_id,
        entity_type=MovementEntityType.PARTNER,
        entity_id=partner.id,
        movement_type=MovementType.UPDATED,
        description=f"Parceiro '{partner.name}' {status_str}.",
        created_by=current_user.id,
        ip_address=request.client.host
    )

    return {"message": "Status atualizado", "active": partner.active}

# 6. EXCLUIR
@router.delete("/{partner_id}")
def delete_partner(
    request: Request,
    partner_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    partner = db.query(Partner).filter(
        Partner.id == partner_id,
        Partner.company_id == current_user.company_id
    ).first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro não encontrado.")

    has_operations = db.query(Operation).filter(Operation.partner_id == partner_id).first()
    
    if has_operations:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível excluir parceiro com histórico. Tente desativá-lo."
        )

    partner_name = partner.name # Salva nome antes de apagar

    # --- REGISTRO DE MOVIMENTO (Antes de deletar) ---
    try:
        MovementService.create_manual(
            db=db,
            company_id=current_user.company_id,
            entity_type=MovementEntityType.PARTNER,
            entity_id=partner.id,
            movement_type=MovementType.DELETED,
            description=f"Parceiro '{partner_name}' excluído permanentemente.",
            created_by=current_user.id,
            ip_address=request.client.host
        )
    except Exception as e:
        print(f"Aviso: Não foi possível registrar log de exclusão: {e}")

    db.delete(partner)
    db.commit()
    return {"message": "Parceiro excluído com sucesso."}

# 7. ESTATÍSTICAS
@router.get("/stats/count")
def get_partners_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    total = db.query(Partner).filter(Partner.company_id == current_user.company_id).count()
    customers = db.query(Partner).filter(Partner.company_id == current_user.company_id, Partner.is_customer == True).count()
    suppliers = db.query(Partner).filter(Partner.company_id == current_user.company_id, Partner.is_supplier == True).count()
    
    return {
        "total": total,
        "customers": customers,
        "suppliers": suppliers
    }