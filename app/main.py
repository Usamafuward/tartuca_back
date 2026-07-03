from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, menu, offers, orders, reservations, reviews, gallery, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tartuca API", description="Backend for Tartuca Restaurant")

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*" # For development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
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

@app.get("/")
def read_root():
    return {"message": "Welcome to Tartuca API"}
