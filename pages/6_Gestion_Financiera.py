import streamlit as st
from db import SessionLocal, Ventas, Gastos
from sqlalchemy import func
from datetime import date, timedelta
import pandas as pd
import os

st.set_page_config(
    page_title="Gestión Financiera",
    page_icon="💸",
    layout="wide"
)

st.title("Gestión Financiera 💸")
st.markdown("Registra y analiza tus gastos para una visión completa del flujo de caja.")

# Función para la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

# --- 1. Sección de Gastos ---
st.subheader("Registrar Nuevo Gasto")
opciones_gastos = ["Renta Diaria", "Salario", "Inventario", "Gasolina", "Otro"]
with st.form("form_gasto", clear_on_submit=True):
    tipo_gasto = st.selectbox("Tipo de Gasto", opciones_gastos)
    monto = st.number_input("Monto", min_value=0.01, format="%.2f")
    
    # Si el tipo de gasto es "Otro", permite al usuario escribir la descripción
    if tipo_gasto == "Otro":
        descripcion = st.text_input("Descripción del Gasto")
    else:
        descripcion = tipo_gasto
        
    submitted = st.form_submit_button("Registrar Gasto")
    if submitted:
        if descripcion and monto > 0:
            nuevo_gasto = Gastos(descripcion=descripcion, monto=monto)
            db.add(nuevo_gasto)
            db.commit()
            st.success(f"Gasto '{descripcion}' de ${monto:.2f} registrado exitosamente.")
        else:
            st.error("Por favor, completa todos los campos.")

st.markdown("---")

# --- 2. Sección de Cuenta de Efectivo ---
st.subheader("Cuenta de Efectivo")

# Archivo para guardar el efectivo acumulado
efectivo_file = "efectivo_acumulado.txt"
if not os.path.exists(efectivo_file):
    with open(efectivo_file, "w") as f:
        f.write("0.00")

with open(efectivo_file, "r") as f:
    efectivo_acumulado = float(f.read())

# Obtener ventas y gastos del día anterior para calcular la ganancia neta diaria
ayer = date.today() - timedelta(days=1)
ventas_ayer = db.query(func.sum(Ventas.total_venta)).filter(func.date(Ventas.fecha_venta) == ayer).scalar() or 0
gastos_ayer = db.query(func.sum(Gastos.monto)).filter(func.date(Gastos.fecha_gasto) == ayer).scalar() or 0
ganancia_neta_ayer = ventas_ayer - gastos_ayer

# Actualizar el efectivo acumulado
efectivo_acumulado += ganancia_neta_ayer
with open(efectivo_file, "w") as f:
    f.write(f"{efectivo_acumulado:.2f}")

col_efectivo, col_retirar = st.columns(2)
with col_efectivo:
    st.metric("Efectivo Acumulado", f"${efectivo_acumulado:.2f}")

with col_retirar:
    st.markdown("#### Retirar Efectivo")
    monto_a_retirar = st.number_input("¿Cuánto desea retirar?", min_value=0.00, max_value=efectivo_acumulado, format="%.2f")
    if st.button("Retirar Monto"):
        if monto_a_retirar > 0 and monto_a_retirar <= efectivo_acumulado:
            efectivo_acumulado -= monto_a_retirar
            with open(efectivo_file, "w") as f:
                f.write(f"{efectivo_acumulado:.2f}")
            st.success(f"Se ha retirado ${monto_a_retirar:.2f}. Nuevo efectivo acumulado: ${efectivo_acumulado:.2f}")
            st.experimental_rerun()
        else:
            st.warning("Ingrese un monto válido para retirar.")

st.markdown("---")

# --- 3. Sección de Análisis Financiero ---
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

# ... (resto de la sección de análisis financiero, incluyendo el gráfico de barras) ...
