from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
from datetime import datetime, timedelta
from typing import Annotated
import os

# Auth handling imports
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)

# Configuration for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 30 minutes inactivity expiry

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get current user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(token: Annotated[str | None, Depends(oauth2_scheme_optional)], db: Session = Depends(database.get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = schemas.TokenData(email=email)
    except JWTError:
        return None
    user = crud.get_user_by_email(db, email=token_data.email)
    return user

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(database.get_db)):
    return crud.update_user(db, user_id=current_user.id, user_update=user_update)

@router.get("/users/{user_id}/avatar")
def get_user_avatar(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.image_data:
        media_type = "image/jpeg"
        if db_user.image_data.startswith(b"\x89PNG"):
            media_type = "image/png"
        elif db_user.image_data.startswith(b"RIFF") and b"WEBP" in db_user.image_data[:16]:
            media_type = "image/webp"
        elif db_user.image_data.startswith(b"GIF8"):
            media_type = "image/gif"
        return Response(content=db_user.image_data, media_type=media_type)
    
    if db_user.profile_picture:
        return RedirectResponse(url=db_user.profile_picture)
        
    raise HTTPException(status_code=404, detail="Avatar image not found")

@router.post("/me/avatar", response_model=schemas.User)
def upload_avatar_me(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")
    
    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")
    
    current_user.image_data = contents
    timestamp = int(datetime.utcnow().timestamp())
    current_user.profile_picture = f"/api/auth/users/{current_user.id}/avatar?t={timestamp}"
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/create-admin", response_model=schemas.User)
def create_admin(user: schemas.UserCreate, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(database.get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user, role="admin")

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
