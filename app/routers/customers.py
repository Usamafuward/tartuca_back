from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, database, models
from .auth import get_current_user
from sqlalchemy import func
from typing import Annotated, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"]
)

class CustomerUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@router.get("")
@router.get("/", include_in_schema=False)
def get_all_customers(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin access required.")
    
    # Query all customer users
    customers = db.query(models.User).filter(models.User.role == "customer").order_by(models.User.id.asc()).all()

    # Pre-fetch orders & reservations counts and spend
    results = []
    for c in customers:
        orders = db.query(models.Order).filter(
            (models.Order.user_id == c.id) | (models.Order.customer_email == c.email)
        ).all()

        reservations_count = db.query(models.Reservation).filter(
            (models.Reservation.user_id == c.id) | (models.Reservation.customer_email == c.email)
        ).count()

        non_cancelled_orders = [o for o in orders if o.status != 'cancelled']
        total_spent = sum(float(o.total_amount or 0) for o in non_cancelled_orders)
        
        last_order = None
        if orders:
            sorted_orders = sorted(orders, key=lambda x: x.created_at or 0, reverse=True)
            last_order = sorted_orders[0].created_at.isoformat() if sorted_orders[0].created_at else None

        results.append({
            "id": c.id,
            "full_name": c.full_name,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "role": c.role,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "orders_count": len(orders),
            "completed_orders_count": len(non_cancelled_orders),
            "total_spent": round(total_spent, 2),
            "reservations_count": reservations_count,
            "last_order_date": last_order
        })

    return results

@router.get("/{customer_id}")
def get_customer_details(
    customer_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admin access required.")

    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch orders
    orders_db = db.query(models.Order).filter(
        (models.Order.user_id == customer.id) | (models.Order.customer_email == customer.email)
    ).order_by(models.Order.created_at.desc()).all()

    orders_data = []
    dish_frequency = {}
    for o in orders_db:
        items_data = []
        for it in o.items:
            dish_name = it.menu_item.name if it.menu_item else (it.special_offer.title if it.special_offer else f"Item #{it.menu_item_id or it.special_offer_id}")
            items_data.append({
                "id": it.id,
                "name": dish_name,
                "quantity": it.quantity,
                "unit_price": float(it.unit_price),
                "total_price": float(it.unit_price * it.quantity)
            })
            dish_frequency[dish_name] = dish_frequency.get(dish_name, 0) + it.quantity

        orders_data.append({
            "id": o.id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "status": o.status,
            "total_amount": float(o.total_amount),
            "payment_method": o.payment_method,
            "delivery_address": o.delivery_address,
            "delivery_instructions": o.delivery_instructions,
            "items_count": len(o.items),
            "items": items_data
        })

    # Fetch reservations
    reservations_db = db.query(models.Reservation).filter(
        (models.Reservation.user_id == customer.id) | (models.Reservation.customer_email == customer.email)
    ).order_by(models.Reservation.reservation_date.desc(), models.Reservation.reservation_time.desc()).all()

    reservations_data = []
    for r in reservations_db:
        reservations_data.append({
            "id": r.id,
            "reservation_date": r.reservation_date.isoformat() if r.reservation_date else None,
            "reservation_time": r.reservation_time.strftime("%H:%M") if r.reservation_time else None,
            "party_size": r.party_size,
            "occasion": r.occasion,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    # Fetch reviews
    reviews_db = db.query(models.Review).filter(
        models.Review.author_name.ilike(f"%{customer.full_name}%")
    ).all()

    reviews_data = [{
        "id": rev.id,
        "rating": rev.rating,
        "comment": rev.comment,
        "sentiment": rev.sentiment,
        "is_approved": rev.is_approved,
        "created_at": rev.created_at.isoformat() if rev.created_at else None
    } for rev in reviews_db]

    # Metrics
    valid_orders = [o for o in orders_db if o.status != 'cancelled']
    total_spent = sum(float(o.total_amount or 0) for o in valid_orders)
    avg_order_value = round(total_spent / len(valid_orders), 2) if valid_orders else 0.0

    # Top favorite dishes
    favorite_dishes = sorted(
        [{"dish": k, "count": v} for k, v in dish_frequency.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]

    return {
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "role": customer.role,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        },
        "metrics": {
            "total_orders": len(orders_db),
            "completed_orders": len(valid_orders),
            "total_spent": round(total_spent, 2),
            "avg_order_value": avg_order_value,
            "reservations_count": len(reservations_data),
            "reviews_count": len(reviews_data),
            "favorite_dishes": favorite_dishes
        },
        "orders": orders_data,
        "reservations": reservations_data,
        "reviews": reviews_data
    }

@router.put("/{customer_id}")
def update_customer_info(
    customer_id: int,
    data: CustomerUpdateSchema,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if data.full_name is not None:
        customer.full_name = data.full_name.strip()
    if data.phone is not None:
        customer.phone = data.phone.strip()
    if data.address is not None:
        customer.address = data.address.strip()

    db.commit()
    db.refresh(customer)
    return {
        "id": customer.id,
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address
    }
