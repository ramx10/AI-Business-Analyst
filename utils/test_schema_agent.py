import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from agents.schema_agent import (
    SchemaUnderstandingAgent
)

agent = SchemaUnderstandingAgent()

response = agent.understand_schema(
    """
    cust_id
    txn_amt
    ord_dt
    region_cd
    rev
    """
)

print(response)