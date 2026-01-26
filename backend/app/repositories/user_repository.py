# Importação padrão
from sqlalchemy.orm import Session

# Importação local
from app.models.user import User

# Função para obter um usuário pelo email
def get_user_by_email(
    db: Session,
    email: str
) -> User | None:
    '''Obtém um usuário pelo email.
    
    Args:
        db (Session): Sessão do banco de dados.
        email (str): Email do usuário a ser buscado.
    '''
    return db.query(User).filter(User.email == email).first()