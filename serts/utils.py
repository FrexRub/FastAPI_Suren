import jwt

from core.config import setting


def encode_jwt(
        payload: dict,
        private_key: str = setting.auth_jwt.private_key_path.read_text(),
        algorithm: str = setting.auth_jwt.algorithm,
):
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = setting.auth_jwt.public_key_path.read_text(),
        algorithm: str = setting.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded
