import polars as pl

connection_string = "postgresql://sageosborne@localhost:5432/chicago311"

df = pl.read_csv("Data_By_Community_Area.csv") 

income_cols = [
    "Under $25,000", "$25,000 to $49,999", "$50,000 to $74,999",
    "$75,000 to $125,000", "$125,000 +", "Total Population"
]

df = df.with_columns([
    pl.col(c).str.replace_all(",", "").cast(pl.Int64) for c in income_cols
])

df = df.with_columns(
    pl.col("Community Area")
      .str.to_titlecase()
      .str.replace("Ohare", "O'Hare")
      .str.replace("Mckinley", "McKinley")
      .alias("COMMUNITY_AREA_NAME")
)

df = df.select(["COMMUNITY_AREA_NAME"] + income_cols)

print(df)

#df.write_database("community_demographics", connection_string, if_table_exists="replace", engine="adbc")