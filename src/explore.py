import streamlit as st
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from main import trains_df
from layout import sbb_header

# display sbb header
sbb_header("Explore the Dataframe")

# Linechart of monthly average of trains in 2025
st.subheader("Monthly train traffic")
st.write("This line chart shows the monthly train traffic per selected section for the selected year.")

# Summe oder Durchschnitt der ausgewählten Stationen, alle Stationen gleichzeitig
# Auswählen zwischen dtv, dtv_p oder dtv_g
col11, col12, col13, col14 = st.columns(4)
# User specifies the year
with col12:
    selected_year = st.selectbox(
        "Jahr auswählen",
        options=[2024, 2025],
        key="year_select_traffic"
    )
with col13:
    metrics = ["Separate", "Sum", "Mean"]
    metric = st.radio(
        "Metric",
        metrics
    )
train_types = ["All types", "Passenger trains", "Freight trains"]
types_to_prefix = {"All types":"dtv_", "Passenger trains":"dtv_p_", "Freight trains":"dtv_g_"}
with col14:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_traffic"
    )
data_sel = "bezugsmonat" if selected_year == 2025 else "vorjahresmonat"
data_sel = types_to_prefix[train_type]+data_sel
# User specifies the stations
with col11:
    valid_abschnitte = (
        trains_df.groupby("abschnitt")[data_sel]
        .filter(lambda x: x.notna().all())
        .index
    )
    selected_sections = st.multiselect(
        "Abschnitte auswählen",
        options=sorted(trains_df.loc[valid_abschnitte, "abschnitt"].unique()),
    )
filtered = trains_df[trains_df["abschnitt"].isin(selected_sections)].copy()
plot_args = {
    "x": "bezugsmonat",
    "y": "zuege_total",
    "markers": True
}
if metric == metrics[0]:
    compare_months = (
        filtered
        .groupby(["bezugsmonat", "abschnitt"])
        .agg(zuege_total=(data_sel, "sum"))
    ).reset_index()
    plot_args["color"] = "abschnitt"
else:
    compare_months = (
        filtered
        .groupby("bezugsmonat")
        .agg(zuege_total = (data_sel, metric.lower()))
    ).reset_index()
# Make plot
fig = px.line(compare_months, **plot_args)
st.plotly_chart(fig, width="stretch")


# Create map of all routes
st.subheader("Map of train routes")
st.write("This map contains the mean monthly traffic from the selected year")
# Auswählen zwischen dtv, dtv_p oder dtv_g
col11, col12 = st.columns(2)
# User specifies the year
with col11:
    selected_year = st.selectbox(
        "Jahr auswählen",
        options=[2024, 2025],
        key="year_select_map"
    )
train_types = ["All types", "Passenger trains", "Freight trains"]
types_to_prefix = {"All types":"dtv_", "Passenger trains":"dtv_p_", "Freight trains":"dtv_g_"}
with col12:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_map"
    )
data_sel = "bezugsmonat" if selected_year == 2025 else "vorjahresmonat"
data_sel = types_to_prefix[train_type]+data_sel
map_trains = draw_map(trains_df, data_sel=data_sel)
st_folium(map_trains, width=700)


