from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user, get_current_user_optional

router = APIRouter(
    prefix="/api/orders",
    tags=["orders"]
)

@router.post("", response_model=schemas.Order)
@router.post("/", response_model=schemas.Order, include_in_schema=False)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user_optional)):
    user_id = current_user.id if current_user else None
    return crud.create_order(db, order, user_id=user_id)

@router.get("/my-orders", response_model=List[schemas.Order])
def read_my_orders(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_user_orders(db, user_id=current_user.id)

@router.get("", response_model=List[schemas.Order])
@router.get("/", response_model=List[schemas.Order], include_in_schema=False)
def read_orders(db: Session = Depends(database.get_db)):
    # if current_user.role != "admin":
    #      raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_orders(db)

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(database.get_db)):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    current_status = db_order.status
    new_status = status_update.status

    valid_statuses = {"pending", "cooking", "delivered", "cancelled"}
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{new_status}'")

    if current_status == new_status:
        return db_order

    if current_status == "cancelled":
        raise HTTPException(status_code=400, detail="Cancelled orders cannot be changed to any status")

    if current_status == "cooking" and new_status == "pending":
        raise HTTPException(status_code=400, detail="Cooking orders cannot be changed back to pending")

    if current_status == "delivered" and new_status in ["pending", "cooking"]:
        raise HTTPException(status_code=400, detail="Delivered orders cannot be changed back to pending or cooking")

    return crud.update_order_status(db, order_id, new_status)
