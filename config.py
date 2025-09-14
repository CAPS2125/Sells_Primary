from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configura tu base de datos SQLite. Es ideal para empezar.
# SQLAlchemy creará un archivo llamado 'tienda_escolar.db' en tu directorio.
DATABASE_URL = "sqlite:///tienda_escolar.db"

# Crea el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crea una clase base para las clases declarativas
Base = declarative_base()

# Crea una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
