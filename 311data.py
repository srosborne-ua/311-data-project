import polars as pl

df = pl.scan_csv("311_Service_Requests_20260527.csv")

drop_cols = [
    "CITY", "STATE", "ELECTRICAL_DISTRICT", "ELECTRICITY_GRID", "POLICE_SECTOR",
    "POLICE_DISTRICT", "POLICE_BEAT", "PRECINCT", "SANITATION_DIVISION_DAYS",
    "X_COORDINATE", "Y_COORDINATE", "LOCATION", "LEGACY_RECORD", "LEGACY_SR_NUMBER",
    "PARENT_SR_NUMBER", "STREET_NUMBER", "STREET_DIRECTION", "STREET_NAME", "STREET_TYPE",
]

df = df.drop(drop_cols)

# Convert into more usefull date format
df = df.with_columns([
    pl.col("CREATED_DATE").str.to_datetime("%m/%d/%Y %I:%M:%S %p"),
    pl.col("CLOSED_DATE").str.to_datetime("%m/%d/%Y %I:%M:%S %p")
])

# Compute response time 
df = df.with_columns([
    ((pl.col("CLOSED_DATE") - pl.col("CREATED_DATE"))
    .dt.total_seconds() / 3600)
    .alias("RESPONSE_TIME_HOURS")
])


df = df.with_columns([
    pl.col("SR_TYPE").str.strip_chars().str.to_titlecase(),
    pl.col("COMMUNITY_AREA").cast(pl.Utf8).str.strip_chars()
])

# get rid of duplicates and nulls
df = df.drop_nulls(subset=["LATITUDE", "LONGITUDE"])
df = df.unique(subset=["SR_NUMBER"])
df = df.filter(pl.col("DUPLICATE") == False)