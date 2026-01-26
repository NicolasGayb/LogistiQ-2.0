from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Substitua pela sua URL de conexão real (a mesma do seu .env)
DATABASE_URL = "postgresql://postgres:Zerinhomilgrau003@localhost:5432/logistiq"

def test_connection():
    try:
        # Cria a "engine" (o motor de conexão)
        engine = create_engine(DATABASE_URL)
        
        # Tenta conectar e executar um comando simples
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexão bem-sucedida! O banco respondeu:", result.scalar())
            
    except OperationalError as e:
        print("❌ Erro de conexão. Verifique senha, porta ou host.")
        print(f"Detalhes: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_connection()