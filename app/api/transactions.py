"""
transactions.py - REST endpoints for querying transaction history and individual audit records.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.transaction import TransactionListResponse, TransactionRecord
from app.services.db_service import get_db_service

router = APIRouter(prefix="/transactions", tags=["Transaction Audit Explorer"])


@router.get("", response_model=TransactionListResponse, summary="Query paginated transactions")
async def list_transactions(
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    risk_tier: Optional[str] = Query(None, description="Filter by LOW, MODERATE, HIGH or ALL"),
    search: Optional[str] = Query(None, description="Search by UPI ID or transaction reference"),
):
    """
    Returns authentic transaction history stored in the database with search and risk-tier filtering.
    """
    try:
        db = get_db_service()
        result = db.get_transactions(
            limit=limit,
            offset=offset,
            risk_tier=risk_tier,
            search=search,
        )
        return {
            "items": result["items"],
            "total": result["total"],
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query transactions: {str(e)}"
        )


@router.get("/{tx_id}", response_model=TransactionRecord, summary="Retrieve single transaction audit record")
async def get_transaction(tx_id: str):
    """
    Retrieve single transaction by UUID or UPI reference, including full feature snapshot
    and explainability factors.
    """
    try:
        db = get_db_service()
        record = db.get_transaction_by_id(tx_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID/Ref '{tx_id}' not found."
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transaction: {str(e)}"
        )
