import json

import config


def load_all_users(users_path=None) -> list[dict]:
    users_path = users_path or config.USERS_FILE
    return json.loads(users_path.read_text(encoding="utf-8"))


def load_user(user_id: str, users_path=None) -> dict:
    for user in load_all_users(users_path):
        if user["id"] == user_id:
            return user
    raise ValueError(f"no user with id {user_id}")
