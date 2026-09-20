from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
from .auth import get_current_user

router = APIRouter(
    prefix="/api/settings",
    tags=["settings"]
)

@router.get("", response_model=schemas.RestaurantSetting)
@router.get("/", response_model=schemas.RestaurantSetting, include_in_schema=False)
def read_settings(db: Session = Depends(database.get_db)):
    return crud.get_restaurant_settings(db)

@router.put("", response_model=schemas.RestaurantSetting)
@router.put("/", response_model=schemas.RestaurantSetting, include_in_schema=False)
def update_settings(
    settings_update: schemas.RestaurantSettingUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.update_restaurant_settings(db, settings_update)
