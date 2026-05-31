import polars as pl

connection_string = "postgresql://sageosborne@localhost:5432/chicago311"

df = pl.scan_csv("311_Service_Requests_20260527.csv")

drop_cols = [
    "CITY", "STATE", "ZIP_CODE", "ELECTRICAL_DISTRICT", "ELECTRICITY_GRID", "POLICE_SECTOR",
    "POLICE_DISTRICT", "POLICE_BEAT", "PRECINCT", "SANITATION_DIVISION_DAYS",
    "X_COORDINATE", "Y_COORDINATE", "LOCATION", "LEGACY_RECORD", "LEGACY_SR_NUMBER",
    "PARENT_SR_NUMBER", "STREET_NUMBER", "STREET_DIRECTION", "STREET_NAME", "STREET_TYPE",
]


#print(df.schema)

#matches areas to their actuall name 
df = df.drop(drop_cols)

community_area_names = {
    "1": "Rogers Park", "2": "West Ridge", "3": "Uptown", "4": "Lincoln Square",
    "5": "North Center", "6": "Lake View", "7": "Lincoln Park", "8": "Near North Side",
    "9": "Edison Park", "10": "Norwood Park", "11": "Jefferson Park", "12": "Forest Glen",
    "13": "North Park", "14": "Albany Park", "15": "Portage Park", "16": "Irving Park",
    "17": "Dunning", "18": "Montclare", "19": "Belmont Cragin", "20": "Hermosa",
    "21": "Avondale", "22": "Logan Square", "23": "Humboldt Park", "24": "West Town",
    "25": "Austin", "26": "West Garfield Park", "27": "East Garfield Park", "28": "Near West Side",
    "29": "North Lawndale", "30": "South Lawndale", "31": "Lower West Side", "32": "Loop",
    "33": "Near South Side", "34": "Armour Square", "35": "Douglas", "36": "Oakland",
    "37": "Fuller Park", "38": "Grand Boulevard", "39": "Kenwood", "40": "Washington Park",
    "41": "Hyde Park", "42": "Woodlawn", "43": "South Shore", "44": "Chatham",
    "45": "Avalon Park", "46": "South Chicago", "47": "Burnside", "48": "Calumet Heights",
    "49": "Roseland", "50": "Pullman", "51": "South Deering", "52": "East Side",
    "53": "West Pullman", "54": "Riverdale", "55": "Hegewisch", "56": "Garfield Ridge",
    "57": "Archer Heights", "58": "Brighton Park", "59": "McKinley Park", "60": "Bridgeport",
    "61": "New City", "62": "West Elsdon", "63": "Gage Park", "64": "Clearing",
    "65": "West Lawn", "66": "Chicago Lawn", "67": "West Englewood", "68": "Englewood",
    "69": "Greater Grand Crossing", "70": "Ashburn", "71": "Auburn Gresham", "72": "Beverly",
    "73": "Washington Heights", "74": "Mount Greenwood", "75": "Morgan Park",
    "76": "O'Hare", "77": "Edgewater"
}

df = df.with_columns([
    pl.col("COMMUNITY_AREA").cast(pl.Utf8).replace(community_area_names).alias("COMMUNITY_AREA_NAME")
])

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
df = df.drop_nulls(subset = "CLOSED_DATE")
df = df.unique(subset=["SR_NUMBER"])
df = df.filter(pl.col("DUPLICATE") == False)

# query1 = """
#     SELECT "SR_TYPE", COUNT(*) as count
#     FROM requests
#     GROUP BY "SR_TYPE"
#     ORDER BY count DESC
# """

# complaint_types = pl.read_database_uri(query1, connection_string)
#print(complaint_types)

# Filtering out "311 Information Only Call" and "Aircraft Noise Complaint"
# Info calls have no real service work, aircraft noise skews response times
# and is concentrated in a few areas near airports rather than reflecting city service quality
# query2 = """
#     SELECT "COMMUNITY_AREA_NAME", AVG("RESPONSE_TIME_HOURS") as avg_response_hours
#     FROM requests
#     WHERE "SR_TYPE" NOT IN ('311 Information Only Call', 'Aircraft Noise Complaint')
#     AND "COMMUNITY_AREA_NAME" IS NOT NULL
#     GROUP BY "COMMUNITY_AREA_NAME"
#     ORDER BY avg_response_hours DESC
# """

# response_by_area = pl.read_database_uri(query2, connection_string)
# with pl.Config(tbl_rows=77):
#     print(response_by_area)

# query3 = """
#     SELECT EXTRACT(month FROM "CREATED_DATE")::int as month, COUNT(*) as count
#     FROM requests
#     WHERE "SR_TYPE" NOT IN ('311 Information Only Call', 'Aircraft Noise Complaint')
#     GROUP BY month
#     ORDER BY month
# """

# seasonal = pl.read_database_uri(query3, connection_string)
# print(seasonal)

query4 = """
    WITH agency_stats AS (
        SELECT 
            "OWNER_DEPARTMENT",
            AVG("RESPONSE_TIME_HOURS") as avg_response_hours,
            COUNT(*) as total_requests
        FROM requests
        WHERE "SR_TYPE" NOT IN ('311 Information Only Call', 'Aircraft Noise Complaint')
        GROUP BY "OWNER_DEPARTMENT"
    )
    SELECT 
        "OWNER_DEPARTMENT",
        avg_response_hours,
        total_requests,
        RANK() OVER (ORDER BY avg_response_hours ASC) as response_rank
    FROM agency_stats
    ORDER BY response_rank
"""

agency_rankings = pl.read_database_uri(query4, connection_string)
with pl.Config(tbl_rows=50):
    print(agency_rankings)

# streaming engine required due to RAM limitations on local machine 
# if_table_exists is the correct arg name as of Polars 1.25+, originally experienced problems with
# if_exists/on_conflict. polars documentation was usefull

#df.collect(engine="streaming").write_database("requests", connection_string, if_table_exists="replace", engine="adbc")

#database name: chicago311