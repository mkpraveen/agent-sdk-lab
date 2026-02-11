from dotenv import load_dotenv
import os
import sqlite3

# Load Environment Vars
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set default API key for Agents
from agents import set_default_openai_key
set_default_openai_key(OPENAI_API_KEY)

# Define Search Agent
from agents import Agent, WebSearchTool
search_agent = Agent(
    name = "FitnessSearchAgent",
    instructions=(
        "Immediately call the WebSearchTool to find up-to-date fitness information or trends based on the user's query."
    ),
    tools=[WebSearchTool()]
)

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

from agents import FileSearchTool

# Define Knowledge Agent
def create_vector_store(store_name: str) -> str:
    vs = client.vector_stores.create(name=store_name)
    return vs.id

vs_id = create_vector_store("Fitness Knowledge Base - PMK")
knowledge_agent = Agent(
    name = "FitnessKnowledgeAgent",
    instructions="Answer user questions about Fitness programs with concise, helpful responses using the FileSearchTool.",
    tools=[FileSearchTool(max_num_results=3, vector_store_ids=[vs_id])]
)

# Define custom tool for Account Agent
from agents import function_tool

@function_tool
def get_membership_info(user_id: str) -> dict:
    """Retrun dummy membership data for a given user"""
    return {
      "user_id": user_id,
      "name": "Jane Doe",
      "membership_level": "Platinum",
      "remaining_sessions": 8,
  }
account_agent = Agent(
    name="FitnessAccountAgent",
    instructions="Provide membership information based on a user ID using the get_membership_info tool.",
    tools=[get_membership_info]
)

# Define custom tool for Invoice Agent
@function_tool
def get_invoices_by_customer_name(customer_name: str) -> dict:
    """Return invoices and line items for a customer name (partial match, case-insensitive)."""
    db_path = os.path.join(os.path.dirname(__file__), "invoices.db")
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

        customers_out = [dict(row) for row in customers]
        customer_ids = [cust["customer_id"] for cust in customers]
        cust_lookup = {c["customer_id"]: c["customer_name"] for c in customers}

        placeholders = ",".join("?" for _ in customer_ids)
        invoices = conn.execute(
            f"""
            SELECT invoice_id, invoice_number, customer_id, invoice_date, due_date,
                   currency_code, status, subtotal_amount, tax_amount, total_amount, notes
            FROM invoice_header
            WHERE customer_id IN ({placeholders})
            ORDER BY invoice_date, invoice_id
            """,
            customer_ids,
        ).fetchall()

        if not invoices:
            return {
                "customer_name_query": customer_name,
                "customers": customers_out,
                "invoices": [],
            }

        invoice_ids = [inv["invoice_id"] for inv in invoices]
        line_placeholders = ",".join("?" for _ in invoice_ids)
        lines = conn.execute(
            f"""
            SELECT line_id, invoice_id, line_number, item_code, description, quantity,
                   unit_price, discount_amount, tax_amount, line_total
            FROM invoice_line
            WHERE invoice_id IN ({line_placeholders})
            ORDER BY invoice_id, line_number
            """,
            invoice_ids,
        ).fetchall()

        lines_by_invoice: dict[int, list[dict]] = {}
        for line in lines:
            lines_by_invoice.setdefault(line["invoice_id"], []).append(dict(line))

        invoices_out = []
        for inv in invoices:
            inv_id = inv["invoice_id"]
            cust_id = inv["customer_id"]
            invoices_out.append(
                {
                    "invoice": dict(inv),
                    "lines": lines_by_invoice.get(inv_id, []),
                    "customer": {
                        "customer_id": cust_id,
                        "customer_name": cust_lookup[cust_id],
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

invoice_agent = Agent(
    name="InvoiceAssistant",
    instructions=(
        "Lookup invoices for a given customer name using the get_invoices_by_customer_name tool. "
        "Return a concise summary with invoice numbers, dates, totals, and line items."
    ),
    tools=[get_invoices_by_customer_name],
)

# Setup Triage Agent
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
triage_agent = Agent(
    name="FitnessAssistant",
    instructions=prompt_with_handoff_instructions(
"""
You are the virtual fitness assistant for FitLife. Welcome the user and ask how you can help.
Based on the user's intent, route to:
- FitnessAccountAgent for membership queries,
- FitnessKnowledgeAgent for workout or nutrition FAQs,
- FitnessSearchAgent for general fitness trends or real-time info,
- InvoiceAssistant for invoice lookups by customer name.
"""
    ),
    handoffs=[account_agent, knowledge_agent, search_agent, invoice_agent]
)

from agents import Runner, trace
import asyncio

async def test_queries():
    examples = [
    #   "What is my remaining session count? My user ID is 12345",
      "Tell me about the Fitness - Why Is Physical Activity So Important?",
    #   "What fitness trends are popular right now?",
    "Provide invoice details for customer Pioneer Tech Co."
    ]
    with trace("FitLife Assistant Test"):
      for query in examples:
          result = await Runner.run(triage_agent, query)
          print(f"User: {query}\n{result.final_output}\n---")

def main():
    asyncio.run(test_queries())


    print("Hello from agent-sdk-lab!")


if __name__ == "__main__":
    main()
