# import frappe
# import json

# @frappe.whitelist()
# def add_item_to_bom(bom_name, item_data):
#     # Convert JSON string to dict
#     if isinstance(item_data, str):
#         item_data = json.loads(item_data)

#     item_data = frappe._dict(item_data)
#     bom = frappe.get_doc("BOM", bom_name)

#     # Append new item
#     bom.append("items", {
#         "item_code": item_data.item_code,
#         "qty": item_data.qty,
#         "uom": item_data.uom,
#         "rate": item_data.rate,
#         "bom_no": item_data.bom_no
#     })

#     # Save even if submitted
#     bom.save(ignore_permissions=True)
#     frappe.db.commit()
############## above codee is adding the single item in the items table only ##########











###################################### It's below code is updaing the two level bom ##########


import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_default_bom_and_details(item_code):
    item = frappe.get_doc("Item", item_code)
    return {
        "bom_no": item.default_bom or "",
        "uom": item.stock_uom or "",
        "description": item.description or ""
    }

@frappe.whitelist()
def add_item_with_exploded_bom(docname, item_code, qty, uom, rate):
    doc = frappe.get_doc("BOM", docname)
    item_data = frappe.get_doc("Item", item_code)
    default_bom = item_data.default_bom
    amount = flt(qty) * flt(rate)

    # Add to main items table
    doc.append("items", {
        "item_code": item_code,
        "qty": qty,
        "uom": uom,
        "rate": rate,
        "bom_no": default_bom,
        "amount": amount,
        "stock_qty": qty,
        "conversion_factor": 1,
        "include_item_in_manufacturing": 1,
        "do_not_explode": 0
    })

    if default_bom:
        # Add exploded items from BOM
        bom_doc = frappe.get_doc("BOM", default_bom)
        for row in bom_doc.items:
            doc.append("exploded_items", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "description": row.description,
                "stock_qty": row.qty,
                "stock_uom": row.uom,
                "rate": row.rate or 0,
                "bom_no": default_bom,
                "amount": flt(row.qty) * flt(row.rate or 0),
                "include_item_in_manufacturing": 1,
                "qty_consumed_per_unit": row.qty
            })
    else:
        # Add manually entered item to exploded_items
        doc.append("exploded_items", {
            "item_code": item_code,
            "item_name": item_data.item_name,
            "description": item_data.description,
            "stock_qty": qty,
            "stock_uom": uom,
            "rate": rate,
            "bom_no": None,
            "amount": amount,
            "include_item_in_manufacturing": 1,
            "qty_consumed_per_unit": qty
        })

    doc.save(ignore_permissions=True)
