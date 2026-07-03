import os
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, crud

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def link_orders_to_users():
    db = SessionLocal()
    try:
        print("Linking orphan orders to users by email...")
        
        # Get all orders with null user_id
        orphan_orders = db.query(models.Order).filter(models.Order.user_id == None).all()
        print(f"Found {len(orphan_orders)} orphan orders.")
        
        count = 0
        for order in orphan_orders:
            if order.customer_email:
                user = db.query(models.User).filter(models.User.email == order.customer_email).first()
                if user:
                    order.user_id = user.id
                    count += 1
                    print(f"Linked Order #{order.id} to User {user.email}")
        
        db.commit()
        print(f"Successfully linked {count} orders.")

    except Exception as e:
        print(f"Error linking orders: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    link_orders_to_users()
