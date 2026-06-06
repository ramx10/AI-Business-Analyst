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
    n = 1500
    start = datetime(2025, 1, 1)
    dates = [start + timedelta(days=int(np.random.randint(0, 365))) for _ in range(n)]

    regions_states = {
        "North": ["New York", "Ohio", "Michigan", "Pennsylvania"],
        "South": ["Florida", "Georgia", "North Carolina", "Texas"],
        "East": ["Massachusetts", "Maryland", "New Jersey"],
        "West": ["California", "Washington", "Colorado", "Oregon"],
    }
    cats_prods = {
        "Technology": ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard"],
        "Office Supplies": ["Paper Reams", "Gel Pens", "Notebooks", "Calculators"],
        "Furniture": ["Desk Chair", "Dining Table", "Bookshelf", "Office Desk"],
    }

    sel_regions = np.random.choice(list(regions_states.keys()), n)
    sel_states = [np.random.choice(regions_states[r]) for r in sel_regions]
    sel_cats = np.random.choice(list(cats_prods.keys()), n, p=[0.4, 0.35, 0.25])
    sel_prods = [np.random.choice(cats_prods[c]) for c in sel_cats]
    revenue = np.random.normal(4500, 2500, n).clip(300, 25000).round(2)
    profit = (revenue * np.random.uniform(0.1, 0.45, n)).round(2)

    df = pd.DataFrame({
        "Date": dates,
        "Order_ID": [f"O-{np.random.randint(5001, 6200)}" for _ in range(n)],
        "Customer_ID": [f"C-{np.random.randint(1001, 1250)}" for _ in range(n)],
        "Region": sel_regions,
        "State": sel_states,
        "Product_Category": sel_cats,
        "Product": sel_prods,
        "Revenue": revenue,
        "Profit": profit,
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
