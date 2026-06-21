import streamlit as st
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from data_store import get_trains_df
from layout import sbb_header
import pandas as pd

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
row1_col1, row1_col2, row1_col3 = st.columns((1, 2, 1))
row2_col1, row2_col2, row2_col3 = st.columns(3)
# User specifications
with row1_col1:
    selected_year = st.selectbox(
        "Select Year",
        options=[2024, 2025],
        key="year_select_traffic"
    )
with row2_col1:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_traffic"
    )
with row2_col2:
    metrics = ["Show separately", "Total", "Average"]
    metric = st.radio(
        "Aggregation across selected sections",
        metrics
    )
with row2_col3:
    smoothing = st.radio(
        "Smoothing",
        ["None", "3-month rolling mean"]
    )
sort_options = ["Alphabet", "Variance"]
with row1_col3:
    sel_sort_option = st.radio(
        "Sort sections by",
        sort_options,
        key="sort_sections_traffic"
    )
with row1_col2:
    year_col = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
    # Sort option selected by user
    if sel_sort_option == sort_options[0]:
        section_options = sorted(trains_df["section"].unique())
    else:
        section_variance = (
            trains_df.groupby("section")[year_col]
            .var()
            .sort_values(ascending=False)
        )
        section_options = section_variance.index.tolist()
        
    default_value = [section_options[0]] if section_options else []
    
    selected_sections = st.multiselect(
        "Select Route Sections",
        options=section_options,
        # Use default only once
        default=default_value if "selected_sections_traffic" not in st.session_state else None,
        placeholder="Choose sections",
        key="selected_sections_traffic"
    )    

data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
zoom_mode_1 = st.checkbox("Zoom y-axis into data", key="zoom_traffic_1")

filtered = trains_df[trains_df["section"].isin(selected_sections)].copy()
plot_args = {
    "x": "reference_month",
    "y": "total_trains",
    "labels" : {"reference_month":"Month", "total_trains": "Average Daily Trains", "section" : "Route Section"},
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

# Use rolling mean if selected
def add_rolling(df, window=3):
    df = df.sort_values("reference_month").copy()
    df["total_trains"] = df["total_trains"].rolling(window=window, min_periods=1).mean()
    return df
if smoothing == "3-month rolling mean" and not compare_months.empty:
    if metric == "Show separately":
        compare_months = pd.concat([
            add_rolling(
                compare_months[compare_months["section"] == section]
            )
            for section in compare_months["section"].unique()
        ])
    else:
        compare_months = add_rolling(compare_months)
        
# Make plot
fig = px.line(compare_months, **plot_args)
if zoom_mode_1:
    fig.update_yaxes(autorange=True)
else:
    fig.update_yaxes(rangemode="tozero")
st.plotly_chart(fig, width="stretch")

######################## Line chart of traffic comparison ############################

st.subheader("Comparison 2024-2025")
st.write("Monthly average daily train traffic for a selected route section across 2024 and 2025.")

col1, col2, col3 = st.columns((2, 1, 1))

sort_options_2 = ["Alphabet", "Largest mean relative difference", "Largest mean absolute difference"] 
with col2:
    sel_sort_option_2 = st.radio(
        "Sort sections by",
        options=sort_options_2,
        key="sort_sections_comparison"
    )
with col3:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type2_select_traffic"
    )
current_year_col, previous_year_col = train_type_to_columns[train_type]
with col1:
    # Sort option selected by user
    if sel_sort_option_2 == sort_options_2[0]:
        section_options_2 = sorted(trains_df["section"].unique())
    elif sel_sort_option_2 == sort_options_2[1]:
        def safe_relative_diff(g):
            epsilon = 1  # kleine Konstante um Division durch 0 zu vermeiden
            diffs = (g[current_year_col] - g[previous_year_col]) / (g[previous_year_col] + epsilon)
            return diffs.abs().mean()
        rel_diff_per_section = (
            trains_df.groupby("section")
            .apply(safe_relative_diff)
            .sort_values(ascending=False)
        )
        section_options_2 = rel_diff_per_section.index.tolist()
    else:
        diff_per_section = (
            trains_df.groupby("section")
            .apply(lambda g: (g[current_year_col] - g[previous_year_col]).abs().mean())
            .sort_values(ascending=False)
        )
        section_options_2 = diff_per_section.index.tolist()
    
    selected_section = st.selectbox(
        "Select Route Section",
        options=section_options_2,
        key="explore_section_select_2",
    )
zoom_mode_2 = st.checkbox("Zoom y-axis into data", key="zoom_traffic_2")

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
if zoom_mode_2:
    fig.update_yaxes(autorange=True)
else:
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