from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.schemas import ProductSchema, ProductCreate
import pandas as pd
import io, os, asyncio

router = APIRouter()
active_connections = {}

@router.websocket("/ws/excel")
async def excel_ws(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)
    active_connections[client_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del active_connections[client_id]

# Función para emitir mensajes a todos los clientes conectados
def notify_clients(message: str):
    for ws in active_connections.values():
        try:
            asyncio.create_task(ws.send_text(message))
        except Exception:
            pass

# Endpoint para subir y procesar Excel
@router.post("/upload-products-excel")
async def upload_products_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    notify_clients(" Carga iniciada")

    if not file.filename.endswith(".xlsx"):
        notify_clients(" Archivo no válido")
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        notify_clients(" Error al leer el Excel")
        raise HTTPException(status_code=400, detail=f"Error al leer el Excel: {str(e)}")

    required_columns = {"name", "description", "price", "category", "image_filename"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        notify_clients(f" Faltan columnas: {missing}")
        raise HTTPException(status_code=400, detail=f"Faltan columnas requeridas: {missing}")

    os.makedirs("static/images", exist_ok=True)

    products = []
    for i, row in df.iterrows():
        try:
            name = str(row["name"]).strip()
            if not name:
                raise ValueError("El nombre del producto no puede estar vacío")

            if db.query(Product).filter_by(name=name).first():
                raise ValueError(f"Ya existe un producto con el nombre '{name}'")

            product = Product(
                name=name,
                description=str(row.get("description", "")).strip(),
                price=int(row["price"]),
                category=str(row.get("category", "")).strip(),
                image_filename=str(row.get("image_filename", "")).strip()
            )
            products.append(product)
            notify_clients(f" Fila {i + 2}: {product.name} preparada")
        except Exception as e:
            notify_clients(f" Error en fila {i + 2}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error en fila {i + 2}: {str(e)}")

    db.add_all(products)
    db.commit()
    notify_clients(f" Se insertaron {len(products)} productos")

    return {"message": f"{len(products)} productos cargados exitosamente"}

# Obtener todos los productos
@router.get("/", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    productos = db.query(Product).all()
    print(f"✅ get_products() fue llamado. Se encontraron {len(productos)} productos.")
    return productos

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Eliminar producto por ID
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    nombre = producto.name
    db.delete(producto)
    db.commit()

    notify_clients(f" Producto eliminado: {nombre}")

    return {"message": "Producto eliminado"}

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, updated_data: ProductCreate, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.name = updated_data.name
    producto.description = updated_data.description
    producto.price = updated_data.price
    producto.category = updated_data.category
    producto.image_filename = updated_data.image_filename

    db.commit()
    db.refresh(producto)

    notify_clients(f" Producto actualizado: {producto.name}")

    return producto