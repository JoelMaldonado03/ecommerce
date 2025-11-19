import io 
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from collections import Counter
from app.database import get_db
from app.models import Product

router = APIRouter()

def generar_grafico(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/grafico-barras")
def grafico_barras(db: Session = Depends(get_db)):
    categorias = db.query(Product.category).all()
    # contar productos por categoría
    conteo = {}
    for c in categorias:
        conteo[c[0]] = conteo.get(c[0], 0) + 1

    fig, ax = plt.subplots()
    ax.bar(conteo.keys(), conteo.values())

    # ✅ Forzar que el eje Y muestre solo enteros
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.title("Cantidad de productos por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Cantidad")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/grafico-torta")
def grafico_torta(db: Session = Depends(get_db)):
    # Contar productos por categoría
    categorias = db.query(Product.category).all()
    conteo = {}
    for c in categorias:
        conteo[c[0]] = conteo.get(c[0], 0) + 1

    # Crear gráfico de torta mostrando cantidades
    fig, ax = plt.subplots()
    ax.pie(
        conteo.values(),
        labels=conteo.keys(),
        autopct=lambda p: f"{int(round(p * sum(conteo.values()) / 100))} productos"
    )

    plt.title("Distribución de productos por categoría")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

