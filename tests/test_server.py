import pytest
import pytest_asyncio
from fastmcp import Client

from ynab_mcp.server import mcp


def find_tool(tools, name):
    """Find tool in tools list."""
    return next(t for t in tools if t.name == name)


def assert_contains(a, b):
    """Check if dictionary a contains all items from dictionary b."""
    for key, value in b.items():
        assert key in a
        if isinstance(value, dict):
            assert isinstance(a[key], dict)
            for k, v in value.items():
                assert k in a[key]
                assert a[key][k] == v
        else:
            assert a[key] == value


@pytest_asyncio.fixture
async def tools():
    async with Client(mcp) as client:
        return await client.list_tools()


@pytest.mark.asyncio
async def test_list_tools(tools):
    expected = set(
        """
    create_category
    create_transaction
    get_accounts
    get_budget_summary
    get_budgets
    get_categories
    get_transactions
    update_category_budgeted
    update_transaction
    """.split()
    )
    assert expected == set(t.name for t in tools)


@pytest.mark.asyncio
async def test_get_accounts(tools):
    get_accounts_tool = find_tool(tools, "get_accounts")
    get_accounts_tool_schema = get_accounts_tool.inputSchema

    assert set(get_accounts_tool_schema["required"]) == {"budget_id"}

    assert_contains(
        get_accounts_tool_schema["properties"],
        {"budget_id": {"title": "Budget Id", "type": "string"}},
    )


@pytest.mark.asyncio
async def test_get_budgets(tools):
    get_budgets_tool = find_tool(tools, "get_budgets")
    get_budgets_tool_schema = get_budgets_tool.inputSchema

    assert (
        "required" not in get_budgets_tool_schema
        or not get_budgets_tool_schema["required"]
    )

    assert (
        "properties" not in get_budgets_tool_schema
        or not get_budgets_tool_schema["properties"]
    )


@pytest.mark.asyncio
async def test_get_categories(tools):
    get_categories_tool = find_tool(tools, "get_categories")
    get_categories_tool_schema = get_categories_tool.inputSchema

    # budget_id is required
    assert set(get_categories_tool_schema["required"]) == {"budget_id"}
    # budget_id is an argument of type string
    assert_contains(
        get_categories_tool_schema["properties"],
        {"budget_id": {"title": "Budget Id", "type": "string"}},
    )


@pytest.mark.asyncio
async def test_get_transactions(tools):
    get_transactions_tool = find_tool(tools, "get_transactions")
    get_transactions_tool_schema = get_transactions_tool.inputSchema

    assert set(get_transactions_tool_schema["required"]) == {"budget_id"}

    properties = get_transactions_tool_schema["properties"]
    assert properties["budget_id"]["type"] == "string"
    assert properties["budget_id"]["title"] == "Budget Id"

    assert "anyOf" in properties["since_date"]
    assert "anyOf" in properties["account_id"]
    assert "anyOf" in properties["category_id"]

    assert properties["limit"]["default"] == 20
    assert properties["limit"]["type"] == "integer"


@pytest.mark.asyncio
async def test_create_transaction(tools):
    create_transaction_tool = find_tool(tools, "create_transaction")
    create_transaction_tool_schema = create_transaction_tool.inputSchema

    required_fields = {"budget_id", "account_id", "date", "amount", "payee_name"}
    assert set(create_transaction_tool_schema["required"]) == required_fields

    properties = create_transaction_tool_schema["properties"]

    assert properties["budget_id"]["type"] == "string"
    assert properties["account_id"]["type"] == "string"
    assert properties["date"]["type"] == "string"
    assert properties["amount"]["type"] == "integer"
    assert properties["payee_name"]["type"] == "string"

    assert "anyOf" in properties["category_id"]
    assert "anyOf" in properties["memo"]


@pytest.mark.asyncio
async def test_create_category(tools):
    create_category_tool = find_tool(tools, "create_category")
    create_category_tool_schema = create_category_tool.inputSchema

    required_fields = {"budget_id", "group_id", "name"}
    assert set(create_category_tool_schema["required"]) == required_fields

    assert_contains(
        create_category_tool_schema["properties"],
        {
            "budget_id": {"title": "Budget Id", "type": "string"},
            "group_id": {"title": "Group Id", "type": "string"},
            "name": {"title": "Name", "type": "string"},
        },
    )


@pytest.mark.asyncio
async def test_update_category_budgeted(tools):
    update_category_tool = find_tool(tools, "update_category_budgeted")
    update_category_tool_schema = update_category_tool.inputSchema

    required_fields = {"budget_id", "category_id", "month", "amount"}
    assert set(update_category_tool_schema["required"]) == required_fields

    assert_contains(
        update_category_tool_schema["properties"],
        {
            "budget_id": {"title": "Budget Id", "type": "string"},
            "category_id": {"title": "Category Id", "type": "string"},
            "month": {"title": "Month", "type": "string"},
            "amount": {"title": "Amount", "type": "integer"},
        },
    )


@pytest.mark.asyncio
async def test_get_budget_summary(tools):
    get_budget_summary_tool = find_tool(tools, "get_budget_summary")
    get_budget_summary_tool_schema = get_budget_summary_tool.inputSchema

    required_fields = {"budget_id"}
    assert set(get_budget_summary_tool_schema["required"]) == required_fields

    properties = get_budget_summary_tool_schema["properties"]

    assert properties["budget_id"]["type"] == "string"
    assert properties["budget_id"]["title"] == "Budget Id"

    assert "anyOf" in properties["month"]
    assert properties["month"]["title"] == "Month"


@pytest.mark.asyncio
async def test_update_transaction(tools):
    update_transaction_tool = find_tool(tools, "update_transaction")
    update_transaction_tool_schema = update_transaction_tool.inputSchema

    required_fields = {"budget_id", "transaction_id"}
    assert set(update_transaction_tool_schema["required"]) == required_fields

    properties = update_transaction_tool_schema["properties"]

    assert properties["budget_id"]["type"] == "string"
    assert properties["transaction_id"]["type"] == "string"

    assert "anyOf" in properties["account_id"]
    assert "anyOf" in properties["date"]
    assert "anyOf" in properties["amount"]
    assert "anyOf" in properties["payee_name"]
    assert "anyOf" in properties["category_id"]
    assert "anyOf" in properties["memo"]
    assert "anyOf" in properties["cleared"]


@pytest.mark.asyncio
async def test_docstrings_match_tools(tools):
    """Test that the docstrings in the tools match the actual implementations."""
    for tool in tools:
        # Check that the tool has a description
        assert tool.description, f"Tool {tool.name} has no description"

        # Check that required parameters are documented in Args section
        if "required" in tool.inputSchema:
            for param in tool.inputSchema["required"]:
                assert (
                    f"{param}:" in tool.description
                ), f"Required parameter {param} not documented in {tool.name}"

        # Check that all properties are documented
        if "properties" in tool.inputSchema:
            for param in tool.inputSchema["properties"]:
                assert (
                    f"{param}:" in tool.description
                ), f"Parameter {param} not documented in {tool.name}"
