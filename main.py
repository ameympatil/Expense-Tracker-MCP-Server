from fastmcp import FastMCP
import aiosqlite
import aiofiles
import os
import shutil
import tempfile
import asyncio
from datetime import datetime, timedelta, timezone

# Determine the database path
# 1. Prefer DB_DIR env var
# 2. Fallback to current directory if writable
# 3. Fallback to temp directory (for read-only cloud filesystems)
DB_NAME = "expenses.db"
BASE_DIR = os.path.dirname(__file__)

if os.getenv("DB_DIR"):
    DB_PATH = os.path.join(os.getenv("DB_DIR"), DB_NAME)
elif os.access(BASE_DIR, os.W_OK):
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)
else:
    temp_dir = tempfile.gettempdir()
    DB_PATH = os.path.join(temp_dir, DB_NAME)
    # If the database exists in the read-only source but not in temp, copy it
    source_db = os.path.join(BASE_DIR, DB_NAME)
    if os.path.exists(source_db) and not os.path.exists(DB_PATH):
        try:
            shutil.copy2(source_db, DB_PATH)
        except Exception:
            pass  # Keep going, init_db will create a fresh one
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("Expense Tracker")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
        """)
        await db.commit()


# Run initialization
asyncio.run(init_db())


@mcp.tool
async def add_expense(
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
    date: str | None = None,
) -> dict:
    """
    Add a new expense entry to the database.
    If date is not provided, it defaults to current IST date.
    """
    IST = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(IST)
    if not date:
        date = now.strftime("%d-%m-%Y")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
        INSERT INTO expenses (date, amount, category, subcategory, note)
        VALUES (?, ?, ?, ?, ?)
        """,
            (date, amount, category, subcategory, note),
        )
        await db.commit()
        last_row_id = cursor.lastrowid
    return {"status": "ok", "id": last_row_id}


@mcp.tool
async def list_expenses(start_date: str, end_date: str) -> list[dict]:
    """
    List all expenses between start_date and end_date.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC
            """,
            (start_date, end_date),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


@mcp.tool
async def summarize(start_date: str, end_date: str, category: str = None) -> list[dict]:
    """
    Summarize all expenses by category within an inclusive date range.
    If category is not provided, summarize all categories.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
        SELECT category, SUM(amount) as total_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


@mcp.resource("expense://categories", mime_type="application/json")
async def categories():
    # Read fresh each time so you can edit the file without restarting the server
    async with aiofiles.open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return await f.read()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
