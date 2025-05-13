from app.database import Base, engine
import app.models  # important!

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully!")
