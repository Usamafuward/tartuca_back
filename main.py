from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, menu, offers, orders, reservations, reviews, gallery, admin, settings, customers

import os
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tartuca API", description="Backend for Tartuca Restaurant")

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
    "https://tartuca-user.vercel.app",
    "https://tartuca-admin.vercel.app",
]

extra_origins = os.getenv("CORS_ORIGINS")
if extra_origins:
    allowed_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(offers.router)
app.include_router(orders.router)
app.include_router(reservations.router)
app.include_router(reviews.router)
app.include_router(gallery.router)
app.include_router(admin.router)
app.include_router(settings.router)
app.include_router(customers.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Tartuca API"}
