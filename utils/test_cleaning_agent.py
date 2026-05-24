import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pandas as pd

from agents.cleaning_agent import (
    DataCleaningAgent
)

# Fake messy dataset
df = pd.DataFrame({
    "customer_id": [1, 2, 2, None],
    "revenue": [100, 200, 200, 1000000],
    "region": ["West", None, "West", "East"]
})

# Better dataset info
data_info = f"""
Columns:
{df.columns.tolist()}

Data Types:
{df.dtypes}

Missing Values:
{df.isnull().sum()}

Duplicate Rows:
{df.duplicated().sum()}

Statistics:
{df.describe(include='all')}

Sample Data:
{df.head().to_string()}
"""

agent = DataCleaningAgent()

response = agent.analyze_data_quality(
    data_info
)

print(response)