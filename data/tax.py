from . import db
from .cache import Cache

record = db.tax.find_one()

# these numbers will be multiplied directly so use the format like 1.125 for 12.5%
def tax_style(n):
  return (n / 100) + 1

tax_class = {
    0: 1,
    1: tax_style(12.5),
    2: tax_style(5.5),
    "service_tax": 5.6 / 100
    }

if record:
  tax_class[1] = tax_style(record.get("1", 12.5))
  tax_class[2] = tax_style(record.get("2", 5.5))
  tax_class['service_tax'] = record.get('service_tax', 5.6) / 100


service_charge_cache = Cache('service_charge')


def process_tax(vendor_id, tax_dict):
  taxed_amount = 0
  original_amount = 0
  for k,v in tax_dict.items():
    original_amount += v
    taxed_amount += v * tax_class.get(k, 1)
  service_tax = taxed_amount * tax_class['service_tax']

  service_charge = service_charge_cache.retrieve(str(vendor_id))
  if not service_charge:
    mer = db.merchants.find_one({
      "vendors.vendor_id": vendor_id
      }, {"vendors.$": 1})

    if mer:
      service_charge = mer['vendors'][0].get('service_charge', 0) / 100
    else:
      service_charge = 0

    service_charge_cache.store(str(vendor_id), service_charge)

  calc_service_charge = taxed_amount * service_charge
  service_tax = (taxed_amount + calc_service_charge) * tax_class['service_tax']
  vat = taxed_amount - original_amount
  return {
      "vat": vat,
      "base": original_amount,
      "service_tax": service_tax,
      "service_charge": calc_service_charge,
      "net_after_tax": taxed_amount,
      "total": taxed_amount + service_tax + calc_service_charge
  }


