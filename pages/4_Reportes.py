import streamlit as st
from bd import SessionLocal, Ventas, DetalleVenta, Productos, Inventario, create_tables
from sqlalchemy import func, cast, Date
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="Reportes",
    page_icon="📈",
    layout="wide"
)

st.title("Análisis y Reportes 📈")
st.markdown("Explora el rendimiento de tu negocio con estas visualizaciones.")

# Función para la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

# --- Opciones de filtro de fecha ---
st.sidebar.header("Opciones de Filtro")
today = date.today()
start_date = st.sidebar.date_input("Fecha de Inicio", today - timedelta(days=30))
end_date = st.sidebar.date_input("Fecha de Fin", today)

# Validar que la fecha de inicio no sea mayor a la de fin
if start_date > end_date:
    st.sidebar.error("Error: La fecha de inicio debe ser anterior a la de fin.")

# --- Funciones para obtener los datos de la base de datos ---
def get_reporte_ventas(db, start_date, end_date):
    ventas = db.query(
        cast(Ventas.fecha_venta, Date).label('fecha'),
        func.sum(Ventas.total_venta).label('total_diario')
    ).filter(Ventas.fecha_venta >= start_date, Ventas.fecha_venta <= end_date + timedelta(days=1)
    ).group_by('fecha'
    ).order_by('fecha').all()
    
    df_ventas = pd.DataFrame(ventas, columns=['Fecha', 'Ventas Diarias'])
    df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
    return df_ventas

def get_reporte_productos(db, start_date, end_date):
    productos = db.query(
        Productos.nombre,
        func.sum(DetalleVenta.cantidad).label('cantidad_vendida'),
        func.sum(DetalleVenta.cantidad * (Productos.precio_venta - Productos.precio_compra)).label('ganancia')
    ).join(DetalleVenta, Productos.id_producto == DetalleVenta.id_producto
    ).join(Ventas, DetalleVenta.id_venta == Ventas.id_venta
    ).filter(Ventas.fecha_venta >= start_date, Ventas.fecha_venta <= end_date + timedelta(days=1)
    ).group_by(Productos.nombre
    ).all()

    df_productos = pd.DataFrame(productos, columns=['Producto', 'Cantidad Vendida', 'Ganancia'])
    return df_productos

# --- Ejecución y visualización de datos ---
if start_date <= end_date:
    df_ventas = get_reporte_ventas(db, start_date, end_date)
    df_productos = get_reporte_productos(db, start_date, end_date)

    st.subheader("Métricas Clave del Periodo Seleccionado")
    
    total_ventas = df_ventas['Ventas Diarias'].sum() if not df_ventas.empty else 0
    total_ganancia = df_productos['Ganancia'].sum() if not df_productos.empty else 0
    num_transacciones = db.query(Ventas).filter(Ventas.fecha_venta >= start_date, Ventas.fecha_venta <= end_date + timedelta(days=1)).count()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ventas Totales", f"${total_ventas:.2f}")
    with col2:
        st.metric("Ganancia Neta", f"${total_ganancia:.2f}")
    with col3:
        st.metric("Total de Transacciones", num_transacciones)

    st.markdown("---")
    
    st.subheader("Tendencia de Ventas Diarias")
    if not df_ventas.empty:
        st.line_chart(df_ventas.set_index('Fecha'))
    else:
        st.info("No hay datos de ventas en el periodo seleccionado.")
    
    st.markdown("---")

    st.subheader("Análisis de Producto")
    col_prod_top, col_prod_bottom = st.columns(2)

    with col_prod_top:
        st.write("#### Productos Más Vendidos (por cantidad)")
        df_mas_vendidos = df_productos.sort_values(by='Cantidad Vendida', ascending=False).head(10)
        if not df_mas_vendidos.empty:
            st.bar_chart(df_mas_vendidos.set_index('Producto'))
        else:
            st.info("No hay datos de productos en el periodo seleccionado.")

    with col_prod_bottom:
        st.write("#### Productos Más Rentables (por ganancia)")
        df_mas_rentables = df_productos.sort_values(by='Ganancia', ascending=False).head(10)
        if not df_mas_rentables.empty:
            st.dataframe(df_mas_rentables.style.format({'Ganancia': "${:.2f}"}), use_container_width=True)
        else:
            st.info("No hay datos de productos rentables.")
    
    st.markdown("---")

    st.subheader("Inventario Actual vs. Ventas del Periodo")
    # Obtener el stock actual
    df_inventario = pd.read_sql_query(
        "SELECT T1.nombre as Producto, T2.cantidad as Stock_Actual FROM productos as T1 JOIN inventario as T2 ON T1.id_producto = T2.id_producto",
        db.bind
    )
    # Unir datos de ventas con inventario
    df_comparacion = pd.merge(df_inventario, df_productos[['Producto', 'Cantidad Vendida']], on='Producto', how='left').fillna(0)
    df_comparacion = df_comparacion.sort_values(by='Cantidad Vendida', ascending=False)
    
    st.write("Esta tabla te muestra qué tan rápido se está moviendo tu inventario.")
    st.dataframe(df_comparacion, use_container_width=True)
