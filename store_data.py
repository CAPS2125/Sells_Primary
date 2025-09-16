# store_data.py
import os
import streamlit as st

@st.cache_resource
def get_db_path():
    # Crea la carpeta "data" si no existe
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Define la ruta absoluta de la base de datos dentro de la carpeta "data"
    db_path = os.path.join(data_dir, "tienda_escolar.db")
    return db_path

db_path = get_db_path()
st.write(f"Ruta de la base de datos: {db_path}")
