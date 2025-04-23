"""
YNAB MCP Server - Main entry point
"""

from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP

from ynab_mcp.config import config
from ynab_mcp.ynab import YNABClient

ynab = YNABClient()
mcp = FastMCP(name="ynab")


@mcp.tool()
async def get_budgets(ctx: Context) -> Dict[str, Any]:
    """
    Retrieve all budgets for the authenticated user.

    Returns:
        Dictionary with budget data (all amounts in milliunits)
    """
    ctx.info("Retrieving budgets...")
    return await ynab.get_budgets()


@mcp.tool()
async def get_accounts(ctx: Context, budget_id: str):
    """
    Retrieve all accounts for a specific budget.

    Args:
        budget_id: The budget ID to fetch accounts for

    Returns:
        Dictionary with account data (all amounts in milliunits)
    """
    ctx.info(f"Retrieving accounts for budget {budget_id}...")
    return await ynab.get_accounts(budget_id)


@mcp.tool()
async def get_categories(ctx: Context, budget_id: str) -> Dict[str, Any]:
    """
    Retrieve all categories for a specific budget.

    Args:
        budget_id: The budget ID to fetch categories for

    Returns:
        Dictionary with category data (all amounts in milliunits)
    """
    ctx.info(f"Retrieving categories for budget {budget_id}...")
    return await ynab.get_categories(budget_id)


@mcp.tool()
async def get_transactions(
    ctx: Context,
    budget_id: str,
    since_date: Optional[str] = None,
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve transactions for a specific budget, optionally filtered by date,
    account, or category.

    Args:
        budget_id: The budget ID to fetch transactions for
        since_date: Optional date filter in YYYY-MM-DD format
        account_id: Optional account ID filter
        category_id: Optional category ID filter
        limit: Maximum number of transactions to return (default: 20)

    Returns:
        Dictionary with transaction data (all amounts in milliunits)
    """
    ctx.info(f"Retrieving transactions for budget {budget_id}...")

    filters = []
    if since_date:
        filters.append(f"since {since_date}")
    if account_id:
        filters.append(f"for account {account_id}")
    if category_id:
        filters.append(f"in category {category_id}")
    if filters:
        ctx.info(f"Applying filters: {', '.join(filters)}")

    return await ynab.get_transactions(
        budget_id, since_date, account_id, category_id, limit
    )


@mcp.tool()
async def create_transaction(
    ctx: Context,
    budget_id: str,
    account_id: str,
    date: str,
    amount: int,
    payee_name: str,
    category_id: Optional[str] = None,
    memo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new transaction in the specified budget.

    Args:
        budget_id: The budget ID
        account_id: The account ID
        date: Transaction date in YYYY-MM-DD format
        amount: Transaction amount in milliunits (1000 = $1.00, with negative for outflow and positive for inflow)
        payee_name: Name of the payee
        category_id: Optional category ID
        memo: Optional memo for the transaction

    Returns:
        Dictionary with success status and transaction info (amounts in milliunits)
    """
    ctx.info(f"Creating transaction of {amount} for {payee_name}...")

    return await ynab.create_transaction(
        budget_id, account_id, date, amount, payee_name, category_id, memo
    )


@mcp.tool()
async def create_category(
    ctx: Context, budget_id: str, group_id: str, name: str
) -> Dict[str, Any]:
    """
    Create a new category in the specified budget group.

    Args:
        budget_id: The budget ID
        group_id: The category group ID
        name: Name of the new category

    Returns:
        Dictionary with success status and category info
    """
    ctx.info(f"Creating category '{name}' in group {group_id}...")

    return await ynab.create_category(budget_id, group_id, name)


@mcp.tool()
async def update_category_budgeted(
    ctx: Context, budget_id: str, category_id: str, month: str, amount: int
) -> Dict[str, Any]:
    """
    Update the budgeted amount for a category in a specific month.

    Args:
        budget_id: The budget ID
        category_id: The category ID
        month: Month in YYYY-MM format
        amount: Budgeted amount to set in milliunits

    Returns:
        Dictionary with success status and updated category info (amounts in milliunits)
    """
    ctx.info(f"Updating budget for category {category_id} to {amount}...")
    return await ynab.update_category_budgeted(budget_id, category_id, month, amount)


@mcp.tool()
async def get_budget_summary(
    ctx: Context, budget_id: str, month: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a summary of the budget, optionally for a specific month.

    Args:
        budget_id: The budget ID
        month: Optional month in YYYY-MM format (defaults to current month)

    Returns:
        Dictionary with budget summary information (all amounts in milliunits)
    """
    if month:
        ctx.info(f"Retrieving budget summary for {month}...")
    else:
        ctx.info("Retrieving overall budget summary...")

    return await ynab.get_budget_summary(budget_id, month)


@mcp.tool()
async def update_transaction(
    ctx: Context,
    budget_id: str,
    transaction_id: str,
    account_id: Optional[str] = None,
    date: Optional[str] = None,
    amount: Optional[int] = None,
    payee_name: Optional[str] = None,
    category_id: Optional[str] = None,
    memo: Optional[str] = None,
    cleared: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing transaction in the specified budget.

    Args:
        budget_id: The budget ID
        transaction_id: The ID of the transaction to update
        account_id: Optional account ID to update
        date: Optional transaction date in YYYY-MM-DD format
        amount: Optional transaction amount (negative for outflow, positive for inflow)
        payee_name: Optional payee name to update
        category_id: Optional category ID to update
        memo: Optional memo to update
        cleared: Optional cleared status ('cleared', 'uncleared', or 'reconciled')

    Returns:
        Dictionary with updated transaction info (amounts in milliunits)
    """
    ctx.info(f"Updating transaction {transaction_id}...")

    fields_to_update = []
    if account_id:
        fields_to_update.append("account")
    if date:
        fields_to_update.append("date")
    if amount is not None:
        fields_to_update.append("amount")
    if payee_name:
        fields_to_update.append("payee")
    if category_id:
        fields_to_update.append("category")
    if memo is not None:
        fields_to_update.append("memo")
    if cleared:
        fields_to_update.append("cleared status")

    if fields_to_update:
        ctx.info(f"Updating fields: {', '.join(fields_to_update)}")

    return await ynab.update_transaction(
        budget_id,
        transaction_id,
        account_id,
        date,
        amount,
        payee_name,
        category_id,
        memo,
        cleared,
    )


def main():
    config.validate()
    mcp.run()


if __name__ == "__main__":
    main()
