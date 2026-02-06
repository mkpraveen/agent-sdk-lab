"""
MCP server exposing SQLite invoice queries.

Run:
  uv run python /Users/praveenmk/oai_bootcamp/agent-sdk-lab/mcp_invoice_server.py
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from typing import Any

from mcp.server.fastmcp import FastMCP


def _db_path() -> str:
    return os.path.join(os.path.dirname(__file__), "invoices.db")


def _query_invoices_by_customer_name(customer_name: str) -> dict[str, Any]:
    db_path = _db_path()
    if not os.path.exists(db_path):
        return {
            "error": "invoices.db not found",
            "db_path": db_path,
        }

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        customers = conn.execute(
            """
            SELECT customer_id, customer_name, email, phone, city, state, country
            FROM customer_master
            WHERE customer_name LIKE ? COLLATE NOCASE
            ORDER BY customer_name
            """,
            (f"%{customer_name}%",),
        ).fetchall()

        if not customers:
            return {
                "customer_name_query": customer_name,
                "customers": [],
                "invoices": [],
                "message": "No matching customers found.",
            }

        invoices_out: list[dict[str, Any]] = []
        customers_out = [dict(row) for row in customers]

        for cust in customers:
            invoices = conn.execute(
                """
                SELECT invoice_id, invoice_number, customer_id, invoice_date, due_date,
                       currency_code, status, subtotal_amount, tax_amount, total_amount, notes
                FROM invoice_header
                WHERE customer_id = ?
                ORDER BY invoice_date, invoice_id
                """,
                (cust["customer_id"],),
            ).fetchall()

            for inv in invoices:
                lines = conn.execute(
                    """
                    SELECT line_id, line_number, item_code, description, quantity, unit_price,
                           discount_amount, tax_amount, line_total
                    FROM invoice_line
                    WHERE invoice_id = ?
                    ORDER BY line_number
                    """,
                    (inv["invoice_id"],),
                ).fetchall()

                invoices_out.append(
                    {
                        "invoice": dict(inv),
                        "lines": [dict(line) for line in lines],
                        "customer": {
                            "customer_id": cust["customer_id"],
                            "customer_name": cust["customer_name"],
                        },
                    }
                )

        return {
            "customer_name_query": customer_name,
            "customers": customers_out,
            "invoices": invoices_out,
        }
    finally:
        conn.close()


def _build_server(host: str, port: int, streamable_http_path: str) -> FastMCP:
    return FastMCP(
        "invoice-sqlite-server",
        host=host,
        port=port,
        streamable_http_path=streamable_http_path,
    )


def _register_tools(server: FastMCP) -> None:
    @server.tool()
    def get_invoices_by_customer_name(customer_name: str) -> dict[str, Any]:
        """
        Query invoices and line items by customer name (partial, case-insensitive).
        """
        return _query_invoices_by_customer_name(customer_name=customer_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run invoice MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="streamable-http",
        help="MCP transport (default: streamable-http)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host")
    parser.add_argument("--port", type=int, default=8000, help="HTTP bind port")
    parser.add_argument(
        "--path",
        default="/mcp",
        help="Streamable HTTP path (default: /mcp)",
    )
    args = parser.parse_args()

    mcp = _build_server(host=args.host, port=args.port, streamable_http_path=args.path)
    _register_tools(mcp)
    mcp.run(transport=args.transport)
