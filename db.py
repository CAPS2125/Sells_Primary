import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime

# Define la ruta de la base de datos en la raíz del proyecto.
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
    
    # La relación con Inventario ahora usa un nombre más descriptivo
    # y `uselist=False` para indicar una relación de uno a uno.
    inventario_item = relationship("Inventario", back_populates="producto_item", uselist=False)
    
    # La relación con DetalleVenta ahora usa un nombre más descriptivo.
    detalles_de_venta = relationship("DetalleVenta", back_populates="producto_detalle")

# Definición de la tabla Inventario
class Inventario(Base):
    __tablename__ = 'inventario'
    id_inventario = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, default=0, nullable=False)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación que apunta de regreso a Productos.
    producto_item = relationship("Productos", back_populates="inventario_item")

# Definición de la tabla Ventas
class Ventas(Base):
    __tablename__ = 'ventas'
    id_venta = Column(Integer, primary_key=True, index=True)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    total_venta = Column(Numeric(10, 2), nullable=False)
    
    detalles_de_venta = relationship("DetalleVenta", back_populates="venta")

# Definición de la tabla DetalleVenta
class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    
    venta = relationship("Ventas", back_populates="detalles_de_venta")
    producto_detalle = relationship("Productos", back_populates="detalles_de_venta")

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
