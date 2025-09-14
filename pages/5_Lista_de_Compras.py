import streamlit as st
from bd import SessionLocal, Productos, Inventario
from sqlalchemy.orm import joinedload

st.set_page_config(
    page_title="Lista de Compras",
    page_icon="🛒",
    layout="wide"
)

st.title("Lista de Compras 🛒")
st.markdown("Reabastece tu inventario para evitar quedarte sin productos populares.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

# Muestra el inventario con una columna de alerta
st.subheader("Inventario para Reabastecer")
productos = db.query(Productos).options(joinedload(Productos.inventario)).all()

# Opcional: Permitir al usuario definir un umbral de stock bajo
umbral = st.number_input("Establece un umbral de stock bajo:", min_value=1, value=5, step=1)

if productos:
    data = []
    lista_de_compras = []
    
    for p in productos:
        cantidad = p.inventario.cantidad if p.inventario else 0
        alerta = "⚠️ Stock Bajo" if cantidad <= umbral else "✅ Stock Suficiente"
        
        data.append({
            'ID': p.id_producto,
            'Producto': p.nombre,
            'Stock Actual': cantidad,
            'Estado': alerta
        })

        if cantidad <= umbral:
            lista_de_compras.append(p)
    
    st.dataframe(data, use_container_width=True)

    st.markdown("---")

    # Muestra la lista de productos a comprar
    st.subheader("Productos para Comprar")
    if lista_de_compras:
        for producto in lista_de_compras:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{producto.nombre}**")
            with col2:
                cantidad_a_comprar = st.number_input(
                    f"Cantidad a comprar para {producto.nombre}", 
                    min_value=1, 
                    value=10, 
                    step=1, 
                    key=f"compra_{producto.id_producto}"
                )
                if st.button("Comprar y Actualizar Stock", key=f"actualizar_{producto.id_producto}"):
                    inventario = db.query(Inventario).filter(Inventario.id_producto == producto.id_producto).first()
                    if inventario:
                        inventario.cantidad += cantidad_a_comprar
                        db.commit()
                        st.success(f"Stock de {producto.nombre} actualizado. Cantidad total: {inventario.cantidad}")
                        st.experimental_rerun()
                    else:
                        st.error("Error al actualizar el inventario.")
    else:
        st.info("¡No hay productos con stock bajo en este momento!")
