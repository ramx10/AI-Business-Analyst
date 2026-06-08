import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import io
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from api.session_store import new_session_id, save_df

router = APIRouter()


def _generate_sample_df() -> pd.DataFrame:
    np.random.seed(42)
    n = 2823
    
    # 1. Date (from 2024-01-01 to 2025-12-31)
    start = datetime(2024, 1, 1)
    dates = [start + timedelta(days=int(np.random.randint(0, 730))) for _ in range(n)]
    
    # 2. Region / Territory: EMEA, APAC, Japan
    sel_regions = np.random.choice(["EMEA", "APAC", "Japan"], n, p=[0.80, 0.12, 0.08])
    
    # 3. Product Category (Product Line)
    categories = [
        "Classic Cars", "Vintage Cars", "Motorcycles", 
        "Trucks and Buses", "Planes", "Ships", "Trains"
    ]
    cat_p = [0.35, 0.22, 0.12, 0.11, 0.10, 0.07, 0.03]
    sel_cats = np.random.choice(categories, n, p=cat_p)
    
    # 4. Products (Product Code)
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
    
    # 5. Order ID
    order_ids = [f"10{100 + np.random.randint(0, 300)}" for _ in range(n)]
    
    # 6. Customer ID
    customers = [
        "Land of Toys Inc.", "Reims Collectables", "Mini Gifts Distributors Ltd.", 
        "Havel & Collectables", "Scandinavian Gift Ideas", "Danish Wholesale Imports"
    ]
    sel_customers = np.random.choice(customers, n)
    
    # 7. Revenue (Sales) based on Region
    revenue = []
    for r in sel_regions:
        if r == "EMEA":
            val = np.random.normal(2175, 500)
        elif r == "APAC":
            val = np.random.normal(2200, 500)
        else: # Japan
            val = np.random.normal(2000, 400)
        revenue.append(round(max(300, val), 2))
    revenue = np.array(revenue)
    
    # 8. Profit (about 25% to 35% of Revenue)
    profit = (revenue * np.random.uniform(0.25, 0.35, n)).round(2)
    
    # 9. PostalCode (with exactly 465 missing values!)
    postal_codes = []
    for i in range(n):
        if len(postal_codes) < 465:
            postal_codes.append(None)
        else:
            postal_codes.append(str(np.random.randint(10000, 99999)))
    np.random.shuffle(postal_codes)
    
    df = pd.DataFrame({
        "Date": dates,
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


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Accept a CSV file upload, save to session, return session_id."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding_errors="replace")
        session_id = new_session_id()
        save_df(session_id, df)
        return JSONResponse({
            "session_id": session_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "preview": df.head(5).fillna("").astype(str).to_dict(orient="records"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/sample")
async def load_sample():
    """Generate and return a sample retail sales dataset."""
    try:
        df = _generate_sample_df()
        session_id = new_session_id()
        save_df(session_id, df)
        return JSONResponse({
            "session_id": session_id,
            "filename": "sample_retail_sales.csv",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "preview": df.head(5).fillna("").astype(str).to_dict(orient="records"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
