import os
import sys
from app.crud import get_password_hash
from app.database import SessionLocal
from app.models import User, Order, Reservation, Review

# 10 Authentic Sri Lankan Customer Profiles
CUSTOMER_PROFILES = [
    {
        "id": 2,
        "full_name": "Kasun Perera",
        "email": "kasun.perera@gmail.com",
        "phone": "+94 77 123 4567",
        "address": "14/2 Alfred House Gardens, Colombo 03, Sri Lanka",
    },
    {
        "id": 3,
        "full_name": "Dilani Jayawardena",
        "email": "dilani.j@gmail.com",
        "phone": "+94 71 234 5678",
        "address": "88 Horton Place, Colombo 07, Sri Lanka",
    },
    {
        "id": 4,
        "full_name": "Roshan Senanayake",
        "email": "roshan.s@gmail.com",
        "phone": "+94 76 345 6789",
        "address": "25/4 Havelock Road, Colombo 05, Sri Lanka",
    },
    {
        "id": 5,
        "full_name": "Amanda Fernando",
        "email": "amanda.fernando@gmail.com",
        "phone": "+94 77 456 7890",
        "address": "102 Galle Road, Mount Lavinia, Sri Lanka",
    },
    {
        "id": 6,
        "full_name": "Dinesh Wickramasinghe",
        "email": "dinesh.w@gmail.com",
        "phone": "+94 70 567 8901",
        "address": "45 Ward Place, Colombo 07, Sri Lanka",
    },
    {
        "id": 8,
        "full_name": "Shamila Weerasinghe",
        "email": "shamila.w@gmail.com",
        "phone": "+94 72 678 9012",
        "address": "18 Flower Road, Colombo 07, Sri Lanka",
    },
    {
        "id": 9,
        "full_name": "Kaveen Alwis",
        "email": "kaveen.alwis@gmail.com",
        "phone": "+94 77 789 0123",
        "address": "63 Duplication Road, Colombo 04, Sri Lanka",
    },
    {
        "id": 10,
        "full_name": "Minoli Silva",
        "email": "minoli.silva@gmail.com",
        "phone": "+94 71 890 1234",
        "address": "32 Barnes Place, Colombo 07, Sri Lanka",
    },
    {
        "id": 11,
        "full_name": "Sachith Mendis",
        "email": "sachith.mendis@gmail.com",
        "phone": "+94 76 901 2345",
        "address": "77 Nawala Road, Rajagiriya, Sri Lanka",
    },
    {
        "id": 12,
        "full_name": "Tharushi Ranatunga",
        "email": "tharushi.r@gmail.com",
        "phone": "+94 77 012 3456",
        "address": "50 Kynsey Road, Colombo 08, Sri Lanka",
    }
]

UNIFIED_PASSWORD = "Customer@123"

def update_customers():
    db = SessionLocal()
    try:
        hashed_password = get_password_hash(UNIFIED_PASSWORD)
        print(f"Hashed password generated for '{UNIFIED_PASSWORD}'")

        customer_map = {}
        for prof in CUSTOMER_PROFILES:
            user = db.query(User).filter(User.id == prof["id"]).first()
            if not user:
                # In case user id doesn't exist, create it
                user = User(
                    id=prof["id"],
                    role="customer"
                )
                db.add(user)
            
            user.full_name = prof["full_name"]
            user.email = prof["email"]
            user.phone = prof["phone"]
            user.address = prof["address"]
            user.password_hash = hashed_password
            user.role = "customer"
            customer_map[user.id] = user
            print(f"Updated User #{user.id}: {user.full_name} ({user.email})")

        db.commit()

        # Now link and synchronize orders with these customers
        all_orders = db.query(Order).order_by(Order.id.asc()).all()
        # Ensure every order has a valid customer
        user_ids = [p["id"] for p in CUSTOMER_PROFILES]
        
        for idx, order in enumerate(all_orders):
            # If order has no user_id or user_id not in customer profiles, distribute across user_ids
            assigned_user_id = order.user_id if order.user_id in customer_map else user_ids[idx % len(user_ids)]
            order.user_id = assigned_user_id
            cust = customer_map[assigned_user_id]
            order.customer_name = cust.full_name
            order.customer_email = cust.email
            order.customer_phone = cust.phone
            order.delivery_address = cust.address
            print(f"Synchronized Order #{order.id} -> {cust.full_name}")

        # Now link and synchronize reservations
        all_reservations = db.query(Reservation).order_by(Reservation.id.asc()).all()
        for idx, res in enumerate(all_reservations):
            assigned_user_id = res.user_id if res.user_id in customer_map else user_ids[idx % len(user_ids)]
            res.user_id = assigned_user_id
            cust = customer_map[assigned_user_id]
            res.customer_name = cust.full_name
            res.customer_email = cust.email
            res.customer_phone = cust.phone
            print(f"Synchronized Reservation #{res.id} -> {cust.full_name}")

        db.commit()
        print("\nAll customers, orders, and reservations successfully updated and synchronized!")

    except Exception as e:
        db.rollback()
        print(f"Error updating customers: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_customers()
