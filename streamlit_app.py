import streamlit as st
from db import create_tables
# Esta función se ejecutará solo una vez al iniciar la aplicación.
# Streamlit maneja la ejecución de los scripts de las páginas de forma separada
# pero el script principal solo se ejecuta una vez al iniciar.
create_tables()

st.set_page_config(
    page_title="Tienda Escolar",
    page_icon="🍎",
    layout="wide"
)

st.title("Sistema de Gestión para la Tienda Escolar 🏫")
st.markdown("Bienvenido al sistema de control de tu tienda de snacks saludables. Usa el menú de la izquierda para navegar por las diferentes secciones.")
# La navegación se maneja automáticamente por Streamlit al colocar los archivos en la carpeta 'pages'.
