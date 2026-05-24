import duckdb

result = duckdb.sql("""
SELECT 10 + 5 AS total
""").fetchall()

print(result)