import json
from shapely.geometry import LineString
import geopandas as gpd
import folium
import branca.colormap as cm
from branca.element import Element
import numpy as np
import pandas as pd

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
    # Display real values in a custom legend while keeping the log color scale
    tick_log_values = np.linspace(gdf["log_trains"].min(), gdf["log_trains"].max(), 6)
    tick_real_values = np.expm1(tick_log_values).astype(int)

    legend_items = "".join(
        f"""
        <div style=\"display:flex; align-items:center; margin-bottom:4px;\">
            <span style=\"display:inline-block; width:18px; height:18px; margin-right:8px; background:{colormap(tick_log)}; border:1px solid rgba(0,0,0,0.15);\"></span>
            <span>{real_value}</span>
        </div>
        """
        for tick_log, real_value in zip(tick_log_values, tick_real_values)
    )
    legend_html = f"""
    <div style=\"
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: white;
        padding: 12px 14px;
        border: 1px solid rgba(0,0,0,0.2);
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.12);
        font-size: 12px;
        line-height: 1.2;
        min-width: 160px;
    ">
        <div style=\"font-weight: 600; margin-bottom: 8px;\">Average Daily Trains</div>
        {legend_items}
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))
    
    return m