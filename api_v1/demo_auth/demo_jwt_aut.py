from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (HTTPBearer, HTTPAuthorizationCredentials,
                              OAuth2PasswordBearer)
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from users.schemas import UserSchema
from auth import utils as auth_utils


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


router = APIRouter(prefix="/jwt", tags=["JWT"])

john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
)

sam = UserSchema(
    username="sam",
    password=auth_utils.hash_password("secret"),
)

user_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}

# http_bearer = HTTPBearer()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/v1/jwt/login")


def validate_auth_user(
        username: str = Form(),
        password: str = Form(),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    if not (user := user_db.get(username)):
        raise unauthed_exc

    if not auth_utils.validate_password(
            password=password,
            hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive"
        )

    return user


def get_current_token_payload(
        token: str = Depends(oauth2_schema),
        # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    # token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error exception: {exc}"
        )
    else:
        return payload


def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload),
) -> UserSchema:
    username: str = payload.get("sub")
    if not (user := user_db.get(username)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token invalid"
        )
    return user


def get_current_active_auth_user(
        user: UserSchema = Depends(get_current_auth_user)
):
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive"
        )
    return user


@router.post("/login", response_model=TokenInfo)
def auth_user_issue_jwt(
        user: UserSchema = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


@router.get("/users/me/")
def auth_user_check_self_info(
        payload: dict = Depends(get_current_token_payload),
        user: UserSchema = Depends(get_current_active_auth_user)
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "login_in_at": iat,
    }
