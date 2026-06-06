class DataCleaningAgent:

    def analyze_data_quality(self, df):

        missing_values = (
            df.isnull()
            .sum()[df.isnull().sum() > 0]
            .to_dict()
        )

        duplicate_rows = int(df.duplicated().sum())

        return {
            "missing_values": missing_values,
            "duplicate_rows": duplicate_rows
        }