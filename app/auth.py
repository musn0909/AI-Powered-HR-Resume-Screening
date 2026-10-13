
from typing import Annotated

from fastapi import (
    APIRouter, Depends, HTTPException, status
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

DbSession = Annotated[Session, Depends(get_db)]


# REGISTER
@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=201
)
def register(
    data: schemas.UserRegister,
    db: DbSession
):
    email = str(data.email).lower()

    existing = db.scalar(
        select(models.User).where(
            models.User.email == email
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = models.User(
        email=email,
        hashed_password=hash_password(data.password),
        role="candidate",
        is_active=1
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    db.refresh(user)
    return user


# LOGIN
@router.post(
    "/login",
    response_model=schemas.Token
)
def login(
    form: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: DbSession
):
    email = form.username.lower()

    user = db.scalar(
        select(models.User).where(
            models.User.email == email
        )
    )

    if (
        user is None
        or not verify_password(
            form.password,
            user.hashed_password
        )
        or not user.is_active
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# AUTHENTICATION DEPENDENCY
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession
):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    user_id = decode_access_token(token)

    if user_id is None:
        raise unauthorized

    user = db.get(models.User, user_id)

    if user is None or not user.is_active:
        raise unauthorized

    return user


# ROLE AUTHORIZATION DEPENDENCY
def require_roles(*allowed_roles: str):
    def role_checker(
        user: Annotated[
            models.User,
            Depends(get_current_user)
        ]
    ):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return user

    return role_checker


# LOGGED-IN USER
@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def read_me(
    user: Annotated[
        models.User,
        Depends(get_current_user)
    ]
):
    return user


# ADMIN ONLY
@router.get("/admin-only")
def admin_only(
    user: Annotated[
        models.User,
        Depends(require_roles("admin"))
    ]
):
    return {
        "message": "Welcome, administrator",
        "email": user.email
    }


# HR OR ADMIN
@router.get("/hr-dashboard")
def hr_dashboard(
    user: Annotated[
        models.User,
        Depends(require_roles("hr", "admin"))
    ]
):
    return {
        "message": "HR dashboard access granted",
        "role": user.role
    }
