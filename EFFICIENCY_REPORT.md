# Efficiency Report -- agent-sdk-lab

## 1. N+1 Query Pattern in Invoice Lookup (HIGH)

**Files:** `main.py` (lines 69-126), `mcp_invoice_server.py` (lines 30-95)

The `get_invoices_by_customer_name` function issues **1 + C + I** separate SQL queries
(1 customer lookup, C invoice-header queries per customer, I line-item queries per
invoice). For a customer with 10 invoices each having 5 line items this means
**1 + 1 + 10 = 12 round-trips** to SQLite instead of the 1-2 that a JOIN-based
approach would need. The cost compounds quickly with broader name matches that hit
multiple customers.

**Fix included in this PR:** replace the nested loop with a single two-query approach
using `IN`-clause batching for invoice headers and line items.

---

## 2. Duplicated Invoice Query Logic (MEDIUM)

**Files:** `main.py` (lines 60-134) vs `mcp_invoice_server.py` (lines 22-95)

The invoice-fetching logic is copy-pasted almost verbatim between the two files.
Any bug fix or optimisation must be applied twice, and they can drift out of sync.

**Suggested fix:** extract the shared logic into a common module
(e.g. `invoice_queries.py`) and import it from both consumers.

---

## 3. File Handle Leak in `load_vector.py` (MEDIUM)

**File:** `load_vector.py` (line 16)

```python
file_resp = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
```

`open()` is called without a `with` statement or explicit `close()`. If the API call
raises an exception the file descriptor is leaked until GC collects it.

**Suggested fix:** use a context manager:
```python
with open(file_path, "rb") as f:
    file_resp = client.files.create(file=f, purpose="assistants")
```

---

## 4. Vector Store Created on Every Import (LOW-MEDIUM)

**File:** `main.py` (line 33)

```python
vs_id = create_vector_store("Fitness Knowledge Base - PMK")
```

This runs at **module-import time**, so importing `main` for tests, linting, or
any other purpose fires a real OpenAI API call and creates a brand-new (duplicate)
vector store each time.

**Suggested fix:** move the call inside `main()` or guard it with
`if __name__ == "__main__"`, and consider caching or reusing an existing store by
name.

---

## 5. Scattered Imports in `main.py` (LOW)

**File:** `main.py`

Imports are spread across lines 1-3, 10-14, 23, 26, 41, 146, 162-163 instead of
being consolidated at the top of the file. This makes the module harder to scan
and can mask circular-import issues.

**Suggested fix:** consolidate all imports at the top of the file following PEP 8
ordering (stdlib, third-party, local).
