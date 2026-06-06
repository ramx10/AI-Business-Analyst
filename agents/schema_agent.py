class SchemaAgent:

    def analyze_schema(self, df):

        schema_info = {}

        for column in df.columns:

            schema_info[column] = {
                "datatype": str(df[column].dtype),
                "unique_values": int(df[column].nunique())
            }

        return schema_info