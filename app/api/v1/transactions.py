"""The two graded Part 4 endpoints: create and list/filter transactions
for the Personal Ledger feature."""

import math
from datetime import date as date_type
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.errors import api_error
from app.db.session import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionListResponse, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = (
        db.query(Category)
        .filter(
            Category.id == payload.category_id,
            or_(Category.is_default.is_(True), Category.user_id == current_user.id),
        )
        .first()
    )
    if category is None:
        raise api_error(404, "not_found", "Category not found")

    transaction = Transaction(
        user_id=current_user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        type=payload.type,
        date=payload.date,
        vendor=payload.vendor,
        payment_method=payload.payment_method,
        note=payload.note,
        receipt_url=payload.receipt_url,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    transaction.category = category
    return transaction


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
    category_id: str | None = Query(default=None),
    vendor: str | None = Query(default=None),
    q: str | None = Query(default=None),
    min_amount: Decimal | None = Query(default=None),
    max_amount: Decimal | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    if date_from and date_to and date_from > date_to:
        raise api_error(400, "validation_error", "date_from must be before date_to")

    query = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.user_id == current_user.id)
    )

    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if vendor:
        query = query.filter(Transaction.vendor.ilike(f"%{vendor}%"))
    if q:
        query = query.filter(
            or_(Transaction.vendor.ilike(f"%{q}%"), Transaction.note.ilike(f"%{q}%"))
        )
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    total_items = query.count()
    items = (
        query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=max(1, math.ceil(total_items / page_size)),
    )
