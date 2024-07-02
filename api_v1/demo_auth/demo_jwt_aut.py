from users.schemas import UserSchema
from auth import utils as auth_utils

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

}
