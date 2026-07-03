from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from .. import crud, schemas, database, models
from .auth import get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/api/special-offers",
    tags=["special_offers"]
)

@router.get("/", response_model=List[schemas.SpecialOffer])
def read_special_offers(db: Session = Depends(database.get_db)):
    return crud.get_special_offers(db)

@router.get("/{offer_id}/image")
def read_special_offer_image(offer_id: int, db: Session = Depends(database.get_db)):
    db_offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if db_offer.image_data:
        return Response(content=db_offer.image_data, media_type="image/jpeg")
    
    if db_offer.image_url:
        return RedirectResponse(url=db_offer.image_url)
        
    raise HTTPException(status_code=404, detail="Image not found")

@router.post("/", response_model=schemas.SpecialOffer)
def create_special_offer(
    title: str = Form(...),
    price: Decimal = Form(...),
    description: Optional[str] = Form(None),
    badge_text: Optional[str] = Form(None),
    badge_color: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    image_data = None
    if image:
        image_data = image.file.read()

    offer = schemas.SpecialOfferCreate(
        title=title,
        price=price,
        description=description,
        badge_text=badge_text,
        badge_color=badge_color,
        image_url=image_url,
        is_active=is_active
    )
    return crud.create_special_offer(db, offer, image_data)

@router.delete("/{offer_id}")
def delete_special_offer(offer_id: int, db: Session = Depends(database.get_db)):
    # if current_user.role != "admin":
    #      raise HTTPException(status_code=403, detail="Not authorized")
    success = crud.delete_special_offer(db, offer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found")
    return {"message": "Deleted"}

@router.put("/{offer_id}", response_model=schemas.SpecialOffer)
def update_special_offer(
    offer_id: int, 
    title: Optional[str] = Form(None),
    price: Optional[Decimal] = Form(None),
    description: Optional[str] = Form(None),
    badge_text: Optional[str] = Form(None),
    badge_color: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    image_data = None
    if image:
        image_data = image.file.read()
    
    # Create update data with only provided fields
    update_fields = {}
    if title is not None:
        update_fields["title"] = title
    if price is not None:
        update_fields["price"] = price
    if description is not None:
        update_fields["description"] = description
    if badge_text is not None:
        update_fields["badge_text"] = badge_text
    if badge_color is not None:
        update_fields["badge_color"] = badge_color
    if image_url is not None:
        update_fields["image_url"] = image_url
    if is_active is not None:
        update_fields["is_active"] = is_active
        
    offer = schemas.SpecialOfferUpdate(**update_fields)
    
    db_offer = crud.update_special_offer(db, offer_id, offer, image_data)
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return db_offer

