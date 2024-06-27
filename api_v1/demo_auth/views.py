from typing import Annotated
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }


username_to_passwords = {
    "admin": "admin",
    "john": "password",

}

static_auth_token_username = {
    "6d86d329004d7a5c84ba9493bb44cee77": "admin",
    "41fa8183f208e234291027d8781bb89": "john",
}


def get_auth_user_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    unauthed_exe = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = username_to_passwords.get(credentials.username)

    if correct_password is None:
        raise unauthed_exe

    # secret
    if not secrets.compare_digest(
            credentials.password.encode("utf-8"),
            correct_password.encode("utf-8"),
    ):
        raise unauthed_exe

    return credentials.username


def get_username_by_static_auth_token(
        static_token: str = Header(alias="x-auth-token"),
) -> str:
    if static_token not in static_auth_token_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{static_token} token invalid",
        )
    return static_auth_token_username[static_token]


@router.get("/basic-auth-username/")
def demo_basic_auth_username(
        auth_username: str = Depends(get_auth_user_username),
):
    return {
        "message": f"Hi {auth_username}!",
        "username": auth_username,
    }


@router.get("/some-http-header-auth/")
def demo_auth_some_http_header(
        username: str = Depends(get_username_by_static_auth_token),
):
    return {
        "message": f"Hi {username}!",
        "username": username,
    }


@router.get("/")
def hello():
    return "Hello, world!!!"
