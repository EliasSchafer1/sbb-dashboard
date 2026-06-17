import streamlit as st
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from data_store import get_trains_df
from layout import sbb_header

trains_df = get_trains_df()

# display sbb header
sbb_header("Explore the Dataframe")

train_types = ["All types", "Passenger trains", "Freight trains"]
train_type_to_columns = {
    "All types": ("daily_trains", "daily_trains_py"),
    "Passenger trains": ("daily_passenger_trains", "daily_passenger_trains_py"),
    "Freight trains": ("daily_freight_trains", "daily_freight_trains_py"),
}

################ Line chart of monthly traffic ####################

# Linechart of monthly average of trains in 2025
st.subheader("Monthly train traffic")
st.write("Monthly average daily train traffic per selected route section for the selected year.")

# Sum or average of selected sections, all sections at the same time
# Choose between daily train categories
col1, col2, col3, col4 = st.columns(4)
# User specifications
with col1:
    selected_sections = st.multiselect(
        "Select Route Sections",
        options=sorted(trains_df["section"].unique()),
        default=[sorted(trains_df["section"].unique())[0]]
    )
with col2:
    selected_year = st.selectbox(
        "Select Year",
        options=[2024, 2025],
        key="year_select_traffic"
    )
with col3:
    metrics = ["Show separately", "Total", "Average"]
    metric = st.radio(
        "Aggregation across selected sections",
        metrics
    )
with col4:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_traffic"
    )
data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
filtered = trains_df[trains_df["section"].isin(selected_sections)].copy()
plot_args = {
    "x": "reference_month",
    "y": "total_trains",
    "labels" : {"reference_month":"Reference Month", "total_trains": "Average Daily Trains", "section" : "Route Section"},
    "markers": True
}
agg_map = {
    "Total": "sum",
    "Average": "mean"
}
# Separate lines
if metric == metrics[0]:
    compare_months = (
        filtered
        .groupby(["reference_month", "section"])
        .agg(total_trains=(data_sel, "mean"))
    ).reset_index()
    plot_args["color"] = "section"
else: # Other metric
    compare_months = (
        filtered
        .groupby("reference_month")
        .agg(total_trains = (data_sel, agg_map[metric]))
    ).reset_index()
# Check if any selected sections have a missing month
incomplete = (
    filtered
    .groupby("section")[data_sel]
    .count()
    .lt(12)
    .any()
)
if incomplete:
    st.info("Some route sections have incomplete data for certain months. These are excluded from aggregations.")
# Make plot
fig = px.line(compare_months, **plot_args)
fig.update_yaxes(rangemode="tozero")
st.plotly_chart(fig, width="stretch")

######################## Line chart of traffic comparison ############################

st.subheader("Comparison 2024-2025")
st.write("Monthly average daily train traffic for a selected route section across 2024 and 2025.")

col1, col2 = st.columns(2)

with col1:
    selected_section = st.selectbox(
        "Select Route Section",
        options=sorted(trains_df["section"].unique()),
        key="explore_section_select_2",
    )
with col2:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type2_select_traffic"
    )

current_year_col, previous_year_col = train_type_to_columns[train_type]

# Filter and aggregate
filtered = trains_df[trains_df["section"] == selected_section].copy()
compare_years = filtered.groupby("reference_month").agg(
    value_2025=(current_year_col, "mean"),
    value_2024=(previous_year_col, "mean"),
).reset_index()

# Wide to long
compare_years_long = compare_years.melt(
    id_vars="reference_month",
    value_vars=["value_2025", "value_2024"],
    var_name="year",
    value_name="total_trains"
)
compare_years_long["year"] = compare_years_long["year"].replace({
    "value_2025": "2025",
    "value_2024": "2024"
})

# Line chart
fig = px.line(
    compare_years_long,
    x="reference_month",
    y="total_trains",
    color="year",
    markers=True,
    line_dash="year",
    line_dash_map={"2024": "dash", "2025": "solid"},
    labels={"reference_month": "Month", "total_trains": "Average Daily Trains", "year": "Year"},
    color_discrete_map={"2024": "#F67469", "2025": "#D50000"}
)
fig.update_yaxes(rangemode="tozero")
st.plotly_chart(fig, width="stretch", key="traffic_lineplot")

######################## Map of route sections #########################

# Create map of all route sections
st.subheader("Route section traffic map")
st.write("Average daily train traffic per route section over the selected year, "
        "colored by traffic intensity.")
# Choose between daily train categories
col1, col2 = st.columns(2)
# User specifies the year
with col1:
    selected_year = st.selectbox(
        "Select Year",
        options=[2024, 2025],
        key="year_select_map"
    )
with col2:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_map"
    )
data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
map_trains = draw_map(trains_df, data_sel=data_sel)
st_folium(map_trains, width="100%", height=600)