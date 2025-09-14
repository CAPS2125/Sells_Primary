import streamlit as st
from ..BD.tablas import SessionLocal, Ventas, DetalleVenta, Productos
from sqlalchemy import func
import pandas as pd
from datetime import date

st.title("Dashboard de Ventas 📊")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener ventas del día
def get_ventas_del_dia(db, dia):
    total_ventas = db.query(func.sum(Ventas.total_venta)).filter(func.date(Ventas.fecha_venta) == dia).scalar()
    num_transacciones = db.query(Ventas).filter(func.date(Ventas.fecha_venta) == dia).count()
    return total_ventas, num_transacciones

# Obtener productos más vendidos
def get_productos_mas_vendidos(db, dia):
    stmt = db.query(
        Productos.nombre,
        func.sum(DetalleVenta.cantidad).label('total_cantidad_vendida')
    ).join(DetalleVenta, Productos.id_producto == DetalleVenta.id_producto
    ).join(Ventas, DetalleVenta.id_venta == Ventas.id_venta
    ).filter(func.date(Ventas.fecha_venta) == dia
    ).group_by(Productos.nombre
    ).order_by(func.sum(DetalleVenta.cantidad).desc()).limit(5).all()
    
    return pd.DataFrame(stmt, columns=['Producto', 'Cantidad Vendida'])


# Usar el contexto de la base de datos
db = next(get_db())

dia_actual = date.today()

# Muestra las métricas
total_ventas_hoy, num_transacciones_hoy = get_ventas_del_dia(db, dia_actual)
ticket_promedio = total_ventas_hoy / num_transacciones_hoy if num_transacciones_hoy else 0

st.subheader(f"Resumen de Hoy ({dia_actual.strftime('%d-%m-%Y')})")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ventas Totales", f"${total_ventas_hoy:.2f}" if total_ventas_hoy else "$0.00")

with col2:
    st.metric("Transacciones", num_transacciones_hoy)

with col3:
    st.metric("Ticket Promedio", f"${ticket_promedio:.2f}")

st.subheader("Productos Más Vendidos Hoy")
df_mas_vendidos = get_productos_mas_vendidos(db, dia_actual)
if not df_mas_vendidos.empty:
    st.table(df_mas_vendidos)
else:
    st.info("Aún no hay ventas registradas para hoy.")