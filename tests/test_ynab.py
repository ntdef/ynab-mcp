import json

import httpx
import pytest
import respx

from src.ynab_mcp.ynab import YNABClient


@pytest.fixture
def client():
    return YNABClient(api_token="test-token")


@pytest.mark.asyncio
@respx.mock
async def test_get_budgets(client):
    """Test that get_budgets calls the YNAB API with the correct path."""
    route = respx.get("https://api.ynab.com/v1/budgets").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "budgets": [
                        {
                            "id": "budget-id",
                            "name": "Test Budget",
                            "last_modified_on": "2023-01-01T00:00:00+00:00",
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_budgets()

    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"
    assert "budgets" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_accounts(client):
    """Test that get_accounts calls the YNAB API with the correct path."""
    route = respx.get("https://api.ynab.com/v1/budgets/budget-id/accounts").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "accounts": [
                        {
                            "id": "account-id",
                            "name": "Test Account",
                            "type": "checking",
                            "balance": 10000,
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_accounts("budget-id")

    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"
    assert "accounts" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_categories(client):
    """Test that get_categories calls the YNAB API with the correct path."""
    route = respx.get("https://api.ynab.com/v1/budgets/budget-id/categories").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "category_groups": [
                        {
                            "id": "group-id",
                            "name": "Immediate Obligations",
                            "categories": [
                                {
                                    "id": "category-id",
                                    "name": "Rent/Mortgage",
                                    "budgeted": 100000,
                                    "activity": -100000,
                                    "balance": 0,
                                }
                            ],
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_categories("budget-id")

    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"
    assert "category_groups" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_transactions_without_filters(client):
    """Test that get_transactions without filters calls the YNAB API correctly."""
    route = respx.get("https://api.ynab.com/v1/budgets/budget-id/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "transactions": [
                        {
                            "id": "transaction-id",
                            "date": "2023-01-01",
                            "amount": -1000,
                            "payee_name": "Test Payee",
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_transactions("budget-id", limit=10)

    assert route.called
    # Check that limit parameter was passed correctly
    url = str(route.calls[0].request.url)
    assert "limit=10" in url
    assert "transactions" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_transactions_with_account_filter(client):
    """Test that get_transactions with account filter calls the YNAB API correctly."""
    route = respx.get(
        "https://api.ynab.com/v1/budgets/budget-id/accounts/account-id/transactions"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "transactions": [
                        {
                            "id": "transaction-id",
                            "date": "2023-01-01",
                            "amount": -1000,
                            "account_id": "account-id",
                            "payee_name": "Test Payee",
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_transactions(
        budget_id="budget-id", account_id="account-id", since_date="2023-01-01"
    )

    assert route.called
    url = str(route.calls[0].request.url)
    assert "since_date=2023-01-01" in url
    assert "transactions" in response


@pytest.mark.asyncio
@respx.mock
async def test_get_transactions_with_category_filter(client):
    """Test that get_transactions with category filter calls the YNAB API correctly."""
    route = respx.get(
        "https://api.ynab.com/v1/budgets/budget-id/categories/category-id/transactions"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "transactions": [
                        {
                            "id": "transaction-id",
                            "date": "2023-01-01",
                            "amount": -1000,
                            "category_id": "category-id",
                            "payee_name": "Test Payee",
                        }
                    ]
                }
            },
        )
    )

    response = await client.get_transactions(
        budget_id="budget-id", category_id="category-id", since_date="2023-01-01"
    )

    assert route.called
    url = str(route.calls[0].request.url)
    assert "since_date=2023-01-01" in url
    assert "transactions" in response


@pytest.mark.asyncio
@respx.mock
async def test_create_transaction(client):
    """Test that create_transaction calls the YNAB API with the correct data."""
    route = respx.post("https://api.ynab.com/v1/budgets/budget-id/transactions").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "transaction": {
                        "id": "transaction-id",
                        "date": "2023-01-01",
                        "amount": -1000,
                        "payee_name": "Test Payee",
                    }
                }
            },
        )
    )

    response = await client.create_transaction(
        budget_id="budget-id",
        account_id="account-id",
        date="2023-01-01",
        amount=-1000,
        payee_name="Test Payee",
        category_id="category-id",
        memo="Test memo",
    )

    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"

    request_body = route.calls[0].request.content.decode("utf-8")
    request_json = json.loads(request_body)

    assert request_json["transaction"]["account_id"] == "account-id"
    assert request_json["transaction"]["date"] == "2023-01-01"
    assert request_json["transaction"]["amount"] == -1000
    assert request_json["transaction"]["payee_name"] == "Test Payee"
    assert request_json["transaction"]["category_id"] == "category-id"
    assert request_json["transaction"]["memo"] == "Test memo"

    assert "transaction" in response


@pytest.mark.asyncio
@respx.mock
async def test_create_category(client):
    """Test that create_category calls the YNAB API with the correct data."""
    route = respx.post(
        "https://api.ynab.com/v1/budgets/budget-id/categories/group-id/categories"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "category": {
                        "id": "new-category-id",
                        "name": "New Category",
                        "group_id": "group-id",
                        "budgeted": 0,
                        "activity": 0,
                        "balance": 0,
                    }
                }
            },
        )
    )

    response = await client.create_category(
        budget_id="budget-id", group_id="group-id", name="New Category"
    )

    assert route.called

    request_body = route.calls[0].request.content.decode("utf-8")
    request_json = json.loads(request_body)

    assert request_json["category"]["name"] == "New Category"

    assert "category" in response
    assert response["category"]["name"] == "New Category"


@pytest.mark.asyncio
@respx.mock
async def test_update_category_budgeted(client):
    """Test that update_category_budgeted calls the YNAB API with the correct data."""
    route = respx.patch(
        "https://api.ynab.com/v1/budgets/budget-id/months/2023-05/categories/category-id"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "category": {
                        "id": "category-id",
                        "name": "Test Category",
                        "budgeted": 50000,  # 50 dollars as milliunits
                        "activity": 0,
                        "balance": 50000,
                    }
                }
            },
        )
    )

    response = await client.update_category_budgeted(
        budget_id="budget-id",
        category_id="category-id",
        month="2023-05",
        amount=50000,
    )

    assert route.called

    request_body = route.calls[0].request.content.decode("utf-8")
    request_json = json.loads(request_body)

    assert request_json["category"]["budgeted"] == 50000

    assert "category" in response
    assert response["category"]["budgeted"] == 50000


