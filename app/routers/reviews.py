from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user

router = APIRouter(
    prefix="/api/reviews",
    tags=["reviews"]
)

@router.get("/", response_model=List[schemas.Review])
def read_reviews(db: Session = Depends(database.get_db)):
    return crud.get_reviews(db, approved_only=True)

@router.post("/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(database.get_db)):
    return crud.create_review(db, review)

@router.get("/admin", response_model=List[schemas.Review])
def read_all_reviews(db: Session = Depends(database.get_db)):
    # if current_user.role != "admin":
    #      raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_reviews(db, approved_only=False)

@router.patch("/{review_id}/approve", response_model=schemas.Review)
def approve_review(review_id: int, approval: schemas.ReviewApprove, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    db_review = crud.approve_review(db, review_id, approval.is_approved)
    if db_review is None:
         raise HTTPException(status_code=404, detail="Review not found")
    return db_review
