from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
from .auth import get_current_user
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/api/dashboard",
    tags=["admin"]
)

@router.get("/stats")
def read_dashboard_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    
    # 1. Total Revenue (sum of non-cancelled orders)
    revenue = float(db.query(func.sum(models.Order.total_amount)).filter(models.Order.status != 'cancelled').scalar() or 0)
    cancelled_revenue = float(db.query(func.sum(models.Order.total_amount)).filter(models.Order.status == 'cancelled').scalar() or 0)
    
    # 2. Orders count
    orders_all = db.query(models.Order).order_by(models.Order.created_at.asc()).all()
    orders_count = len(orders_all)
    cancelled_orders_count = sum(1 for o in orders_all if o.status == 'cancelled')
    
    # 3. New Customers
    new_customers = db.query(models.User).filter(models.User.role == 'customer').count()

    # 4. Average Order Value
    valid_orders_count = sum(1 for o in orders_all if o.status != 'cancelled')
    avg_order_value = round(revenue / valid_orders_count, 2) if valid_orders_count > 0 else 0.0

    # 4b. Menu Inventory Status
    total_menu_items = db.query(models.MenuItem).count()
    available_menu_items = db.query(models.MenuItem).filter(models.MenuItem.is_active == True).count()

    # 5. Daily Revenue & Orders Trend (Last 7 to 14 days)
    daily_map = {}
    for o in orders_all:
        if o.created_at:
            d_str = o.created_at.strftime('%Y-%m-%d')
            label = o.created_at.strftime('%b %d')
            if d_str not in daily_map:
                daily_map[d_str] = {"date": d_str, "label": label, "revenue": 0.0, "orders": 0}
            if o.status != 'cancelled':
                daily_map[d_str]["revenue"] += float(o.total_amount or 0)
            daily_map[d_str]["orders"] += 1

    # Ensure continuous 7-day timeline
    ref_date = max([o.created_at for o in orders_all if o.created_at] or [datetime.now(timezone.utc)])
    trend_7d = []
    for i in range(6, -1, -1):
        target_day = ref_date - timedelta(days=i)
        d_str = target_day.strftime('%Y-%m-%d')
        label = target_day.strftime('%b %d')
        if d_str in daily_map:
            entry = daily_map[d_str]
            trend_7d.append({
                "date": d_str,
                "label": label,
                "revenue": round(entry["revenue"], 2),
                "orders": entry["orders"]
            })
        else:
            trend_7d.append({
                "date": d_str,
                "label": label,
                "revenue": 0.0,
                "orders": 0
            })

    # 14-day timeline
    trend_14d = []
    for i in range(13, -1, -1):
        target_day = ref_date - timedelta(days=i)
        d_str = target_day.strftime('%Y-%m-%d')
        label = target_day.strftime('%b %d')
        if d_str in daily_map:
            entry = daily_map[d_str]
            trend_14d.append({
                "date": d_str,
                "label": label,
                "revenue": round(entry["revenue"], 2),
                "orders": entry["orders"]
            })
        else:
            trend_14d.append({
                "date": d_str,
                "label": label,
                "revenue": 0.0,
                "orders": 0
            })

    # 6. Top-Selling Menu Items (Join OrderItem -> MenuItem & SpecialOffer)
    order_items = db.query(models.OrderItem).join(models.Order).filter(models.Order.status != 'cancelled').all()
    items_map = {}
    total_items_revenue = 0.0

    for oi in order_items:
        name = "Special Item"
        category = "General"
        if oi.menu_item:
            name = oi.menu_item.name
            if oi.menu_item.category:
                category = oi.menu_item.category.name
        elif oi.special_offer:
            name = oi.special_offer.title
            category = "Special Offer"
        
        qty = oi.quantity or 1
        item_rev = float(oi.unit_price or 0) * qty
        total_items_revenue += item_rev

        if name not in items_map:
            items_map[name] = {"name": name, "category": category, "quantity": 0, "revenue": 0.0}
        items_map[name]["quantity"] += qty
        items_map[name]["revenue"] += item_rev

    top_items = sorted(items_map.values(), key=lambda x: x["quantity"], reverse=True)[:5]
    for it in top_items:
        it["revenue"] = round(it["revenue"], 2)
        it["percentage"] = round((it["revenue"] / total_items_revenue * 100) if total_items_revenue > 0 else 0, 1)

    # 7. Category Breakdown
    cat_map = {}
    for oi in order_items:
        cat_name = "Other"
        if oi.menu_item and oi.menu_item.category:
            cat_name = oi.menu_item.category.name
        elif oi.special_offer:
            cat_name = "Chef's Specials"
        
        qty = oi.quantity or 1
        cat_rev = float(oi.unit_price or 0) * qty
        if cat_name not in cat_map:
            cat_map[cat_name] = {"name": cat_name, "quantity": 0, "revenue": 0.0}
        cat_map[cat_name]["quantity"] += qty
        cat_map[cat_name]["revenue"] += cat_rev

    category_sales = sorted(cat_map.values(), key=lambda x: x["revenue"], reverse=True)
    for c in category_sales:
        c["revenue"] = round(c["revenue"], 2)
        c["percentage"] = round((c["revenue"] / total_items_revenue * 100) if total_items_revenue > 0 else 0, 1)

    # 8. Order Status Funnel
    status_counts = {"delivered": 0, "cooking": 0, "pending": 0, "cancelled": 0}
    for o in orders_all:
        st = (o.status or "pending").lower()
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1
    
    order_status_distribution = [
        {
            "status": st,
            "count": count,
            "percentage": round((count / orders_count * 100) if orders_count > 0 else 0, 1)
        }
        for st, count in status_counts.items()
    ]

    # 9. Reservations Summary
    reservations_all = db.query(models.Reservation).all()
    total_guests = sum(r.party_size or 0 for r in reservations_all)
    res_status = {"confirmed": 0, "pending": 0, "completed": 0, "cancelled": 0}
    for r in reservations_all:
        st = (r.status or "pending").lower()
        res_status[st] = res_status.get(st, 0) + 1

    reservations_summary = {
        "total": len(reservations_all),
        "total_guests": total_guests,
        "confirmed": res_status.get("confirmed", 0),
        "pending": res_status.get("pending", 0),
        "completed": res_status.get("completed", 0),
        "cancelled": res_status.get("cancelled", 0),
    }

    # 10. Reviews & Customer Sentiment
    reviews_all = db.query(models.Review).all()
    total_reviews = len(reviews_all)
    avg_rating = round(sum(r.rating for r in reviews_all) / total_reviews, 1) if total_reviews > 0 else 5.0
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews_all:
        if r.rating in rating_distribution:
            rating_distribution[r.rating] += 1

    customer_sentiment = {
        "average_rating": avg_rating,
        "total_reviews": total_reviews,
        "rating_distribution": rating_distribution
    }

    return {
        "revenue": round(revenue, 2),
        "orders_count": orders_count,
        "new_customers": new_customers,
        "avg_order_value": avg_order_value,
        "cancelled_revenue": round(cancelled_revenue, 2),
        "cancelled_orders": cancelled_orders_count,
        "menu_stats": {
            "total": total_menu_items,
            "available": available_menu_items,
            "sold_out": total_menu_items - available_menu_items
        },
        "revenue_trend": trend_7d,
        "revenue_trend_14d": trend_14d,
        "top_items": top_items,
        "category_sales": category_sales,
        "order_status_distribution": order_status_distribution,
        "reservations_summary": reservations_summary,
        "customer_sentiment": customer_sentiment
    }
