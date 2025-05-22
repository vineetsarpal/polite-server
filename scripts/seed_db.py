import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root))

from src.database import Base
from src import models, schemas, utils 
from dotenv import load_dotenv

DATABASE_URL= os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_data():
    db: Session = next(get_db())
    print("Seeding database...")
    try:
        # --- Create Users ---
        admin_password_hash = utils.hash_password("admin")
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            admin_user = models.User(
                username="admin",
                password=admin_password_hash,
                email="admin@example.com",
                full_name="Administrator"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        else:
            print("Admin user already exists")

        guest_password_hash = utils.hash_password("guest")
        guest_user = db.query(models.User).filter(models.User.username == "guest").first()
        if not guest_user:
            guest_user = models.User(
                username="guest",
                password=guest_password_hash,
                email="guest@example.com",
                full_name="Guest"
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        else:
            print("Guest user already exists")

        # --- Create Roles ---
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin_role:
            admin_role = models.Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"Created role: {admin_role.name}")
        else:
            print(f"Role '{admin_role.name}' already exists.")

        guest_role = db.query(models.Role).filter(models.Role.name == "guest").first()
        if not guest_role:
            guest_role = models.Role(name="guest", description="Guest role")
            db.add(guest_role)
            db.commit()
            db.refresh(guest_role)
            print(f"Created role: {guest_role.name}")
        else:
            print(f"Role '{guest_role.name}' already exists.")
        

        # --- Create Permissions ---
        perms_to_create = [
            "create:users", "update:users", "delete:users",
            "create:roles", "update:roles", "delete:roles",
            "create:contacts", "update:contacts", "delete:contacts",
            "create:policies", "update:policies", "delete:policies",
        ]

        created_permissions = {}
        for perm_name in perms_to_create:
            permission = db.query(models.Permission).filter(models.Permission.name == perm_name).first()
            if not permission:
                permission = models.Permission(name=perm_name, description=f"Ability to {perm_name.replace(':', ' ')}")
                db.add(permission)
                db.commit()
                db.refresh(permission)
            else:
                print(f"Permission '{permission.name}' already exists.")
            created_permissions[perm_name] = permission

        # --- Assign Permissions to Roles ---
        admin_role.permissions.extend([p for p in created_permissions.values() if p not in admin_role.permissions])
        guest_role_perms = [
            created_permissions["create:contacts"], created_permissions["update:contacts"], 
            created_permissions["create:policies"], created_permissions["update:policies"], 
        ]
        guest_role.permissions.extend([p for p in guest_role_perms if p not in guest_role.permissions])
        db.commit()

        # --- Assign Roles to Users ---
        if admin_user and admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
        else:
             print(f"'{admin_role.name}' role already assigned to '{admin_user.username}' or user/role missing.")

        if guest_user and guest_role not in guest_user.roles:
            guest_user.roles.append(guest_role)
        else:
            print(f"'{guest_user.name}' role already assigned to '{guest_user.username}' or user/role missing.")
        db.commit() 

        print("\nDatabase seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"\nError during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Drop tables
    print("Dropping tables...")
    Base.metadata.drop_all(bind=engine)

    # Create tables
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)

    # Seed data
    seed_data()

