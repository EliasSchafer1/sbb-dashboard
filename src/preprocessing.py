import pandas as pd
import json

# extracts all the stations from the sbb dataframe
# returns dataframe of the form
#  | station (string) | label (string) | latitude (float) | longitude (float) |
#  |------------------|----------------|------------------|--------------------|  
#  | Travers          | TR             | 46.94            | 6.67              |
#
# hint: latitude = Breitengrad (Nord - Süd), longitude = Längengrad (Ost- West)
def extract_stations_df(trains_df):


    # list with station infos (will become the rows of the final dataframe)
    stations_rows = []

    #set of stations we have extracted already
    extracted_stations = set()

    for _, row in trains_df.iterrows():

        #split section into two station names
        station_from, station_to = row["section"].split(" – ")

        #add second station if not yet
        if(station_to not in extracted_stations):
            stations_rows.append({
                "station": station_to,
                "label": row["section_to"],
                "latitude": json.loads(row["connection"])["coordinates"][1][1],
                "longitude": json.loads(row["connection"])["coordinates"][1][0],
            })

            extracted_stations.add(station_to)

        #add first station if not yet
        if(station_from not in extracted_stations):
            stations_rows.append({
                "station": station_from,
                "label": row["section_from"],
                "latitude": json.loads(row["connection"])["coordinates"][0][1],
                "longitude": json.loads(row["connection"])["coordinates"][0][0],
            })

            extracted_stations.add(station_from)

    #create and return the dataframe
    stations_df = pd.DataFrame(stations_rows)
    return stations_df