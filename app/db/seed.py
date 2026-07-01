"""Seeds the small set of default categories every account starts with,
so transactions can be created without a separate category-management
flow (out of scope for Part 4)."""

from sqlalchemy.orm import Session

from app.models.category import Category

DEFAULT_CATEGORIES = [
    ("Groceries", "#2E86DE", "shopping-cart"),
    ("Dining out", "#E67E22", "utensils"),
    ("Transport", "#16A085", "bus"),
    ("Rent & utilities", "#8E44AD", "home"),
    ("Subscriptions", "#2C3E50", "repeat"),
    ("Salary", "#27AE60", "briefcase"),
    ("Entertainment", "#C0392B", "film"),
    ("Uncategorised", "#7F8C8D", "tag"),
]


def seed_default_categories(db: Session) -> None:
    existing = {c.name for c in db.query(Category).filter(Category.is_default.is_(True)).all()}
    for name, colour, icon in DEFAULT_CATEGORIES:
        if name not in existing:
            db.add(Category(name=name, colour=colour, icon=icon, is_default=True))
    db.commit()
