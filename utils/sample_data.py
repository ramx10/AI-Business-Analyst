import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_sample_sales_df(n_rows: int = 2823) -> pd.DataFrame:
    np.random.seed(42)

    start_date = datetime(2024, 1, 1)
    date_list = [start_date + timedelta(days=int(np.random.randint(0, 730))) for _ in range(n_rows)]

    sel_regions = np.random.choice(["EMEA", "APAC", "Japan"], n_rows, p=[0.80, 0.12, 0.08])

    categories = [
        "Classic Cars", "Vintage Cars", "Motorcycles",
        "Trucks and Buses", "Planes", "Ships", "Trains"
    ]
    cat_p = [0.35, 0.22, 0.12, 0.11, 0.10, 0.07, 0.03]
    sel_cats = np.random.choice(categories, n_rows, p=cat_p)

    prod_pool = {
        "Classic Cars": ["S18_3232", "S10_1949", "S12_1108", "S18_2238", "S24_2887"],
        "Vintage Cars": ["S18_1342", "S18_2709", "S24_2011", "S24_3151"],
        "Motorcycles": ["S10_4698", "S12_2823", "S18_2625"],
        "Trucks and Buses": ["S12_1666", "S18_1097"],
        "Planes": ["S18_1662", "S24_3976"],
        "Ships": ["S700_2824", "S720_1697"],
        "Trains": ["S32_3207", "S50_1392"]
    }
    sel_prods = [np.random.choice(prod_pool[c]) for c in sel_cats]

    order_ids = [f"10{100 + np.random.randint(0, 300)}" for _ in range(n_rows)]

    customers = [
        "Land of Toys Inc.", "Reims Collectables", "Mini Gifts Distributors Ltd.",
        "Havel & Collectables", "Scandinavian Gift Ideas", "Danish Wholesale Imports"
    ]
    sel_customers = np.random.choice(customers, n_rows)

    revenue = []
    for r in sel_regions:
        if r == "EMEA":
            val = np.random.normal(2175, 500)
        elif r == "APAC":
            val = np.random.normal(2200, 500)
        else:
            val = np.random.normal(2000, 400)
        revenue.append(round(max(300, val), 2))
    revenue = np.array(revenue)

    profit = (revenue * np.random.uniform(0.25, 0.35, n_rows)).round(2)

    postal_codes = []
    for i in range(n_rows):
        if len(postal_codes) < 465:
            postal_codes.append(None)
        else:
            postal_codes.append(str(np.random.randint(10000, 99999)))
    np.random.shuffle(postal_codes)

    df = pd.DataFrame({
        "Date": date_list,
        "Order_ID": order_ids,
        "Customer_ID": sel_customers,
        "Region": sel_regions,
        "Product_Category": sel_cats,
        "Product": sel_prods,
        "Revenue": revenue,
        "Profit": profit,
        "PostalCode": postal_codes
    })

    return df.sort_values("Date").reset_index(drop=True)
