"""Authentication routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status

from llm_tracer.api.dependencies import get_current_user, require_auth
from llm_tracer.api.v1.schemas import LoginRequest, RegisterRequest, UserResponse
from llm_tracer.db.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(require_auth)):
    """Get current authenticated user."""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        is_admin=user["is_admin"],
    )


@router.post("/login")
async def login(request: Request, data: LoginRequest):
    """Authenticate user and create session."""
    user = await User.select().where(User.username == data.username).first()

    if not user or not User.verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    # Update last login
    await User.update({User.last_login: datetime.now()}).where(User.id == user["id"])

    # Set session
    user_data = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "is_admin": user["is_admin"],
    }
    request.session["user"] = user_data

    return {"user": user_data}


@router.post("/register")
async def register(request: Request, data: RegisterRequest):
    """Register a new user account."""
    # Check username
    existing = await User.select().where(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check email
    existing = await User.select().where(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        username=data.username,
        email=data.email,
        password_hash=User.hash_password(data.password),
    )
    await user.save()

    # Set session
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }
    request.session["user"] = user_data

    return {"user": user_data}


@router.post("/logout")
async def logout(request: Request):
    """Logout user and clear session."""
    request.session.clear()
    return {"message": "Logged out"}
