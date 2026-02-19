from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status


@dataclass(frozen=True)
class UserContext:
    user_id: str
    scopes: set[str]


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_scopes: str | None = Header(default=None, alias="X-Scopes"),
) -> UserContext:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user identity",
        )

    scopes = {scope.strip() for scope in (x_scopes or "").split(",") if scope.strip()}
    return UserContext(user_id=x_user_id, scopes=scopes)


def check_scope(required_scope: str):
    def _validator(user: UserContext = Depends(get_current_user)) -> UserContext:
        if required_scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}",
            )
        return user

    return _validator
