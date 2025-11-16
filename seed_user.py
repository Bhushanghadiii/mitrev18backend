from datetime import datetime
from app.database import SessionLocal
from app.models.tenant import Tenant, User
from app.utils.security import get_password_hash

def seed():
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.org_name == "Example Organization").first()
        if not tenant:
            tenant = Tenant(
                org_name="Example Organization",
                industry="Information Technology",
                subscription_tier="free",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            user = User(
                tenant_id=tenant.id,
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=get_password_hash("strongpassword123"[:72]),
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()

        print(f"Seed completed: Tenant '{tenant.org_name}' and User '{user.email}'")
    except Exception as e:
        print(f"Failed to seed data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
