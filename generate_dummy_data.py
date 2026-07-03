import os
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, crud
from datetime import datetime, date, time, timedelta
import random

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_dummy_data():
    db = SessionLocal()
    try:
        print("Creating dummy data...")

        # 1. Users
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.email == "admin@tartuca.com").first()
        if not admin:
            admin = models.User(
                email="admin@tartuca.com",
                password_hash=crud.get_password_hash("admin123"[:72]),  # Truncate password
                full_name="Admin User",
                role="admin",
                phone="1234567890"
            )
            db.add(admin)
        
        # Customers
        customers = []
        for i in range(5):
            email = f"customer{i+1}@example.com"
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                user = models.User(
                    email=email,
                    password_hash=crud.get_password_hash("password"[:72]),  # Truncate password
                    full_name=f"Customer {i+1}",
                    role="customer",
                    phone=f"555-010{i}"
                )
                db.add(user)
                customers.append(user)
            else:
                customers.append(user)
        
        db.commit()
        print("Users created.")

        # 2. Categories
        categories_data = [
            {"name": "Pizza", "slug": "pizza", "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=60", "display_order": 1},
            {"name": "Pasta", "slug": "pasta", "image_url": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=500&q=60", "display_order": 2},
            {"name": "Salads", "slug": "salads", "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=500&q=60", "display_order": 3},
            {"name": "Desserts", "slug": "desserts", "image_url": "https://images.unsplash.com/photo-1563729768640-d65d41855869?auto=format&fit=crop&w=500&q=60", "display_order": 4},
            {"name": "Drinks", "slug": "drinks", "image_url": "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=500&q=60", "display_order": 5}
        ]
        
        db_categories = {}
        for cat_data in categories_data:
            cat = db.query(models.Category).filter(models.Category.slug == cat_data["slug"]).first()
            if not cat:
                cat = models.Category(**cat_data)
                db.add(cat)
                db.commit() # Commit to get ID
                db.refresh(cat)
            db_categories[cat.slug] = cat
        print("Categories created.")

        # 3. Menu Items
        menu_items_data = [
            {"name": "Margherita Pizza", "category_slug": "pizza", "price": 12.99, "description": "Classic tomato and mozzarella", "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002", "is_vegetarian": True},
            {"name": "Pepperoni Pizza", "category_slug": "pizza", "price": 14.99, "description": "Spicy pepperoni and cheese", "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e", "is_vegetarian": False},
            {"name": "Spaghetti Carbonara", "category_slug": "pasta", "price": 16.50, "description": "Creamy sauce with pancetta", "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3", "is_vegetarian": False},
            {"name": "Caesar Salad", "category_slug": "salads", "price": 9.99, "description": "Fresh romaine with caesar dressing", "image_url": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9", "is_vegetarian": True},
            {"name": "Tiramisu", "category_slug": "desserts", "price": 8.00, "description": "Classic Italian dessert", "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9", "is_vegetarian": True},
            {"name": "Lemonade", "category_slug": "drinks", "price": 4.50, "description": "Freshly squeezed lemon", "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd", "is_vegetarian": True}
        ]

        db_menu_items = []
        for item_data in menu_items_data:
            cat_slug = item_data.pop("category_slug")
            category = db_categories.get(cat_slug)
            if category:
                item = db.query(models.MenuItem).filter(models.MenuItem.name == item_data["name"]).first()
                if not item:
                    item = models.MenuItem(**item_data, category_id=category.id)
                    db.add(item)
                    db.commit()
                    db.refresh(item)
                db_menu_items.append(item)
        print("Menu Items created.")

        # 4. Special Offers
        offers_data = [
            {"title": "Ultimate Burger Bundle", "description": "Double beef patty, melted cheddar, crispy bacon, and our secret sauce.", "price": 12.99, "badge_text": "20% OFF", "badge_color": "bg-orange-500", "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&q=80&w=800"}, 
            {"title": "Family Pizza Night", "description": "Two large pizzas of your choice, garlic bread, and a 2L soft drink.", "price": 24.50, "badge_text": "HOT DEAL", "badge_color": "bg-red-600", "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&q=80&w=800"}, 
            {"title": "BBQ Chicken Plate", "description": "Slow-cooked BBQ chicken breast served with steamed vegetables and rice.", "price": 15.00, "badge_text": "", "badge_color": "", "image_url": "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?auto=format&fit=crop&q=80&w=800"},
            {"title": "Berry Cheesecake", "description": "Rich and creamy cheesecake topped with fresh berry compote.", "price": 9.00, "badge_text": "", "badge_color": "", "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&q=80&w=800"}
        ]
        
        for offer_data in offers_data:
            offer = db.query(models.SpecialOffer).filter(models.SpecialOffer.title == offer_data["title"]).first()
            if not offer:
                offer = models.SpecialOffer(**offer_data)
                db.add(offer)
        db.commit()
        print("Special Offers created.")

        # 5. Orders
        # Create some orders for customers
        statuses = ["pending", "cooking", "delivered", "cancelled"]
        
        for i in range(10):
            customer = random.choice(customers) if customers else None
            # Mix of registered and guest orders (if user_id is nullable)
            user_id = customer.id if customer and random.choice([True, False]) else None
            
            order = models.Order(
                user_id=user_id,
                customer_name=customer.full_name if user_id else f"Guest User {i}",
                customer_email=customer.email if user_id else f"guest{i}@example.com",
                customer_phone="555-0000",
                delivery_address="123 Main St, City",
                total_amount=0, # Will calculate
                status=random.choice(statuses),
                payment_method="credit_card"
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            # Add items to order
            total = 0
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                menu_item = random.choice(db_menu_items)
                quantity = random.randint(1, 2)
                order_item = models.OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    unit_price=menu_item.price
                )
                db.add(order_item)
                total += (menu_item.price * quantity)
            
            order.total_amount = total
            db.commit()
        print("Orders created.")

        # 6. Reservations
        for i in range(5):
            res = models.Reservation(
                customer_name=f"Reserver {i}",
                customer_email=f"reserver{i}@example.com",
                customer_phone="555-1111",
                party_size=random.randint(2, 6),
                reservation_date=date.today() + timedelta(days=random.randint(1, 7)),
                reservation_time=time(hour=random.randint(17, 21), minute=0),
                occasion="Birthday" if i % 2 == 0 else "Dinner"
            )
            db.add(res)
        db.commit()
        print("Reservations created.")
        
        # 7. Reviews
        author_names = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"]
        for i in range(5):
            review = models.Review(
                author_name=author_names[i],
                rating=random.randint(3, 5),
                comment=f"Great food! Review number {i}",
                sentiment="positive" if random.choice([True, False]) else "neutral",
                is_approved=random.choice([True, False])
            )
            db.add(review)
        db.commit()
        print("Reviews created.")

        # 8. Gallery Images
        gallery_images = [
            {"category": "Food", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&q=80&w=800", "alt_text": "Gourmet Dish"},
            {"category": "Interior", "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&q=80&w=800", "alt_text": "Restaurant Interior"},
            {"category": "Food", "image_url": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&q=80&w=800", "alt_text": "Salad"},
            {"category": "Events", "image_url": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800", "alt_text": "Private Party"},
            {"category": "Food", "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&q=80&w=800", "alt_text": "Pizza"},
            {"category": "Interior", "image_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&q=80&w=800", "alt_text": "Dining Area"},
            {"category": "Food", "image_url": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&q=80&w=800", "alt_text": "French Toast"},
            {"category": "Events", "image_url": "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&q=80&w=800", "alt_text": "Wedding Reception"},
        ]

        for image_data in gallery_images:
            existing = db.query(models.GalleryImage).filter(
                models.GalleryImage.image_url == image_data["image_url"]
            ).first()
            if not existing:
                db.add(models.GalleryImage(**image_data))
        db.commit()
        print("Gallery images created.")

        print("Dummy data generation complete!")

    except Exception as e:
        print(f"Error creating dummy data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data()
