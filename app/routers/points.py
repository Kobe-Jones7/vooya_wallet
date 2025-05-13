from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import func

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/points",
    tags=["Points"]
)

@router.get("/points")
def get_points():
    return{"message": "You have redeemed your points"}

# ---------------- Earn Points ----------------
@router.post("/earn")
def earn_points(earn: schemas.EarnPoints, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == earn.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    earned_points = 10  # You can make this dynamic based on activity_type

    points_txn = models.PointsTransaction(
        user_id=earn.user_id,
        activity_type=earn.activity_type,
        metadata=earn.metadata,
        points=earned_points
    )

    db.add(points_txn)
    db.commit()

    total = db.query(func.sum(models.PointsTransaction.points)).filter_by(user_id=earn.user_id).scalar() or 0

    return {"message": f"{earned_points} points earned", "total_points": total}


# ---------------- Redeem Points ----------------
@router.post("/redeem")
def redeem_points(redeem: schemas.RedeemPoints, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == redeem.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_points = db.query(func.sum(models.PointsTransaction.points)).filter_by(user_id=redeem.user_id).scalar() or 0

    if total_points < redeem.points:
        raise HTTPException(status_code=400, detail="Not enough points")

    redemption = models.PointsTransaction(
        user_id=redeem.user_id,
        activity_type="redeem",
        metadata=redeem.reward_type,
        points=-redeem.points
    )

    db.add(redemption)
    db.commit()

    return {"message": f"{redeem.points} points redeemed for {redeem.reward_type}", "remaining_points": total_points - redeem.points}


# ---------------- Check Points Balance ----------------
@router.get("/balance/{user_id}")
def get_points_balance(user_id: int = Path(..., description="User ID"), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_points = db.query(func.sum(models.PointsTransaction.points)).filter_by(user_id=user_id).scalar() or 0
    return {"user_id": user_id, "total_points": total_points}
