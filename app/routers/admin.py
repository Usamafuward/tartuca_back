from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
from .auth import get_current_user
from sqlalchemy import func

router = APIRouter(
    prefix="/api/dashboard",
    tags=["admin"]
)

@router.get("/stats")
def read_dashboard_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    
    # Revenue (sum of total_amount of non-cancelled orders)
    revenue = db.query(func.sum(models.Order.total_amount)).filter(models.Order.status != 'cancelled').scalar() or 0
    
    # Orders count
    orders_count = db.query(models.Order).count()
    
    # New Customers (simple count for now)
    new_customers = db.query(models.User).filter(models.User.role == 'customer').count()

    # Average Order Value
    avg_order_value = 0
    if orders_count > 0:
        avg_order_value = revenue / orders_count

    return {
        "revenue": revenue,
        "orders_count": orders_count,
        "new_customers": new_customers,
        "avg_order_value": round(avg_order_value, 2)
    }
