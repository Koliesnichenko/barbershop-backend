from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.auth.dependencies import get_current_user, admin_required
from src.app.database import get_db
from src.app.auth.schemas import UserLogin, UserRegister, Token, UserUpdate
from src.app.models.user import User
from src.app.auth.security import hash_password, verify_password, create_access_token
import logging

router = APIRouter(tags=["Auth"])

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/register", status_code=201)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=data.email).first()
    if existing:
        logger.warning(f"Registration failed: user already exists - {data.email}")
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        phone_number=data.phone_number,
        role="user"
    )
    db.add(new_user)
    db.commit()
    logger.info(f"User registered successfully: {new_user.email} (id={new_user.id})")
    return {"message": "User created", "user_id": new_user.id}


@router.post("/login", response_model=Token)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning(f"Login failed for: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    logger.info(f"Login successful: {user.email} (id={user.id})")
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "role": current_user.role
    }


@router.put("/me")
def update_user_info(
        data: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    if data.email and data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exist"
            )
        current_user.email = data.email

    if data.phone_number:
        current_user.phone_number = data.phone_number

    db.commit()
    db.refresh(current_user)

    return {
        "message": "User profile updated",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
        }
    }


@router.post("/admin-only")
def admin_action(current_user: User = Depends(admin_required)):
    return {"message": f"Welcome, admin {current_user.name}"}


@router.get("/test-auth")
def test(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

