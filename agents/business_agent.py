from config.llm import llm


class BusinessUnderstandingAgent:

    def analyze_business(
        self,
        industry,
        goal,
        dataset_columns
    ):

        prompt = f"""
        You are a senior business analyst.

        Industry: {industry}

        Business Goal: {goal}

        Dataset Columns:
        {dataset_columns}

        Understand the business.

        Suggest:

        1. Business type
        2. Important KPIs
        3. Recommended analysis
        4. Key business risks
        5. Best dashboard visuals
        """

        response = llm.invoke(prompt)

        return response.content