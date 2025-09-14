import streamlit as st
from db import SessionLocal, Ventas, DetalleVenta, Productos, Inventario, create_tables
from sqlalchemy.orm import joinedload
from datetime import datetime

st.set_page_config(
    page_title="Ventas",
    page_icon="💰",
    layout="wide"
)

st.title("Registro de Ventas 💰")
st.markdown("Agrega productos al carrito y finaliza la venta rápidamente.")

# Función para la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Conexión a la base de datos
db = next(get_db())

# Inicializar el carrito de compras en la sesión de Streamlit
if 'carrito' not in st.session_state:
    st.session_state.carrito = {}

# --- Funciones de venta ---
def get_productos_disponibles(db):
    # Obtiene todos los productos con su cantidad en inventario
    productos = db.query(Productos).options(joinedload(Productos.inventario)).all()
    # Filtra solo los que tienen stock
    return [p for p in productos if p.inventario and p.inventario[0].cantidad > 0]

def add_to_carrito(producto_id, cantidad):
    if producto_id in st.session_state.carrito:
        st.session_state.carrito[producto_id]['cantidad'] += cantidad
    else:
        producto = db.query(Productos).filter(Productos.id_producto == producto_id).first()
        st.session_state.carrito[producto_id] = {
            'nombre': producto.nombre,
            'precio_venta': float(producto.precio_venta),
            'cantidad': cantidad
        }
    st.success(f"{cantidad} x {st.session_state.carrito[producto_id]['nombre']} agregado(s) al carrito.")

def remove_from_carrito(producto_id):
    if producto_id in st.session_state.carrito:
        del st.session_state.carrito[producto_id]
        st.success("Producto eliminado del carrito.")
    else:
        st.warning("El producto no está en el carrito.")

def finalizar_venta(db):
    if not st.session_state.carrito:
        st.error("El carrito está vacío. Agrega productos para finalizar la venta.")
        return

    # Iniciar la transacción de la venta
    try:
        total_venta = sum(item['precio_venta'] * item['cantidad'] for item in st.session_state.carrito.values())
        nueva_venta = Ventas(total_venta=total_venta)
        db.add(nueva_venta)
        db.flush()  # Obtener el id_venta antes de commitear

        for producto_id, item in st.session_state.carrito.items():
            # Crear el detalle de la venta
            detalle = DetalleVenta(
                id_venta=nueva_venta.id_venta,
                id_producto=producto_id,
                cantidad=item['cantidad'],
                precio_unitario=item['precio_venta']
            )
            db.add(detalle)

            # Actualizar el inventario
            inventario_item = db.query(Inventario).filter(Inventario.id_producto == producto_id).first()
            if inventario_item:
                inventario_item.cantidad -= item['cantidad']
            
        db.commit()
        st.success(f"Venta finalizada exitosamente. Total: ${total_venta:.2f}")
        
        # Limpiar el carrito después de la venta
        st.session_state.carrito = {}

    except Exception as e:
        db.rollback()
        st.error(f"Ocurrió un error al procesar la venta: {e}")

# --- Interfaz de la aplicación ---
col_productos, col_carrito = st.columns([2, 1])

# Sección de productos
with col_productos:
    st.subheader("Productos Disponibles")
    productos = get_productos_disponibles(db)
    
    if productos:
        for producto in productos:
            inventario = producto.inventario
            with st.container():
                st.write(f"**{producto.nombre}** - ${producto.precio_venta:.2f}")
                st.write(f"Stock: {inventario.cantidad}")
                col1, col2 = st.columns([1, 10])
                with col1:
                    cantidad_a_agregar = st.number_input(
                        f"Cantidad_{producto.id_producto}", 
                        min_value=1, 
                        max_value=inventario.cantidad, 
                        value=1, 
                        label_visibility="collapsed"
                    )
                with col2:
                    if st.button("Agregar al Carrito", key=f"add_{producto.id_producto}"):
                        add_to_carrito(producto.id_producto, cantidad_a_agregar)
                st.markdown("---")
    else:
        st.warning("No hay productos en stock para vender.")

# Sección del carrito de compras
with col_carrito:
    st.subheader("Carrito de Compras")
    if st.session_state.carrito:
        total_carrito = 0
        for producto_id, item in st.session_state.carrito.items():
            total_producto = item['precio_venta'] * item['cantidad']
            total_carrito += total_producto
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{item['nombre']} x {item['cantidad']} = ${total_producto:.2f}")
            with col2:
                if st.button("X", key=f"remove_{producto_id}"):
                    remove_from_carrito(producto_id)
                    st.experimental_rerun()
        
        st.markdown("---")
        st.subheader(f"Total: ${total_carrito:.2f}")
        
        if st.button("Finalizar Venta"):
            finalizar_venta(db)
            st.experimental_rerun()
    else:
        st.info("El carrito está vacío.")
