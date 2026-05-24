from config.llm import llm


class DataCleaningAgent:

    def analyze_data_quality(
        self,
        dataframe_info
    ):

        prompt = f"""
        You are a senior data cleaning expert.

        Analyze dataset quality.

        Dataset Information:
        {dataframe_info}

        Identify:

        1. Missing values
        2. Duplicate risks
        3. Datatype problems
        4. Outlier risks
        5. Recommended cleaning steps

        Give practical recommendations.
        """

        response = llm.invoke(prompt)

        return response.content