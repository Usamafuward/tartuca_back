from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    image_url: Optional[str] = None
    display_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# Menu Item Schemas
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    is_active: bool = True
    is_vegetarian: bool = False
    is_gluten_free: bool = False
    category_id: int

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    category_id: Optional[int] = None

class MenuItem(MenuItemBase):
    id: int
    created_at: datetime
    has_image: bool = False
    class Config:
        from_attributes = True

# Special Offer Schemas
class SpecialOfferBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    badge_text: Optional[str] = None
    badge_color: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class SpecialOfferCreate(SpecialOfferBase):
    pass

class SpecialOfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    badge_text: Optional[str] = None
    badge_color: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class SpecialOffer(SpecialOfferBase):
    id: int
    created_at: datetime
    has_image: bool = False
    class Config:
        from_attributes = True

# Order Schemas
class OrderItemBase(BaseModel):
    menu_item_id: Optional[int] = None
    special_offer_id: Optional[int] = None
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    unit_price: Decimal
    menu_item: Optional[MenuItem] = None
    special_offer: Optional[SpecialOffer] = None
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: str
    delivery_address: str
    delivery_instructions: Optional[str] = None
    payment_method: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderStatusUpdate(BaseModel):
    status: str

class Order(OrderBase):
    id: int
    user_id: Optional[int] = None
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[OrderItem]
    class Config:
        from_attributes = True

# Reservation Schemas
class ReservationBase(BaseModel):
    user_id: Optional[int] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    party_size: int
    reservation_date: date
    reservation_time: time
    occasion: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class ReservationStatusUpdate(BaseModel):
    status: str

class Reservation(ReservationBase):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# Review Schemas
class ReviewBase(BaseModel):
    author_name: str
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewApprove(BaseModel):
    is_approved: bool

class Review(ReviewBase):
    id: int
    sentiment: str
    is_approved: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Gallery Schemas
class GalleryImageBase(BaseModel):
    category: str
    image_url: Optional[str] = None
    alt_text: str

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImage(GalleryImageBase):
    id: int
    created_at: datetime
    has_image: bool = False
    class Config:
        from_attributes = True

# Dashboard Stats
class DashboardStats(BaseModel):
    revenue: Decimal
    orders_count: int
    new_customers: Optional[int] = 0
    avg_order_value: Optional[float] = 0.0

# Restaurant Settings Schemas
class RestaurantSettingBase(BaseModel):
    name: str = "Tartuca"
    phone: Optional[str] = "+1 (555) 123-4567"
    email: Optional[str] = "admin@tartuca.com"
    currency: Optional[str] = "USD ($)"
    address: Optional[str] = "123 Culinary Avenue, Foodie City, FC 90210"
    opening_hours: Optional[str] = "Mon-Sun: 11:00 AM - 10:00 PM"
    delivery_fee: Optional[Decimal] = Decimal("2.99")
    min_delivery_time: Optional[int] = 30
    max_delivery_time: Optional[int] = 45

class RestaurantSettingUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    currency: Optional[str] = None
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    delivery_fee: Optional[Decimal] = None
    min_delivery_time: Optional[int] = None
    max_delivery_time: Optional[int] = None

class RestaurantSetting(RestaurantSettingBase):
    id: int
    class Config:
        from_attributes = True

