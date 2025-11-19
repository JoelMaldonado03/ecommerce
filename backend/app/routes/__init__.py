from fastapi import APIRouter
from .auth import router as auth_router
from .product import router as product_router
from .payment import router as payment_router
from .cart import router as cart_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(product_router)
router.include_router(payment_router)
router.include_router(cart_router)
