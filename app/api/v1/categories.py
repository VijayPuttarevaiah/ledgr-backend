"""Supporting endpoint: lets a client fetch valid category_id values to
use when creating a transaction. Read-only, returns the default
categories seeded at startup (see app.db.seed)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = (
        db.query(Category)
        .filter((Category.is_default.is_(True)) | (Category.user_id == current_user.id))
        .order_by(Category.name)
        .all()
    )
    return categories
