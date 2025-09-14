import streamlit as st
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime

# Define la ruta de la base de datos en la raíz del proyecto.
# Esto asegura que el archivo 'tienda_escolar.db' se cree en la misma ubicación que tu aplicación.
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = "sqlite:///" + os.path.join(basedir, "tienda_escolar.db")

# Crea el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crea una clase base para las clases declarativas
Base = declarative_base()

# Crea una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definición de la tabla Productos
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

# Definición de la tabla Productos
class Productos(Base):
    __tablename__ = 'productos'
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    precio_compra = Column(Numeric(10, 2), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    # Esta es la línea crucial
    inventario = relationship("Inventario", back_populates="producto", uselist=False)
    detalles_venta = relationship("DetalleVenta", back_populates="producto")

# Definición de la tabla Inventario
class Inventario(Base):
    __tablename__ = 'inventario'
    id_inventario = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, default=0, nullable=False)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    producto = relationship("Productos", back_populates="inventario")

# Definición de la tabla DetalleVenta
class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    venta = relationship("Ventas", back_populates="detalles")
    producto = relationship("Productos", back_populates="detalles_venta")

# Definición de la tabla Clientes (opcional)
class Clientes(Base):
    __tablename__ = 'clientes'
    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    puntos_lealtad = Column(Integer, default=0)

# Código para crear las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tablas de la base de datos creadas exitosamente.")

if __name__ == "__main__":
    create_tables()
