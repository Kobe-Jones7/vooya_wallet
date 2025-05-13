from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Wallet, Vendor, Tour, TourTransaction, PointsTransaction

# Start DB session
db: Session = SessionLocal()

try:
    # ---- Clear existing data in child-to-parent order ----
    db.query(TourTransaction).delete()
    db.query(PointsTransaction).delete()
    db.query(Wallet).delete()
    db.query(Tour).delete()
    db.query(Vendor).delete()
    db.query(User).delete()
    db.commit()

    # ---- Create Sample Users ----
    user1 = User(name="Kofi Mensah", email="kofi@example.com", password="hashedpassword")
    user2 = User(name="Ama Serwaa", email="ama@example.com", password="hashedpassword")
    db.add_all([user1, user2])
    db.commit()

    # ---- Create Wallets for Users ----
    wallet1 = Wallet(user_id=user1.id, balance=5000.0, currency="GHS")
    wallet2 = Wallet(user_id=user2.id, balance=3000.0, currency="GHS")
    db.add_all([wallet1, wallet2])
    db.commit()

    # ---- Create Vendors ----
    vendor1 = Vendor(name="Explore Ghana Tours", service_type="tour")
    vendor2 = Vendor(name="Takoradi Adventures", service_type="tour")
    db.add_all([vendor1, vendor2])
    db.commit()

    # ---- Create Tours ----
    tour1 = Tour(name="Cape Coast Castle Visit", location="Cape Coast", distance_km=150.0, price=200.0, vendor_id=vendor1.id)
    tour2 = Tour(name="Nzulezu Stilt Village", location="Western Region", distance_km=280.0, price=400.0, vendor_id=vendor2.id)
    db.add_all([tour1, tour2])
    db.commit()

    print("✅ Seed data inserted successfully.")

except Exception as e:
    db.rollback()
    print(f"❌ Error inserting seed data: {e}")

finally:
    db.close()
