import streamlit as st
import pandas as pd
from db import SessionLocal, Productos, Inventario, Ventas, DetalleVenta, Gastos
from sqlalchemy.orm import sessionmaker

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

# Usar un solo botón para exportar todo a un archivo comprimido
# Esto es más eficiente que descargar tabla por tabla
import zipfile
import io

def export_all_tables_to_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        db = SessionLocal()
        try:
            for table_name, table_class in TABLAS.items():
                data = db.query(table_class).all()
                df = pd.DataFrame([vars(d) for d in data])
                # Limpiar columnas internas de SQLAlchemy
                if '_sa_instance_state' in df.columns:
                    df = df.drop(columns=['_sa_instance_state'])
                
                # Escribir el DataFrame al buffer del zip
                df.to_csv(f"{table_name}.csv", index=False)
                zip_file.write(f"{table_name}.csv")

        finally:
            db.close()

    zip_buffer.seek(0)
    return zip_buffer

# Botón de descarga para el archivo ZIP
zip_file = export_all_tables_to_zip()
st.download_button(
    label="Descargar Todas las Tablas (ZIP)",
    data=zip_file,
    file_name="tablas_tienda_escolar.zip",
    mime="application/zip"
)

# --- Importar Datos ---
st.header("Importar Datos desde CSV")
st.markdown("Carga archivos CSV para repoblar tus tablas. **¡Esto sobrescribirá los datos existentes!**")

uploaded_files = st.file_uploader(
    "Sube todos los archivos CSV (.zip)",
    type=["zip"],
    accept_multiple_files=False
)

if uploaded_files is not None:
    # Descomprimir los archivos del ZIP
    zip_buffer = uploaded_files.getvalue()
    zip_file = zipfile.ZipFile(io.BytesIO(zip_buffer), "r")
    
    st.info("Descomprimiendo archivos...")
    
    # Un diccionario para guardar los DataFrames de los archivos subidos
    uploaded_dfs = {}
    for filename in zip_file.namelist():
        with zip_file.open(filename) as file:
            df = pd.read_csv(file)
            table_name = filename.replace(".csv", "")
            if table_name in TABLAS:
                uploaded_dfs[table_name] = df
    
    st.success("Archivos leídos exitosamente.")
    
    # Botón para confirmar la carga
    if st.button("Guardar Datos en la Base de Datos"):
        db = SessionLocal()
        try:
            # Importar en el orden correcto para manejar las dependencias
            # Primero las tablas sin FK, luego las dependientes
            import_order = ["productos", "inventario", "ventas", "detalle_venta", "gastos"]

            for table_name in import_order:
                if table_name in uploaded_dfs:
                    st.write(f"Importando tabla: **{table_name}**")
                    df = uploaded_dfs[table_name]
                    
                    # Limpiar la tabla existente
                    db.query(TABLAS[table_name]).delete()
                    
                    for index, row in df.iterrows():
                        # Crear una nueva instancia de la clase de la tabla
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
