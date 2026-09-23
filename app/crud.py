from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt
from datetime import datetime
from decimal import Decimal

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

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

def create_category(db: Session, category: schemas.CategoryCreate):
    db_cat = models.Category(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
    db_cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_cat:
        return None
    for key, value in category_update.dict(exclude_unset=True).items():
        setattr(db_cat, key, value)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def delete_category(db: Session, category_id: int):
    db_cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_cat:
        return False
    # Reassign or delete menu items in this category or check
    db.delete(db_cat)
    db.commit()
    return True

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
def create_reservation(db: Session, reservation: schemas.ReservationCreate, user_id: int = None):
    data = reservation.dict()
    if user_id:
        data["user_id"] = user_id
    db_res = models.Reservation(**data)
    db.add(db_res)
    db.commit()
    db.refresh(db_res)
    return db_res

def get_reservations(db: Session):
    return db.query(models.Reservation).order_by(models.Reservation.reservation_date.desc(), models.Reservation.reservation_time.desc()).all()

def get_user_reservations(db: Session, user_id: int = None, email: str = None):
    query = db.query(models.Reservation)
    if user_id and email:
        query = query.filter((models.Reservation.user_id == user_id) | (models.Reservation.customer_email == email))
    elif user_id:
        query = query.filter(models.Reservation.user_id == user_id)
    elif email:
        query = query.filter(models.Reservation.customer_email == email)
    return query.order_by(models.Reservation.reservation_date.desc(), models.Reservation.reservation_time.desc()).all()

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

# Settings
def get_restaurant_settings(db: Session):
    settings = db.query(models.RestaurantSetting).first()
    if not settings:
        settings = models.RestaurantSetting(
            name="Tartuca",
            phone="+94 11 257 4820",
            email="info@tartuca.lk",
            currency="LKR (Rs.)",
            address="42 Green Path (Ananda Coomaraswamy Mw), Colombo 07, Sri Lanka",
            opening_hours="Mon-Sun: 11:30 AM - 11:00 PM",
            delivery_fee=Decimal("350.00"),
            min_delivery_time=25,
            max_delivery_time=45
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_restaurant_settings(db: Session, settings_update: schemas.RestaurantSettingUpdate):
    settings = get_restaurant_settings(db)
    for key, value in settings_update.dict(exclude_unset=True).items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


