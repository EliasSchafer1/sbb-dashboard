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
        .groupby("section", as_index=False)
        .agg(
            total_trains=(data_sel, "mean"),
            connection=("connection", "first")
        )
    )
    map_df["geometry"] = map_df["connection"].apply(
        lambda x: LineString(json.loads(x)["coordinates"])
    )
    map_df["log_trains"]=np.log1p(map_df["total_trains"])
    gdf = gpd.GeoDataFrame(
        map_df,
        geometry="geometry",
        crs="EPSG:4326"
    )
    # Initialize world map with zoom position in Zurich
    m = folium.Map(location=[47.3, 8.5], zoom_start=8, tiles="CartoDB positron")
    # Create a colormap with colors from yellow to red, depending on the number of trains
    colormap = cm.linear.YlOrBr_09.scale(
        gdf["log_trains"].min(),
        gdf["log_trains"].max()
    )
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            "color": (
                "gray"
                if pd.isna(feature["properties"]["log_trains"])
                else colormap(feature["properties"]["log_trains"])
            ),
            "weight": 4
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["section", "total_trains"]
        )
    ).add_to(m)
    
    return m