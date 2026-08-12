"""Database-backed catalogue bootstrap for the commercial MCP tools."""

import csv
import os
from sqlalchemy.orm import Session

from backend.models.service import Service


def seed_catalogue(session: Session) -> int:
    """Insert the bundled catalogue once, without overwriting managed prices."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(root, "data", "products.csv")
    created = 0

    with open(csv_path, encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            code = row["product_code"].strip().upper()
            if session.query(Service.id).filter(Service.code == code).first():
                continue
            session.add(Service(
                code=code,
                name=row["name"].strip(),
                description=row["name"].strip(),
                unit="package",
                unit_price=float(row["unit_price"]),
                currency="MAD",
                tax_rate=0.20,
            ))
            created += 1

    if created:
        session.commit()
    return created
