from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config import Base, engine

# Definición de la tabla Productos
class Productos(Base):
    __tablename__ = 'productos'

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    precio_compra = Column(Numeric(10, 2), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con la tabla de inventario
    inventario = relationship("Inventario", back_populates="producto")
    # Relación con la tabla de detalle de venta
    detalles_venta = relationship("DetalleVenta", back_populates="producto")

# Definición de la tabla Inventario
class Inventario(Base):
    __tablename__ = 'inventario'

    id_inventario = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, default=0, nullable=False)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con la tabla de productos
    producto = relationship("Productos", back_populates="inventario")

# Definición de la tabla Ventas
class Ventas(Base):
    __tablename__ = 'ventas'

    id_venta = Column(Integer, primary_key=True, index=True)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    total_venta = Column(Numeric(10, 2), nullable=False)

    # Relación con la tabla de detalle de venta
    detalles = relationship("DetalleVenta", back_populates="venta")

# Definición de la tabla DetalleVenta
class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    # Relaciones para acceder a los datos de la venta y el producto
    venta = relationship("Ventas", back_populates="detalles")
    producto = relationship("Productos", back_populates="detalles_venta")

# Definición de la tabla Clientes
class Clientes(Base):
    __tablename__ = 'clientes'

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    puntos_lealtad = Column(Integer, default=0)

# Código para crear las tablas en la base de datos
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tablas de la base de datos creadas exitosamente.")
