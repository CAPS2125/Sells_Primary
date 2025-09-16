import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import streamlit as st

# La función con el decorador asegura que la conexión y la base de datos
# se creen solo una vez y persistan entre las ejecuciones de la app.
@st.cache_resource
def get_db_engine():
    # Define la ruta persistente para la base de datos SQLite
    # En entornos de Streamlit Cloud, esto la guarda en una ubicación estable.
    db_path = os.path.join(os.getcwd(), "tienda_escolar.db")
    DATABASE_URL = f"sqlite:///{db_path}"
    
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()

    # Definición de todas las tablas
    class Productos(Base):
        __tablename__ = 'productos'
        id_producto = Column(Integer, primary_key=True, index=True)
        nombre = Column(String(50), nullable=False)
        descripcion = Column(String(255))
        precio_compra = Column(Numeric(10, 2), nullable=False)
        precio_venta = Column(Numeric(10, 2), nullable=False)
        fecha_creacion = Column(DateTime, default=datetime.utcnow)
        inventario = relationship("Inventario", back_populates="producto", uselist=False)
        detalles_de_venta = relationship("DetalleVenta", back_populates="producto_detalle")

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
        detalles_de_venta = relationship("DetalleVenta", back_populates="venta")

    class DetalleVenta(Base):
        __tablename__ = 'detalle_venta'
        id_detalle = Column(Integer, primary_key=True, index=True)
        id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
        id_producto = Column(Integer, ForeignKey("productos.id_producto"))
        cantidad = Column(Integer, nullable=False)
        precio_unitario = Column(Numeric(10, 2), nullable=False)
        venta = relationship("Ventas", back_populates="detalles_de_venta")
        producto_detalle = relationship("Productos", back_populates="detalles_de_venta")

    class Gastos(Base):
        __tablename__ = 'gastos'
        id_gasto = Column(Integer, primary_key=True, index=True)
        descripcion = Column(String(100), nullable=False)
        monto = Column(Numeric(10, 2), nullable=False)
        fecha_gasto = Column(DateTime, default=datetime.utcnow)
    
    # Crea las tablas si no existen. Esta línea se ejecuta solo una vez.
    Base.metadata.create_all(bind=engine)
    return engine

# Uso del motor de la base de datos
engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
