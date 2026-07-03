from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime
from decimal import Decimal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, role: str = "customer"):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Menu
def get_categories(db: Session):
    return db.query(models.Category).order_by(models.Category.display_order).all()

def get_menu_items(db: Session, category_id: int = None):
    query = db.query(models.MenuItem)
    if category_id:
        query = query.filter(models.MenuItem.category_id == category_id)
    return query.all()

def get_menu_item(db: Session, item_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()

def create_menu_item(db: Session, item: schemas.MenuItemCreate, image_data: bytes = None):
    data = item.dict()
    if image_data:
        data['image_data'] = image_data
    db_item = models.MenuItem(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_menu_item(db: Session, item_id: int):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

# Special Offers
def get_special_offers(db: Session):
    return db.query(models.SpecialOffer).filter(models.SpecialOffer.is_active == True).all()

def create_special_offer(db: Session, offer: schemas.SpecialOfferCreate, image_data: bytes = None):
    data = offer.dict()
    if image_data:
        data['image_data'] = image_data
    db_offer = models.SpecialOffer(**data)
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

def delete_special_offer(db: Session, offer_id: int):
    offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.id == offer_id).first()
    if offer:
        db.delete(offer)
        db.commit()
        return True
    return False

# Orders
def create_order(db: Session, order: schemas.OrderCreate, user_id: int = None):
    # Calculate total and verify prices
    total_amount = Decimal(0)
    order_items_data = []
    
    for item in order.items:
        price = Decimal(0)
        menu_item_id = None
        special_offer_id = None

        if item.menu_item_id:
            menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
            if menu_item:
                price = menu_item.price
                menu_item_id = menu_item.id
        
        elif item.special_offer_id:
            offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.id == item.special_offer_id).first()
            if offer:
                price = offer.price
                special_offer_id = offer.id

        if price > 0:
            total_amount += price * item.quantity
            order_items_data.append({
                "menu_item_id": menu_item_id,
                "special_offer_id": special_offer_id,
                "quantity": item.quantity,
                "unit_price": price
            })

    db_order = models.Order(
        user_id=user_id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        delivery_instructions=order.delivery_instructions,
        payment_method=order.payment_method,
        total_amount=total_amount,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item_data in order_items_data:
        db_item = models.OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order

# Reservations
def create_reservation(db: Session, reservation: schemas.ReservationCreate):
    db_res = models.Reservation(**reservation.dict())
    db.add(db_res)
    db.commit()
    db.refresh(db_res)
    return db_res

def get_reservations(db: Session):
    return db.query(models.Reservation).order_by(models.Reservation.reservation_date.desc(), models.Reservation.reservation_time.desc()).all()

def update_reservation_status(db: Session, res_id: int, status: str):
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if res:
        res.status = status
        db.commit()
        db.refresh(res)
    return res

# Reviews
def create_review(db: Session, review: schemas.ReviewCreate):
    # Basic sentiment analysis placeholder
    sentiment = "positive" if review.rating >= 4 else "negative" if review.rating <= 2 else "neutral"
    
    db_review = models.Review(
        author_name=review.author_name,
        rating=review.rating,
        comment=review.comment,
        sentiment=sentiment,
        is_approved=False
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews(db: Session, approved_only: bool = True):
    query = db.query(models.Review)
    if approved_only:
        query = query.filter(models.Review.is_approved == True)
    return query.order_by(models.Review.created_at.desc()).all()

def approve_review(db: Session, review_id: int, is_approved: bool):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if review:
        review.is_approved = is_approved
        db.commit()
        db.refresh(review)
    return review

# Gallery
def get_gallery_images(db: Session):
    return db.query(models.GalleryImage).all()

def create_gallery_image(db: Session, image: schemas.GalleryImageCreate, image_data: bytes = None):
    data = image.dict()
    if image_data:
        data['image_data'] = image_data
    db_img = models.GalleryImage(**data)
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return db_img

def delete_gallery_image(db: Session, img_id: int):
    img = db.query(models.GalleryImage).filter(models.GalleryImage.id == img_id).first()
    if img:
        db.delete(img)
        db.commit()
        return True
    return False

def update_menu_item(db: Session, item_id: int, item_update: schemas.MenuItemUpdate, image_data: bytes = None):
    db_item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not db_item:
        return None
    
    update_data = item_update.dict(exclude_unset=True)
    if image_data:
        update_data['image_data'] = image_data

    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def update_special_offer(db: Session, offer_id: int, offer_update: schemas.SpecialOfferUpdate, image_data: bytes = None):
    db_offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.id == offer_id).first()
    if not db_offer:
        return None
    
    update_data = offer_update.dict(exclude_unset=True)
    if image_data:
        update_data['image_data'] = image_data

    for key, value in update_data.items():
        setattr(db_offer, key, value)
    
    db.commit()
    db.refresh(db_offer)
    return db_offer


