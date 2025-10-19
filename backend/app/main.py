from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.product import router as product_router
from app.routes.cart import router as cart_router
from app.routes.payment import router as payment_router
from app.config import settings


# Crea la instancia de FastAPI
app = FastAPI(debug=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Monta archivos estáticos si usas frontend integrado
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Rutas
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(payment_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoints básicos
@app.get("/")
def read_root():
    return {"message": "Bienvenido al e-commerce con FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}
