from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, Payment, User
from app.services.auth import get_current_user
from app.config import settings
import stripe

router = APIRouter(prefix="/payments", tags=["payments"])

# Configurar Stripe
stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout-session")
def create_checkout_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una sesión de pago de Stripe con los items del carrito"""
    
    # Obtener carrito del usuario
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrito no encontrado"
        )
    
    # Obtener items del carrito con sus productos
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El carrito está vacío"
        )
    
    # Calcular total y preparar line_items para Stripe
    line_items = []
    total_amount = 0
    
    for item in cart_items:
        product = item.product
        total_amount += product.price * item.quantity
        
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product.name,
                    "description": product.description or "",
                },
                "unit_amount": product.price,  # Precio en centavos
            },
            "quantity": item.quantity,
        })
    
    try:
        # Crear sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{settings.frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/cancel",
            customer_email=current_user.email,
            metadata={
                "user_id": current_user.id,
                "cart_id": cart.id
            }
        )
        
        # Guardar registro de pago
        payment = Payment(
            user_id=current_user.id,
            amount=total_amount,
            status="pending",
            stripe_session_id=session.id
        )
        db.add(payment)
        db.commit()
        
        return JSONResponse({
            "id": session.id,
            "url": session.url
        })
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de Stripe: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear sesión de pago: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook para recibir eventos de Stripe"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Manejar el evento
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Actualizar estado del pago
        payment = db.query(Payment).filter(
            Payment.stripe_session_id == session["id"]
        ).first()
        
        if payment:
            payment.status = "completed"
            db.commit()
            
            # Vaciar carrito del usuario
            cart = db.query(Cart).filter(Cart.id == session["metadata"]["cart_id"]).first()
            if cart:
                db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
                db.commit()
    
    return {"status": "success"}


@router.get("/history")
def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de pagos del usuario"""
    
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return payments