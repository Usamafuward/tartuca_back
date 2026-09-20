from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user, get_current_user_optional

router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"]
)

@router.post("", response_model=schemas.Reservation)
@router.post("/", response_model=schemas.Reservation, include_in_schema=False)
def create_reservation(
    reservation: schemas.ReservationCreate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    return crud.create_reservation(db, reservation, user_id=user_id)

@router.get("/my-reservations", response_model=List[schemas.Reservation])
def read_my_reservations(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_reservations(db, user_id=current_user.id, email=current_user.email)

@router.get("", response_model=List[schemas.Reservation])
@router.get("/", response_model=List[schemas.Reservation], include_in_schema=False)
def read_reservations(db: Session = Depends(database.get_db)):
    return crud.get_reservations(db)

@router.patch("/{res_id}/status", response_model=schemas.Reservation)
def update_reservation_status(res_id: int, status_update: schemas.ReservationStatusUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    db_res = crud.update_reservation_status(db, res_id, status_update.status)
    if db_res is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_res

