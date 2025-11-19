from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, Product, User
from app.schemas import ProductSchema
from app.services.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

# 🛒 Obtener el carrito del usuario
@router.get("/", response_model=list[ProductSchema])
def get_cart_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return []

    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    return [item.product for item in items]

# ➕ Agregar producto al carrito
@router.post("/add/{product_id}")
def add_to_cart(product_id: int, quantity: int = 1, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    return {"message": "Producto agregado al carrito"}

# 🔄 Actualizar cantidad
@router.put("/update/{product_id}")
def update_cart_item(product_id: int, quantity: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no está en el carrito")

    item.quantity = quantity
    db.commit()
    return {"message": "Cantidad actualizada"}

# ❌ Eliminar producto del carrito
@router.delete("/remove/{product_id}")
def remove_cart_item(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Producto no está en el carrito")

    db.delete(item)
    db.commit()
    return {"message": "Producto eliminado del carrito"}
