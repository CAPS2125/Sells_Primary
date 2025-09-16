import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime
import streamlit as st

# Function to get the database connection
@st.cache_resource
def get_db_connection():
    """Returns the SQLAlchemy engine and Base for the database."""
    # Define the persistent path for the SQLite database file
    db_path = os.path.join(os.getcwd(), "tienda_escolar.db")
    DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(DATABASE_URL)
    Base = declarative_base()

    # Define all your database tables here (the classes you already have)
    class Productos(Base):
        __tablename__ = 'productos'
        id_producto = Column(Integer, primary_key=True, index=True)
        nombre = Column(String(50), nullable=False)
        descripcion = Column(String(255))
        precio_compra = Column(Numeric(10, 2), nullable=False)
        precio_venta = Column(Numeric(10, 2), nullable=False)
        fecha_creacion = Column(DateTime, default=datetime.utcnow)
        inventario = relationship("Inventario", back_populates="producto", uselist=False)
        detalles_venta = relationship("DetalleVenta", back_populates="producto")

    class Inventario(Base):
        __tablename__ = 'inventario'
        id_inventario = Column(Integer, primary_key=True, index=True)
        id_producto = Column(Integer, ForeignKey("productos.id_producto"))
        cantidad = Column(Integer, default=0, nullable=False)
        ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        producto = relationship("Productos", back_populates="inventario")

    class Ventas(Base):
        __tablename__ = 'ventas'
        id_venta = Column(Integer, primary_key=True, index=True)
        fecha_venta = Column(DateTime, default=datetime.utcnow)
        total_venta = Column(Numeric(10, 2), nullable=False)
        detalles = relationship("DetalleVenta", back_populates="venta")

    class DetalleVenta(Base):
        __tablename__ = 'detalle_venta'
        id_detalle = Column(Integer, primary_key=True, index=True)
        id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
        id_producto = Column(Integer, ForeignKey("productos.id_producto"))
        cantidad = Column(Integer, nullable=False)
        precio_unitario = Column(Numeric(10, 2), nullable=False)
        venta = relationship("Ventas", back_populates="detalles")
        producto = relationship("Productos", back_populates="detalles_venta")

    class Gastos(Base):
        __tablename__ = 'gastos'
        id_gasto = Column(Integer, primary_key=True, index=True)
        descripcion = Column(String(100), nullable=False)
        monto = Column(Numeric(10, 2), nullable=False)
        fecha_gasto = Column(DateTime, default=datetime.utcnow)
    
    # Create the tables if they don't exist
    Base.metadata.create_all(bind=engine)
    return engine, Base

# Get the engine and Base from the cached function
engine, Base = get_db_connection()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
