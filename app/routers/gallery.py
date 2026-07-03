from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas, database, models
from .auth import get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/api/gallery",
    tags=["gallery"]
)

@router.get("/", response_model=List[schemas.GalleryImage])
def read_gallery(db: Session = Depends(database.get_db)):
    return crud.get_gallery_images(db)

@router.get("/{img_id}/image")
def read_gallery_image(img_id: int, db: Session = Depends(database.get_db)):
    db_img = db.query(models.GalleryImage).filter(models.GalleryImage.id == img_id).first()
    if not db_img:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if db_img.image_data:
        return Response(content=db_img.image_data, media_type="image/jpeg")
    
    if db_img.image_url:
        return RedirectResponse(url=db_img.image_url)
        
    raise HTTPException(status_code=404, detail="Image not found")

@router.post("/", response_model=schemas.GalleryImage)
def create_gallery_image(
    category: str = Form(...),
    alt_text: str = Form(...),
    image_url: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    image_data = None
    if image:
        image_data = image.file.read()
    
    img = schemas.GalleryImageCreate(
        category=category,
        alt_text=alt_text,
        image_url=image_url
    )
    return crud.create_gallery_image(db, img, image_data)

@router.delete("/{img_id}")
def delete_gallery_image(img_id: int, db: Session = Depends(database.get_db)):
    # if current_user.role != "admin":
    #      raise HTTPException(status_code=403, detail="Not authorized")
    success = crud.delete_gallery_image(db, img_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Deleted"}
