from supabase import create_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# Configuração do Supabase como banco principal
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")

# Cliente Supabase
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_postgres_url_from_supabase():

    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL não configurada")
    

    project_id = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
    

    db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
    
    if db_password:
        DATABASE_URL = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
        return DATABASE_URL
    else:
        # Se não tiver senha, use apenas o cliente Supabase
        return None

# Tenta criar engine SQLAlchemy se tiver credenciais completas
DATABASE_URL = get_postgres_url_from_supabase()

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Use apenas o cliente Supabase
    engine = None
    SessionLocal = None

Base = declarative_base()