@pytest.mark.asyncio
@respx.mock
async def test_update_transaction(client):
    """Test that update_transaction calls the YNAB API with the correct data."""
    route = respx.put(
        "https://api.ynab.com/v1/budgets/budget-id/transactions/transaction-id"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "transaction": {
                        "id": "transaction-id",
                        "date": "2023-01-15",
                        "amount": -2500,
                        "payee_name": "Updated Payee",
                        "category_id": "new-category-id",
                        "memo": "Updated memo",
                        "cleared": "cleared",
                    }
                }
            },
        )
    )

    response = await client.update_transaction(
        budget_id="budget-id",
        transaction_id="transaction-id",
        date="2023-01-15",
        amount=-2500,
        payee_name="Updated Payee",
        category_id="new-category-id",
        memo="Updated memo",
        cleared="cleared",
    )

    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"

    request_body = route.calls[0].request.content.decode("utf-8")
    request_json = json.loads(request_body)

    assert request_json["transaction"]["date"] == "2023-01-15"
    assert request_json["transaction"]["amount"] == -2500
    assert request_json["transaction"]["payee_name"] == "Updated Payee"
    assert request_json["transaction"]["category_id"] == "new-category-id"
    assert request_json["transaction"]["memo"] == "Updated memo"
    assert request_json["transaction"]["cleared"] == "cleared"

    assert "transaction" in response
    assert response["transaction"]["id"] == "transaction-id"


@pytest.mark.asyncio
@respx.mock
async def test_get_budget_summary_without_month(client):
    """Test that get_budget_summary without month specification calls the YNAB API correctly."""
    route = respx.get("https://api.ynab.com/v1/budgets/budget-id").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "budget": {
                        "id": "budget-id",
                        "name": "My Budget",
                        "last_modified_on": "2023-05-15T12:34:56+00:00",
                        "currency_format": {"iso_code": "USD"},
                        "accounts": [],
                        "months": [],
                    }
                }
            },
        )
    )

    response = await client.get_budget_summary("budget-id")

    assert route.called
    assert "budget" in response
    assert response["budget"]["name"] == "My Budget"


@pytest.mark.asyncio
@respx.mock
async def test_get_budget_summary_with_month(client):
    """Test that get_budget_summary with month specification calls the YNAB API correctly."""
    route = respx.get("https://api.ynab.com/v1/budgets/budget-id/months/2023-05").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "month": {
                        "month": "2023-05-01",
                        "income": 500000,
                        "budgeted": 450000,
                        "activity": -400000,
                        "to_be_budgeted": 50000,
                        "categories": [],
                    }
                }
            },
        )
    )

    response = await client.get_budget_summary("budget-id", "2023-05")

    assert route.called
    assert "month" in response
    assert response["month"]["month"] == "2023-05-01"
