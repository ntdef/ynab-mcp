from typing import Any, Dict, Optional

import httpx

from .config import config


class YNABClient:
    """Client for interacting with the YNAB API."""

    def __init__(self, api_token: str = None, base_url: str = None):
        """Initialize the YNAB API client.

        Args:
            api_token: YNAB API token. Defaults to the one in the config.
            base_url: YNAB API base URL. Defaults to the one in the config.
        """
        self.api_token = api_token or config.YNAB_API_TOKEN
        self.base_url = base_url or config.YNAB_API_BASE_URL

    async def _request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make a request to the YNAB API.

        Args:
            method: HTTP method to use.
            path: API path to request.
            params: Query parameters.
            json: JSON body.

        Returns:
            Response data.
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                params=params,
                json=json,
                timeout=10.0,
            )

            response.raise_for_status()
            result = response.json()
            return result["data"]

    async def get_budgets(self) -> Dict[str, Any]:
        """Get a list of budgets.

        Returns:
            Dictionary of budgets.
        """
        return await self._request("GET", "/budgets")

    async def get_accounts(self, budget_id: str) -> Dict[str, Any]:
        """Get a list of accounts for a budget.

        Args:
            budget_id: The ID of the budget to get accounts for.

        Returns:
            Dictionary of accounts.
        """
        return await self._request("GET", f"/budgets/{budget_id}/accounts")

    async def get_categories(self, budget_id: str) -> Dict[str, Any]:
        """Get a list of categories for a budget.

        Args:
            budget_id: The ID of the budget to get categories for.

        Returns:
            Dictionary of categories.
        """
        return await self._request("GET", f"/budgets/{budget_id}/categories")

    async def create_category(
        self, budget_id: str, group_id: str, name: str
    ) -> Dict[str, Any]:
        """Create a new category in the specified budget group.

        Args:
            budget_id: The ID of the budget.
            group_id: The ID of the category group.
            name: The name of the new category.

        Returns:
            Dictionary with information about the new category.
        """
        payload = {"category": {"name": name}}
        return await self._request(
            "POST",
            f"/budgets/{budget_id}/categories/{group_id}/categories",
            json=payload,
        )

    async def get_transactions(
        self,
        budget_id: str,
        since_date: Optional[str] = None,
        account_id: Optional[str] = None,
        category_id: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get a list of transactions for a budget.

        Args:
            budget_id: The ID of the budget to get transactions for.
            since_date: Optional date filter (YYYY-MM-DD format).
            account_id: Optional account ID filter.
            category_id: Optional category ID filter.
            limit: Maximum number of transactions to return.

        Returns:
            Dictionary of transactions.
        """
        params = {}

        if since_date:
            params["since_date"] = since_date

        if account_id:
            return await self._request(
                "GET",
                f"/budgets/{budget_id}/accounts/{account_id}/transactions",
                params=params,
            )

        if category_id:
            return await self._request(
                "GET",
                f"/budgets/{budget_id}/categories/{category_id}/transactions",
                params=params,
            )

        params["limit"] = limit
        return await self._request(
            "GET", f"/budgets/{budget_id}/transactions", params=params
        )

    async def create_transaction(
        self,
        budget_id: str,
        account_id: str,
        date: str,
        amount: int,
        payee_name: str,
        category_id: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new transaction in the specified budget.

        Args:
            budget_id: The ID of the budget.
            account_id: The ID of the account.
            date: Transaction date (YYYY-MM-DD format).
            amount: Transaction amount (negative for outflow, positive for inflow).
                   Amount is in milliunits (1000 = $1.00).
            payee_name: Name of the payee.
            category_id: Optional category ID.
            memo: Optional memo for the transaction.

        Returns:
            Dictionary with information about the new transaction.
        """
        transaction = {
            "account_id": account_id,
            "date": date,
            "amount": amount,
            "payee_name": payee_name,
        }

        if category_id:
            transaction["category_id"] = category_id

        if memo:
            transaction["memo"] = memo

        payload = {"transaction": transaction}
        return await self._request(
            "POST", f"/budgets/{budget_id}/transactions", json=payload
        )

    async def update_transaction(
        self,
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
        """Update an existing transaction in the specified budget.

        Args:
            budget_id: The ID of the budget.
            transaction_id: The ID of the transaction to update.
            account_id: Optional account ID to update.
            date: Optional transaction date (YYYY-MM-DD format) to update.
            amount: Optional transaction amount to update in milliunits (negative for outflow, positive for inflow).
            payee_name: Optional payee name to update.
            category_id: Optional category ID to update.
            memo: Optional memo to update.
            cleared: Optional cleared status to update ('cleared', 'uncleared', or 'reconciled').

        Returns:
            Dictionary with information about the updated transaction.
        """
        transaction = {}

        if account_id:
            transaction["account_id"] = account_id

        if date:
            transaction["date"] = date

        if amount is not None:
            transaction["amount"] = amount

        if payee_name:
            transaction["payee_name"] = payee_name

        if category_id:
            transaction["category_id"] = category_id

        if memo is not None:
            transaction["memo"] = memo

        if cleared:
            transaction["cleared"] = cleared

        payload = {"transaction": transaction}
        return await self._request(
            "PUT", f"/budgets/{budget_id}/transactions/{transaction_id}", json=payload
        )

    async def get_budget_summary(
        self, budget_id: str, month: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a summary of the budget for a specific month.

        Args:
            budget_id: The ID of the budget.
            month: Month in YYYY-MM format. Defaults to current month.

        Returns:
            Dictionary with budget summary.
        """
        if month:
            return await self._request("GET", f"/budgets/{budget_id}/months/{month}")

        return await self._request("GET", f"/budgets/{budget_id}")

    async def update_category_budgeted(
        self, budget_id: str, category_id: str, month: str, amount: int
    ) -> Dict[str, Any]:
        """Update the budgeted amount for a category in a specific month.

        Args:
            budget_id: The ID of the budget.
            category_id: The ID of the category.
            month: Month in YYYY-MM format.
            amount: Budgeted amount to set.
                   Amount is in milliunits (1000 = $1.00).

        Returns:
            Dictionary with updated category information.
        """
        payload = {"category": {"budgeted": amount}}
        return await self._request(
            "PATCH",
            f"/budgets/{budget_id}/months/{month}/categories/{category_id}",
            json=payload,
        )
