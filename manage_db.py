from db import Base, engine, SessionLocal
from models import User

Base.metadata.create_all(bind=engine)

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
def default_admin():
    is_user_exists = SessionLocal().query(User).filter_by(is_default_user=1).first()
    if is_user_exists:
        return
    user = User(email="admin", password="admin", is_default_user=1)
    db = SessionLocal()
    db.add(user)
    db.commit()
    db.close()
