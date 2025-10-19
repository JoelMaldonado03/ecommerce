from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.services.auth import authenticate_user, create_access_token, get_current_user
from app.schemas import ProductSchema
from app.models import Product
from app.database import SessionLocal

router = APIRouter()
db = SessionLocal()

@router.post("/products")
def create_product(product: ProductSchema):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/perfil")
def perfil(email: str = Depends(get_current_user)):
    return {"email": email}

@router.get("/products")
def list_products():
    return db.query(Product).all()
