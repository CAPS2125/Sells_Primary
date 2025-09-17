import streamlit as st
import pandas as pd
from db import SessionLocal, Productos, Inventario, Ventas, DetalleVenta, Gastos
from sqlalchemy.orm import sessionmaker
import zipfile
import io
import os

st.set_page_config(
    page_title="Gestión de Datos",
    page_icon="💾",
    layout="wide"
)

st.title("Gestión de Datos 💾")
st.markdown("Exporta e importa todas tus tablas para mantener un respaldo de tus datos.")

# Un diccionario para mapear los nombres de las tablas a sus clases de SQLAlchemy
TABLAS = {
    "productos": Productos,
    "inventario": Inventario,
    "ventas": Ventas,
    "detalle_venta": DetalleVenta,
    "gastos": Gastos
}

# --- Exportar Datos ---
st.header("Exportar Tablas a CSV")
st.markdown("Descarga todas tus tablas en archivos CSV separados.")

def export_all_tables_to_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        db = SessionLocal()
        try:
            for table_name, table_class in TABLAS.items():
                data = db.query(table_class).all()
                df = pd.DataFrame([vars(d) for d in data])
                
                if not df.empty:
                    # Limpiar columnas internas de SQLAlchemy
                    if '_sa_instance_state' in df.columns:
                        df = df.drop(columns=['_sa_instance_state'])
                    
                    # Escribir el DataFrame al buffer del zip
                    csv_string = df.to_csv(index=False).encode('utf-8')
                    zip_file.writestr(f"{table_name}.csv", csv_string)
        finally:
            db.close()

    zip_buffer.seek(0)
    return zip_buffer

# Botón de descarga para el archivo ZIP
zip_file = export_all_tables_to_zip()
if zip_file:
    st.download_button(
        label="Descargar Todas las Tablas (ZIP)",
        data=zip_file,
        file_name="tablas_tienda_escolar.zip",
        mime="application/zip"
    )
else:
    st.warning("No hay datos para exportar.")

# --- Importar Datos ---
st.header("Importar Datos desde CSV")
st.markdown("Carga archivos CSV para repoblar tus tablas. **¡Esto sobrescribirá los datos existentes!**")

uploaded_files = st.file_uploader(
    "Sube un archivo ZIP",
    type=["zip"],
    accept_multiple_files=False
)

if uploaded_files is not None:
    zip_buffer = uploaded_files.getvalue()
    zip_file = zipfile.ZipFile(io.BytesIO(zip_buffer), "r")
    
    st.info("Descomprimiendo archivos...")
    
    uploaded_dfs = {}
    
    for filename in zip_file.namelist():
        with zip_file.open(filename) as file:
            # Revisa si el archivo no está vacío
            if file.seek(0, os.SEEK_END) > 0:
                file.seek(0) # Regresa al inicio del archivo
                try:
                    df = pd.read_csv(file)
                    table_name = filename.replace(".csv", "")
                    if table_name in TABLAS:
                        uploaded_dfs[table_name] = df
                except pd.errors.EmptyDataError:
                    st.warning(f"El archivo '{filename}' está vacío y será ignorado.")
    
    st.success("Archivos leídos exitosamente.")
    
    # Botón para confirmar la carga
    if st.button("Guardar Datos en la Base de Datos"):
        db = SessionLocal()
        try:
            import_order = ["productos", "inventario", "ventas", "detalle_venta", "gastos"]

            for table_name in import_order:
                if table_name in uploaded_dfs:
                    st.write(f"Importando tabla: **{table_name}**")
                    df = uploaded_dfs[table_name]
                    
                    # Limpiar la tabla existente
                    db.query(TABLAS[table_name]).delete()
                    
                    for index, row in df.iterrows():
                        instance = TABLAS[table_name]()
                        for col, value in row.items():
                            setattr(instance, col, value)
                        db.add(instance)
            
            db.commit()
            st.success("¡Datos importados y repoblados exitosamente!")
            
        except Exception as e:
            db.rollback()
            st.error(f"Ocurrió un error al importar los datos: {e}")
        finally:
            db.close()
            st.error(f"Ocurrió un error al importar los datos: {e}")
        finally:
            db.close()
