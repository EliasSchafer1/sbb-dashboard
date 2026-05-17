import json
from shapely.geometry import LineString
import geopandas as gpd
import folium
import branca.colormap as cm
import numpy as np
import pandas as pd

# Pre-processing
# Store cleaned dataframe in session_state so user changes such as 
# added rows or imputed values are kept during the current session.

def draw_map(trains_df, data_sel):
    map_df = (
        trains_df
        .groupby("abschnitt", as_index=False)
        .agg(
            zuege=(data_sel, "mean"),
            verbindung=("verbindung", "first")
        )
    )
    map_df["geometry"] = map_df["verbindung"].apply(
        lambda x: LineString(json.loads(x)["coordinates"])
    )
    map_df["log_zuege"]=np.log1p(map_df["zuege"])
    gdf = gpd.GeoDataFrame(
        map_df,
        geometry="geometry",
        crs="EPSG:4326"
    )
    # Initialize world map with zoom position in Zurich
    m = folium.Map(location=[47.3, 8.5], zoom_start=8, tiles="CartoDB positron")
    # Create a colormap with colors from yellow to red, depending on the nr. of trains
    colormap = cm.linear.YlOrBr_09.scale(
        gdf["log_zuege"].min(),
        gdf["log_zuege"].max()
    )
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            "color": (
                "gray"
                if pd.isna(feature["properties"]["log_zuege"])
                else colormap(feature["properties"]["log_zuege"])
            ),
            "weight": 4
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["abschnitt", "zuege"]
        )
    ).add_to(m)
    
    return m