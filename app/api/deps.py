import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import api_error
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise api_error(401, "unauthorized", "Authentication required")

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise api_error(401, "invalid_token", "Access token has expired")
    except jwt.InvalidTokenError:
        raise api_error(401, "invalid_token", "Access token is invalid")

    user = db.get(User, uuid.UUID(user_id))
    if user is None:
        raise api_error(401, "unauthorized", "Authentication required")
    if user.status != "active":
        raise api_error(403, "forbidden", "This account has been suspended")
    return user
