import sys
import os

# Add project root to path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from agents.business_agent import (
    BusinessUnderstandingAgent
)

agent = BusinessUnderstandingAgent()

response = agent.analyze_business(
    industry="Retail",
    goal="Increase revenue",
    dataset_columns="""
    order_id
    customer_id
    product_name
    region
    revenue
    order_date
    """
)

print(response)