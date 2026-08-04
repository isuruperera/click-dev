from dataclasses import asdict
from dataclasses import dataclass
from typing import Annotated

import click
import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer


@dataclass(frozen=True)
class Customer:
    id: int
    name: str


@dataclass(frozen=True)
class Invoice:
    id: int
    customer_id: int
    description: str
    total: str


CUSTOMERS = {
    1: Customer(id=1, name="Alice's Bakery"),
    2: Customer(id=2, name="Bob's Bike Shop"),
}

ACCESS_TOKENS = {
    "demo-alice-token": 1,
    "demo-bob-token": 2,
}

INVOICES = {
    1001: Invoice(
        id=1001,
        customer_id=1,
        description="Monthly flour delivery",
        total="184.50",
    ),
    1002: Invoice(
        id=1002,
        customer_id=2,
        description="Replacement wheel parts",
        total="329.00",
    ),
    1003: Invoice(
        id=1003,
        customer_id=1,
        description="Kitchen equipment service",
        total="95.00",
    ),
}

app = FastAPI(title="Invoice Service")
bearer = HTTPBearer(auto_error=False)


def current_customer(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer)
    ],
) -> Customer:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")

    customer_id = ACCESS_TOKENS.get(credentials.credentials)
    if customer_id is None:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return CUSTOMERS[customer_id]


@app.get("/api/invoices")
def list_invoices(
    customer: Annotated[Customer, Depends(current_customer)],
) -> list[dict[str, object]]:
    return [
        asdict(invoice)
        for invoice in INVOICES.values()
        if invoice.customer_id == customer.id
    ]


@app.get("/api/invoices/{invoice_id}")
def get_invoice(
    invoice_id: int,
    customer: Annotated[Customer, Depends(current_customer)],
) -> dict[str, object]:
    invoice = INVOICES.get(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return asdict(invoice)


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=click.IntRange(1, 65535))
def cli(host: str, port: int) -> None:
    """Run the invoice API development server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
