from config.llm import llm


class SchemaUnderstandingAgent:

    def understand_schema(
        self,
        dataset_columns
    ):

        prompt = f"""
        You are a senior data analyst.

        Understand the meaning of dataset columns.

        Dataset Columns:
        {dataset_columns}

        For each column explain:

        1. Business meaning
        2. Data type
        3. Possible use in analytics
        4. Whether it is KPI relevant

        Return in structured format.
        """

        response = llm.invoke(prompt)

        return response.content