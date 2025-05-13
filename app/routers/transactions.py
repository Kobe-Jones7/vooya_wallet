from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/transactions")
def get_transactions():
    return{"message": "Your Transactions here"}

# ---------------- Get All Transactions for a Wallet ----------------
@router.get("/wallet/{wallet_id}", response_model=list[schemas.TransactionOut])
def get_wallet_transactions(wallet_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.wallet_id == wallet_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this wallet")
    return transactions

from fastapi import Query

# ---------------- Get Transactions by Wallet ----------------
@router.get("/wallet/{wallet_id}")
def get_transactions_by_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    transactions = db.query(models.Transaction).filter(models.Transaction.wallet_id == wallet_id).all()
    return {"wallet_id": wallet_id, "transactions": transactions}

@router.get("/user/{user_id}")
def get_transactions_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all wallets owned by the user
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).all()
    wallet_ids = [wallet.id for wallet in wallets]

    if not wallet_ids:
        return {"user_id": user_id, "transactions": []}

    # Fetch all transactions for those wallets
    transactions = db.query(models.Transaction).filter(models.Transaction.wallet_id.in_(wallet_ids)).all()
    return {"user_id": user_id, "transactions": transactions}


# ---------------- Get Single Transaction ----------------
@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
def get_transactions(transaction_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# ---------------- Wallet Transfer ----------------
@router.post("/transfer")
def transfer_funds(
    from_wallet_id: int,
    to_wallet_id: int,
    amount: float,
    db: Session = Depends(get_db)
):
    if from_wallet_id == to_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet")

    from_wallet = db.query(models.Wallet).filter(models.Wallet.id == from_wallet_id).first()
    to_wallet = db.query(models.Wallet).filter(models.Wallet.id == to_wallet_id).first()

    if not from_wallet or not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if from_wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in sender's wallet")

    # Perform transfer
    from_wallet.balance -= amount
    to_wallet.balance += amount

    # Record transactions
    db.add(models.Transaction(wallet_id=from_wallet_id, amount=-amount, transaction_type="debit"))
    db.add(models.Transaction(wallet_id=to_wallet_id, amount=amount, transaction_type="credit"))

    db.commit()

    return {
        "message": "Transfer successful",
        "from_wallet_balance": from_wallet.balance,
        "to_wallet_balance": to_wallet.balance
    }
# ---------------- Transaction Summary by Wallet ----------------
@router.get("/summary/wallet/{wallet_id}")
def transaction_summary_by_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Total credit (sum of all credit transactions)
    total_credits = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.wallet_id == wallet_id,
        models.Transaction.transaction_type == "credit"
    ).scalar() or 0

    # Total debit (sum of all debit transactions)
    total_debits = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.wallet_id == wallet_id,
        models.Transaction.transaction_type == "debit"
    ).scalar() or 0

    # Current balance (credit - debit)
    current_balance = total_credits + total_debits

    return {
        "wallet_id": wallet_id,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "current_balance": current_balance
    }
# ---------------- Transaction Summary by User ----------------
@router.get("/summary/user/{user_id}")
def transaction_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all wallets owned by the user
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).all()
    wallet_ids = [wallet.id for wallet in wallets]

    if not wallet_ids:
        return {"user_id": user_id, "total_credits": 0, "total_debits": 0, "current_balance": 0}

    # Total credits (sum of all credit transactions across all wallets)
    total_credits = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.wallet_id.in_(wallet_ids),
        models.Transaction.transaction_type == "credit"
    ).scalar() or 0

    # Total debits (sum of all debit transactions across all wallets)
    total_debits = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.wallet_id.in_(wallet_ids),
        models.Transaction.transaction_type == "debit"
    ).scalar() or 0

    # Current balance (credit - debit)
    current_balance = total_credits + total_debits
    
    # ---------------- Paginated Transactions by User ----------------
@router.get("/user/{user_id}", response_model=List[schemas.TransactionOut])
def get_transactions_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all wallets owned by the user
    wallets = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).all()
    wallet_ids = [wallet.id for wallet in wallets]

    if not wallet_ids:
        return []

    # Fetch paginated transactions for those wallets
    transactions = db.query(models.Transaction).filter(models.Transaction.wallet_id.in_(wallet_ids))\
        .offset(skip).limit(limit).all()

    return transactions

# ---------------- Paginated Transactions ----------------
@router.get("/", response_model=List[schemas.TransactionOut])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions

    return {
        "user_id": user_id,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "current_balance": current_balance
    }
