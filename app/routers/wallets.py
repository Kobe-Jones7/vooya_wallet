from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/wallets",
    tags=["Wallets"]
)

@router.get("/wallets")
def get_wallets():
    return{"message": "Here is the wallet"}

# ---------------- Create Wallet ----------------
@router.post("/", response_model=schemas.WalletOut)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    new_wallet = models.Wallet(user_id=wallet.user_id, balance=0.0, currency=wallet.currency)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet


# ---------------- Get Wallet ----------------
@router.get("/{wallet_id}", response_model=schemas.WalletOut)
def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


# ---------------- Fund Wallet ----------------
@router.post("/fund")
def fund_wallet(fund: schemas.FundWallet, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == fund.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.balance += fund.amount

    # Create a transaction record
    transaction = models.Transaction(
        wallet_id=wallet.id,
        amount=fund.amount,
        transaction_type="credit"
    )
    db.add(transaction)

    db.commit()
    db.refresh(wallet)
    return {"message": "Wallet funded successfully", "new_balance": wallet.balance}
