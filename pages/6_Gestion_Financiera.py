import streamlit as st
from bd import SessionLocal, Ventas, Gastos
from sqlalchemy import func
from datetime import date, timedelta
import pandas as pd

st.set_page_config(
    page_title="Gestión Financiera",
    page_icon="💸",
    layout="wide"
)

st.title("Gestión Financiera 💸")
st.markdown("Registra y analiza tus gastos para una visión completa del flujo de caja.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

# Sección para registrar un nuevo gasto
st.subheader("Registrar Nuevo Gasto")
with st.form("form_gasto", clear_on_submit=True):
    descripcion = st.text_input("Descripción del Gasto")
    monto = st.number_input("Monto", min_value=0.01, format="%.2f")
    submitted = st.form_submit_button("Registrar Gasto")
    if submitted:
        if descripcion and monto > 0:
            nuevo_gasto = Gastos(descripcion=descripcion, monto=monto)
            db.add(nuevo_gasto)
            db.commit()
            st.success("Gasto registrado exitosamente.")
        else:
            st.error("Por favor, completa todos los campos.")

st.markdown("---")

# Sección de análisis financiero
st.subheader("Análisis de Flujo de Caja")
start_date = st.date_input("Fecha de Inicio del Análisis", date.today() - timedelta(days=30))
end_date = st.date_input("Fecha de Fin del Análisis", date.today())

ventas_totales = db.query(func.sum(Ventas.total_venta)).filter(Ventas.fecha_venta >= start_date, Ventas.fecha_venta <= end_date).scalar() or 0
gastos_totales = db.query(func.sum(Gastos.monto)).filter(Gastos.fecha_gasto >= start_date, Gastos.fecha_gasto <= end_date).scalar() or 0
ganancia_neta = ventas_totales - gastos_totales

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas Totales", f"${ventas_totales:.2f}")
with col2:
    st.metric("Gastos Totales", f"${gastos_totales:.2f}")
with col3:
    st.metric("Ganancia Neta", f"${ganancia_neta:.2f}")

st.markdown("---")

# Visualización con gráfico
st.subheader("Distribución de Ingresos y Gastos")
datos_flujo = pd.DataFrame({
    'Tipo': ['Ventas', 'Gastos'],
    'Monto': [ventas_totales, gastos_totales]
})

# Ajustar los valores para el gráfico de barras si son negativos
datos_flujo['Monto'] = datos_flujo['Monto'].abs()

st.bar_chart(datos_flujo, x='Tipo', y='Monto')

st.write("Esta gráfica te ayuda a visualizar la relación entre tus ventas y tus gastos en el periodo seleccionado.")
