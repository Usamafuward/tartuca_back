from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from .. import crud, schemas, database, models
from .auth import get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/api",
    tags=["menu"]
)

@router.get("/categories", response_model=List[schemas.Category])
def read_categories(db: Session = Depends(database.get_db)):
    return crud.get_categories(db)

@router.get("/menu-items", response_model=List[schemas.MenuItem])
def read_menu_items(category_id: int = None, db: Session = Depends(database.get_db)):
    return crud.get_menu_items(db, category_id)

@router.get("/menu-items/{item_id}", response_model=schemas.MenuItem)
def read_menu_item(item_id: int, db: Session = Depends(database.get_db)):
    db_item = crud.get_menu_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.get("/menu-items/{item_id}/image")
def read_menu_item_image(item_id: int, db: Session = Depends(database.get_db)):
    db_item = crud.get_menu_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_item.image_data:
        return Response(content=db_item.image_data, media_type="image/jpeg")
    
    if db_item.image_url:
        return RedirectResponse(url=db_item.image_url)
        
    raise HTTPException(status_code=404, detail="Image not found")

@router.post("/menu-items", response_model=schemas.MenuItem)
def create_menu_item(
    name: str = Form(...),
    price: Decimal = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    is_active: bool = Form(True),
    is_vegetarian: bool = Form(False),
    is_gluten_free: bool = Form(False),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    image_data = None
    if image:
        image_data = image.file.read()
    
    item = schemas.MenuItemCreate(
        name=name,
        price=price,
        category_id=category_id,
        description=description,
        image_url=image_url,
        is_active=is_active,
        is_vegetarian=is_vegetarian,
        is_gluten_free=is_gluten_free
    )
    return crud.create_menu_item(db, item, image_data)

@router.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(database.get_db)):
    # if current_user.role != "admin":
    #      raise HTTPException(status_code=403, detail="Not authorized")
    success = crud.delete_menu_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Deleted"}

@router.put("/menu-items/{item_id}", response_model=schemas.MenuItem)
def update_menu_item(
    item_id: int,
    name: Optional[str] = Form(None),
    price: Optional[Decimal] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_vegetarian: Optional[bool] = Form(None),
    is_gluten_free: Optional[bool] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    image_data = None
    if image:
        image_data = image.file.read()
    
    update_fields = {}
    if name is not None: update_fields['name'] = name
    if price is not None: update_fields['price'] = price
    if category_id is not None: update_fields['category_id'] = category_id
    if description is not None: update_fields['description'] = description
    if image_url is not None: update_fields['image_url'] = image_url
    if is_active is not None: update_fields['is_active'] = is_active
    if is_vegetarian is not None: update_fields['is_vegetarian'] = is_vegetarian
    if is_gluten_free is not None: update_fields['is_gluten_free'] = is_gluten_free

    item = schemas.MenuItemUpdate(**update_fields)
    db_item = crud.update_menu_item(db, item_id, item, image_data)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
