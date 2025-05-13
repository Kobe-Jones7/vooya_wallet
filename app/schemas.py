from pydantic import BaseModel, EmailStr
from typing import Optional

# ---------------- User Schemas ----------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


# ---------------- Wallet Schemas ----------------
class WalletCreate(BaseModel):
    user_id: int
    currency: str

class WalletOut(BaseModel):
    id: int
    user_id: int
    balance: float
    currency: str

    class Config:
        orm_mode = True

class FundWallet(BaseModel):
    wallet_id: int
    amount: float
    source: str  # card, bank, promo, etc.


# ---------------- Points Schemas ----------------
class EarnPoints(BaseModel):
    user_id: int
    activity_type: str
    metadata: Optional[str] = None

class RedeemPoints(BaseModel):
    user_id: int
    points: int
    reward_type: str


# ---------------- Transaction Schemas ----------------
class TransactionOut(BaseModel):
    id: int
    wallet_id: int
    amount: float
    transaction_type: str  # credit or debit
    created_at: str

    class Config:
        orm_mode = True
