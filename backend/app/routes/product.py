from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductSchema
import pandas as pd
import io
import os
import shutil

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/upload-products-excel")
async def upload_products_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el Excel: {str(e)}")

    required_columns = {"name", "description", "price", "category", "image_filename"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Faltan columnas requeridas: {required_columns - set(df.columns)}")

    image_folder = "static/images"
    os.makedirs(image_folder, exist_ok=True)

    products = []
    for _, row in df.iterrows():
        image_filename = row.get("image_filename")
        image_source_path = os.path.join("backend", "images", image_filename)  # Ajusta si tus imágenes están en otra carpeta
        image_target_path = os.path.join(image_folder, image_filename)

        # Copia la imagen si existe
        if os.path.exists(image_source_path):
            shutil.copy(image_source_path, image_target_path)
        else:
            print(f"⚠️ Imagen no encontrada: {image_source_path}")

        product = Product(
            name=row["name"],
            description=row.get("description", ""),
            price=row["price"],
            category=row.get("category", ""),
            image_filename=image_filename
        )
        products.append(product)

    db.add_all(products)
    db.commit()


    return {"message": f"{len(products)} productos cargados exitosamente"}

@router.get("/", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


