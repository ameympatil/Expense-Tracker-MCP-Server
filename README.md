# Expense Tracker MCP Server

A Model Context Protocol (MCP) server for tracking personal expenses. This server provides tools to add, list, and summarize expenses, utilizing a local SQLite database for storage.

## Features

- **Add Expenses**: Log expenses with details including amount, category, subcategory, date, and notes.
- **List Expenses**: Retrieve a list of expenses within a specified date range.
- **Summarize Expenses**: Generate summaries of expenses (total amount) grouped by category.
- **Categories Resource**: Access a comprehensive list of predefined expense categories.
- **Local Database**: All data is stored in a local `expenses.db` file.

## Prerequisites

- [Python](https://www.python.org/) 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory:

    ```bash
    cd "d:\Study\Expense Tracker MCP"
    ```

2.  **Install dependencies**:

    Using `uv`:
    ```bash
    uv sync
    ```

    Or using `pip`:
    ```bash
    pip install -e .
    ```

## Usage

### Running Locally

You can run the MCP server locally for testing or development.

Development mode (with auto-reload):
```bash
uv run fastmcp dev main.py
```

Production run:
```bash
uv run fastmcp run main.py
```

### Inspector

You can inspect and test the server tools using the MCP Inspector:

```bash
uv run fastmcp inspect main.py
```

### Integration with Claude Desktop

To use this Expense Tracker with Claude Desktop:

1.  Open your Claude Desktop configuration file:
    -   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    -   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

2.  Add the `expense-tracker` server to the `mcpServers` object. Make sure to use the **absolute path** to your `main.py` file.

    ```json
    {
      "mcpServers": {
        "expense-tracker": {
          "command": "uv",
          "args": [
            "run",
            "fastmcp",
            "run",
            "d:/Study/Expense Tracker MCP/main.py"
          ]
        }
      }
    }
    ```

3.  Restart Claude Desktop.

## Tools Available

### `add_expense`
Adds a new expense entry.
*   **Arguments**:
    *   `amount` (float): The cost of the expense.
    *   `category` (string): The category of the expense (see `categories` resource).
    *   `subcategory` (string, optional): A more specific classification.
    *   `note` (string, optional): Additional details.
    *   `date` (string, optional): Date of expense in `DD-MM-YYYY` format. Defaults to current date (IST) if omitted.

### `list_expenses`
Lists expenses within a date range.
*   **Arguments**:
    *   `start_date` (string): Start date in `DD-MM-YYYY` format.
    *   `end_date` (string): End date in `DD-MM-YYYY` format.

### `summarize`
Summarizes expenses by category.
*   **Arguments**:
    *   `start_date` (string): Start date in `DD-MM-YYYY` format.
    *   `end_date` (string): End date in `DD-MM-YYYY` format.
    *   `category` (string, optional): Filter by a specific category.

## Resources

### `expense://categories`
Returns the JSON content of the available expense categories.

## Project Structure

*   `main.py`: The core MCP server implementation.
*   `expenses.db`: SQLite database file (created automatically).
*   `categories.json`: specific categories configuration.
*   `pyproject.toml`: Project configuration and dependencies.

## Notes

*   **Date Format**: The system uses `DD-MM-YYYY` for date storage and querying.
*   **Timezone**: Default dates are calculated in Indian Standard Time (IST).
