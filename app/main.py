from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import users, wallets, points, transactions

# ✅ Add these imports
from database import Base, engine
import models  # Make sure all your models are imported here

# ✅ Create tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vooya Wallet API",
    description="API for Vooya travel wallet, points system, and transactions",
    version="1.0.0"
)

# Optional: Allow frontend apps to call your API (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific frontend URLs in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router)
app.include_router(wallets.router)
app.include_router(points.router)
app.include_router(transactions.router)

# Health check
@app.get("/")
def read_root():
    return {"message": "Vooya Wallet API is live!"}
