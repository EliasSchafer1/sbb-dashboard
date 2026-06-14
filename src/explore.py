import streamlit as st
from streamlit_folium import st_folium
from map_maker import draw_map
import plotly.express as px
from data_store import get_trains_df
from layout import sbb_header

trains_df = get_trains_df()

# display sbb header
sbb_header("Explore the Dataframe")

# Linechart of monthly average of trains in 2025
st.subheader("Monthly train traffic")
st.write("This line chart shows the monthly train traffic per selected route section for the selected year.")

# Sum or average of selected sections, all sections at the same time
# Choose between daily train categories
col11, col12, col13, col14 = st.columns(4)
# User specifies the year
with col12:
    selected_year = st.selectbox(
        "Select Year",
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
train_type_to_columns = {
    "All types": ("daily_trains", "daily_trains_py"),
    "Passenger trains": ("daily_passenger_trains", "daily_passenger_trains_py"),
    "Freight trains": ("daily_freight_trains", "daily_freight_trains_py"),
}
with col14:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_traffic"
    )
data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
# User specifies the sections
with col11:
    valid_sections = (
        trains_df.groupby("section")[data_sel]
        .filter(lambda x: x.notna().all())
        .index
    )
    selected_sections = st.multiselect(
        "Select Route Sections",
        options=sorted(trains_df.loc[valid_sections, "section"].unique()),
    )
filtered = trains_df[trains_df["section"].isin(selected_sections)].copy()
plot_args = {
    "x": "reference_month",
    "y": "total_trains",
    "markers": True
}
if metric == metrics[0]:
    compare_months = (
        filtered
        .groupby(["reference_month", "section"])
        .agg(total_trains=(data_sel, "sum"))
    ).reset_index()
    plot_args["color"] = "section"
else:
    compare_months = (
        filtered
        .groupby("reference_month")
        .agg(total_trains = (data_sel, metric.lower()))
    ).reset_index()
# Make plot
fig = px.line(compare_months, **plot_args)
st.plotly_chart(fig, width="stretch")


# Create map of all route sections
st.subheader("Map of Route Sections")
st.write("This map shows the average daily number of trains for each route section, " \
        "colored by traffic intensity.")
# Choose between daily train categories
col11, col12 = st.columns(2)
# User specifies the year
with col11:
    selected_year = st.selectbox(
        "Select Year",
        options=[2024, 2025],
        key="year_select_map"
    )
train_types = ["All types", "Passenger trains", "Freight trains"]
with col12:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type_select_map"
    )
data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]
map_trains = draw_map(trains_df, data_sel=data_sel)
st_folium(map_trains, width="100%", height=600)

#############################################

st.subheader("Comparison of Train Traffic in 2024 and 2025")
st.write("This map visualizes the difference in train traffic between 2024 and 2025.")

col11, col12 = st.columns(2)

# User specifies the train type
train_types = ["All types", "Passenger trains", "Freight trains"]
with col12:
    train_type = st.radio(
        "Train type",
        train_types,
        key="type2_select_traffic"
    )

data_sel = train_type_to_columns[train_type][0 if selected_year == 2025 else 1]

# User specifies the sections
with col11:
    valid_sections = (
        trains_df.groupby("section")[data_sel]
        .filter(lambda x: x.notna().all())
        .index
    )
    selected_section = st.selectbox(
        "Select Route Section",
        options=sorted(trains_df.loc[valid_sections, "section"].unique()),
        key="explore_section_select_2",
    )

#filter for selected data
filtered = trains_df[trains_df["section"] == selected_section].copy()
plot_args = {
    "x": "reference_month",
    "y": "total_trains",
    "markers": True
}
if metric == metrics[0]:
    compare_months = (
        filtered
        .groupby(["reference_month", "section"])
        .agg(total_trains=(data_sel, "sum"))
    ).reset_index()
    plot_args["color"] = "section"
else:
    compare_months = (
        filtered
        .groupby("reference_month")
        .agg(total_trains = (data_sel, metric.lower()))
    ).reset_index()
current_year_col, previous_year_col = train_type_to_columns[train_type]

#group by months
compare_years = filtered.groupby("reference_month").agg(
    value_2025=(current_year_col, "sum"),
    value_2024=(previous_year_col, "sum"),
).reset_index()

# Transform dataframe from wide format to long format
compare_years_long = compare_years.melt(
    id_vars="reference_month",
    value_vars=["value_2025", "value_2024"],
    var_name="year",
    value_name="total_trains"
)

#replace labels
compare_years_long["year"] = compare_years_long["year"].replace({
    "value_2025": "2025",
    "value_2024": "2024"
})

#creating barplot
fig_bar = px.bar(
    compare_years_long,
    x="reference_month",
    y="total_trains",
    color="year",
    barmode="group",
    color_discrete_map={
        "2024": "#F67469",
        "2025": "#D50000"
    }
)
#make plot
st.plotly_chart(
    fig_bar,
    use_container_width=True,
    key="traffic_barplot",
)
