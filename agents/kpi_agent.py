class KPIAgent:

    def generate_kpis(self, df):

        kpis = {

            "rows": int(len(df)),

            "columns": int(len(df.columns)),

            "missing_values": int(df.isnull().sum().sum()),

            "duplicate_rows": int(df.duplicated().sum())

        }

        # Add statistics for numeric columns

        numeric_columns = df.select_dtypes(include=["number"])

        if not numeric_columns.empty:

            kpis["statistics"] = numeric_columns.describe().to_dict()

        else:

            kpis["statistics"] = {}

        return kpis