# YNAB MCP Server

A Model Context Protocol (MCP) server for interacting with YNAB (You Need A Budget) via their API. 

## Features

- Get budgets, accounts, and categories
- Get, create and update transactions
- Create new categories
- Update budgeted amounts for categories
- Get budget summaries

## Prerequisites

- Python 3.13 or higher
- A YNAB account with an API token ([Get your token here](https://app.ynab.com/settings/developer))
- UV package manager (optional but recommended)

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/ntdef/ynab-mcp.git
   cd ynab-mcp
   ```

2. Create a virtual environment
   ```bash
   uv venv
   ```

3. Activate the virtual environment
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```

4. Install dependencies using UV
   ```bash
   # python -m pip install uv
   uv sync
   ```

5. Copy `.env.example` to `.env` and add your YNAB API token
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor
   ```

## Usage

### Running the server

```bash
uv run ynab-mcp
```

The server will start in stdio mode, so you won't see any output.

### Available tools

The YNAB MCP Server provides the following tools:

#### Budget management
- `get_budgets`: Retrieve all budgets for the authenticated user
- `get_budget_summary`: Get a summary of the budget, optionally for a specific month

#### Account management
- `get_accounts`: Retrieve all accounts for a specific budget

#### Category management
- `get_categories`: Retrieve all categories for a specific budget
- `create_category`: Create a new category in the specified budget group
- `update_category_budgeted`: Update the budgeted amount for a category in a specific month

#### Transaction management
- `get_transactions`: Retrieve transactions for a specific budget, optionally filtered by date, account, or category
- `create_transaction`: Create a new transaction in the specified budget
- `update_transaction`: Update one or more fields of a specific transaction

## Development

### Running tests

```bash
uv run pytest
```

### Code style

This project uses Black and isort for code formatting. To format your code:

```bash
uv run isort src tests
uv run black src tests
```

## License

MIT License

## Acknowledgements

- Some of the code was written with the assistance of [aider](https://aider.chat/)
- [YNAB API Documentation](https://api.ynab.com/)
- [fastmcp](https://github.com/anthropics/fastmcp) by Anthropic
