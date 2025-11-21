# Implementacion, mejoras en el backend fastApi correccion 
# de superposicion de graficos cada grafico ahora se crea
# con su propia figura se cierra correctamente con plt.close
# evita mezclas o textos superpuestos
# IMPLEMENTACION GRAFICO PRECIO POR PRODUCTOS
# CORRECCION DEL GRAFICO CANTIDAD POR CATEGORIA 

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


# ===============================
#  MODIFICADO: PRECIO POR PRODUCTO
# ===============================
@router.get("/grafico-barras")
def grafico_barras(db: Session = Depends(get_db)):
    # limpiar figuras previas
    plt.clf()
    plt.close('all')

    productos = db.query(Product).all()

    # Crear listas con nombres y precios
    nombres = [p.name for p in productos]
    precios = [p.price for p in productos]

    fig, ax = plt.subplots()

    # Gráfico de barras: precio por producto
    ax.bar(nombres, precios)

    # Mostrar enteros en eje Y (opcional)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.title("Precio por producto")
    plt.xlabel("Producto")
    plt.ylabel("Precio")

    # Rotar etiquetas si son muchas
    plt.xticks(rotation=45, ha="right")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ===============================
#  SIN CAMBIOS: CATEGORÍAS
# ===============================
@router.get("/grafico-torta")
def grafico_torta(db: Session = Depends(get_db)):
    # limpiar figuras previas
    plt.clf()
    plt.close('all')

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
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
