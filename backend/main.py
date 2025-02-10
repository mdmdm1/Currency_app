from fastapi import FastAPI
from routes import (
    customer,
    deposit,
    debt,
    employee,
    treasury,
    currency,
    audit_log,
    user,
)

app = FastAPI(title="Currency Bank API", version="1.0")

# Include all routers
app.include_router(customer.router)
app.include_router(deposit.router)
app.include_router(debt.router)
app.include_router(employee.router)
app.include_router(treasury.router)
app.include_router(currency.router)
app.include_router(audit_log.router)
app.include_router(user.router)

# Run with: uvicorn main:app --reload
