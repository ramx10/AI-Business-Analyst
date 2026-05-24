import polars as pl

df = pl.DataFrame({
    "name": ["Ram", "AI"],
    "score": [90, 95]
})

print(df)