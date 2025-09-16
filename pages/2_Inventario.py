import streamlit as st
from db import SessionLocal, Ventas, DetalleVenta, Productos, Inventario
from sqlalchemy.orm import joinedload
from datetime import datetime

st.set_page_config(
    page_title="Inventario",
    page_icon="📦",
    layout="wide"
)

st.title("Gestión de Inventario 📦")

# Función para la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Funciones CRUD ---
def get_productos(db):
    return db.query(Productos).options(joinedload(Productos.inventario)).all()

# pages/2_Inventario.py

def add_producto(db, nombre, descripcion, precio_compra, precio_venta, cantidad):
    nuevo_producto = Productos(
        nombre=nombre,
        descripcion=descripcion,
        precio_compra=precio_compra,
        precio_venta=precio_venta
    )
    db.add(nuevo_producto)
    # En lugar de commit, usa flush para obtener el ID sin guardar en la DB
    db.flush()

    nuevo_inventario = Inventario(
        id_producto=nuevo_producto.id_producto,
        cantidad=cantidad,
        producto=nuevo_producto # Agrega esta línea para establecer la relación
    )
    db.add(nuevo_inventario)
    db.commit() # Un solo commit para ambas transacciones

def update_producto(db, id_producto, nombre, descripcion, precio_compra, precio_venta):
    producto = db.query(Productos).filter(Productos.id_producto == id_producto).first()
    if producto:
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio_compra = precio_compra
        producto.precio_venta = precio_venta
        db.commit()
        return True
    return False

def update_inventario(db, id_producto, cantidad):
    inventario = db.query(Inventario).filter(Inventario.id_producto == id_producto).first()
    if inventario:
        inventario.cantidad = cantidad
        db.commit()
        return True
    return False

def delete_producto(db, id_producto):
    producto = db.query(Productos).filter(Productos.id_producto == id_producto).first()
    if producto:
        # Eliminar el inventario asociado primero
        db.query(Inventario).filter(Inventario.id_producto == id_producto).delete()
        db.delete(producto)
        db.commit()
        return True
    return False
# --- Fin de funciones CRUD ---

# Conexión a la base de datos
db = next(get_db())

# Menú de acciones
accion = st.radio("Selecciona una acción:", ("Ver Inventario", "Agregar Producto", "Editar Producto", "Eliminar Producto"))

if accion == "Ver Inventario":
    st.subheader("Inventario Actual")
    productos = get_productos(db)
    if productos:
        data = []
        for p in productos:
            inventario = p.inventario if p.inventario else None
            cantidad = inventario.cantidad if inventario else 0
            data.append({
                'ID': p.id_producto,
                'Producto': p.nombre,
                'Stock': cantidad,
                'Precio de Venta': f'${p.precio_venta}',
                'Descripción': p.descripcion
            })
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No hay productos en el inventario.")
    
elif accion == "Agregar Producto":
    st.subheader("Agregar Nuevo Producto")
    with st.form("form_agregar_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del Producto")
        descripcion = st.text_area("Descripción")
        col1, col2, col3 = st.columns(3)
        with col1:
            precio_compra = st.number_input("Precio de Compra", min_value=0.01, format="%.2f")
        with col2:
            precio_venta = st.number_input("Precio de Venta", min_value=0.01, format="%.2f")
        with col3:
            cantidad = st.number_input("Cantidad Inicial", min_value=0, step=1)
        
        submitted = st.form_submit_button("Agregar Producto")
        if submitted:
            if nombre and precio_compra > 0 and precio_venta > 0:
                add_producto(db, nombre, descripcion, precio_compra, precio_venta, cantidad)
                st.success(f"Producto '{nombre}' agregado exitosamente.")
            else:
                st.error("Por favor, completa todos los campos requeridos.")

elif accion == "Editar Producto":
    st.subheader("Editar un Producto Existente")
    productos = db.query(Productos).all()
    if not productos:
        st.warning("No hay productos para editar.")
    else:
        producto_seleccionado = st.selectbox(
            "Selecciona el producto a editar:",
            options=[p.id_producto for p in productos],
            format_func=lambda x: db.query(Productos).filter(Productos.id_producto == x).first().nombre
        )
        if producto_seleccionado:
            producto = db.query(Productos).filter(Productos.id_producto == producto_seleccionado).first()
            inventario = db.query(Inventario).filter(Inventario.id_producto == producto_seleccionado).first()
            
            with st.form("form_editar_producto", clear_on_submit=False):
                nombre_edit = st.text_input("Nombre del Producto", value=producto.nombre)
                descripcion_edit = st.text_area("Descripción", value=producto.descripcion)
                col1, col2 = st.columns(2)
                with col1:
                    precio_compra_edit = st.number_input("Precio de Compra", value=float(producto.precio_compra), min_value=0.01, format="%.2f")
                with col2:
                    precio_venta_edit = st.number_input("Precio de Venta", value=float(producto.precio_venta), min_value=0.01, format="%.2f")
                cantidad_edit = st.number_input("Cantidad en Stock", value=inventario.cantidad, min_value=0, step=1)

                submitted_edit = st.form_submit_button("Actualizar Producto")
                if submitted_edit:
                    update_producto(db, producto.id_producto, nombre_edit, descripcion_edit, precio_compra_edit, precio_venta_edit)
                    update_inventario(db, producto.id_producto, cantidad_edit)
                    st.success(f"Producto '{nombre_edit}' actualizado exitosamente.")
                    st.experimental_rerun()

elif accion == "Eliminar Producto":
    st.subheader("Eliminar un Producto")
    productos = db.query(Productos).all()
    if not productos:
        st.warning("No hay productos para eliminar.")
    else:
        producto_a_eliminar = st.selectbox(
            "Selecciona el producto a eliminar:",
            options=[p.id_producto for p in productos],
            format_func=lambda x: db.query(Productos).filter(Productos.id_producto == x).first().nombre
        )
        if st.button("Eliminar Producto", help="Esta acción es irreversible."):
            if delete_producto(db, producto_a_eliminar):
                st.success("Producto eliminado exitosamente.")
                st.experimental_rerun()
            else:
                st.error("No se pudo eliminar el producto.")
