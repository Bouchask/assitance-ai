from typing import List, Dict, Any
from pydantic import BaseModel

class PricingItem(BaseModel):
    service_id: int
    quantity: float
    unit_price: float
    discount_percentage: float = 0.0
    tax_rate: float = 20.0

class PricingResultItem(BaseModel):
    service_id: int
    quantity: float
    unit_price: float
    discount_amount: float
    net_unit_price: float
    total_ht: float
    tax_amount: float
    total_ttc: float

class PricingResult(BaseModel):
    items: List[PricingResultItem]
    subtotal_ht: float
    total_discount: float
    total_net_ht: float
    total_tax: float
    total_ttc: float
    currency: str = "MAD"

class PricingEngine:
    @staticmethod
    def calculate(items: List[PricingItem], currency: str = "MAD") -> PricingResult:
        result_items = []
        subtotal_ht = 0.0
        total_discount = 0.0
        total_net_ht = 0.0
        total_tax = 0.0
        
        for item in items:
            # 1. Calculate discount per unit
            discount_amount_per_unit = item.unit_price * (item.discount_percentage / 100.0)
            net_unit_price = item.unit_price - discount_amount_per_unit
            
            # 2. Total HT for this item
            item_total_ht = net_unit_price * item.quantity
            
            # 3. Tax for this item
            item_tax_amount = item_total_ht * (item.tax_rate / 100.0)
            
            # 4. Total TTC for this item
            item_total_ttc = item_total_ht + item_tax_amount
            
            # Accumulate totals
            subtotal_ht += (item.unit_price * item.quantity)
            total_discount += (discount_amount_per_unit * item.quantity)
            total_net_ht += item_total_ht
            total_tax += item_tax_amount
            
            result_items.append(PricingResultItem(
                service_id=item.service_id,
                quantity=item.quantity,
                unit_price=round(item.unit_price, 2),
                discount_amount=round(discount_amount_per_unit * item.quantity, 2),
                net_unit_price=round(net_unit_price, 2),
                total_ht=round(item_total_ht, 2),
                tax_amount=round(item_tax_amount, 2),
                total_ttc=round(item_total_ttc, 2)
            ))
            
        return PricingResult(
            items=result_items,
            subtotal_ht=round(subtotal_ht, 2),
            total_discount=round(total_discount, 2),
            total_net_ht=round(total_net_ht, 2),
            total_tax=round(total_tax, 2),
            total_ttc=round(total_net_ht + total_tax, 2),
            currency=currency
        )
