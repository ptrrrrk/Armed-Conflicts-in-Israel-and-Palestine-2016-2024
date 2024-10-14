import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_pandas_profiling import st_profile_report

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Israel-Palestine.xlsx")
        return df
    except ImportError as e:
        st.error("Failed to import openpyxl. Please ensure it is installed.")
        st.stop()
    except FileNotFoundError:
        st.error("The file 'Israel-Palestine.xlsx' was not found. Please check the file path.")
        st.stop()


# Main function
def main():
    # Set page configuration to wide mode
    st.set_page_config(page_title="Armed Conflicts in Israel and Palestine (2016-2024)", layout="wide")

    st.title("Armed Conflicts in Israel and Palestine (2016-2024)")
    st.markdown("""
        **Data Source:** This data is sourced from the Armed Conflict Location & Event Data Project (ACLED) Currated Data Files. 
        ACLED provides real-time data on political violence and protest events around the world, making it a vital resource for understanding the dynamics of conflict.
        https://acleddata.com/curated-data-files/
        """)

    # Load the data
    df = load_data()

    # Default filter for Palestine and Israel
    st.sidebar.header("Filter options")

    # Country selection
    country_options = ["Palestine", "Israel", "Both"]
    selected_country = st.sidebar.selectbox("Select Country", options=country_options, index=2)  # Default to "Both"

    # Apply the country filter
    if selected_country == "Both":
        df = df[df['country'].isin(["Palestine", "Israel"])]
    else:
        df = df[df['country'] == selected_country]

    # Timeline filter
    years = sorted(df['year'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(years[0]), max_value=int(years[-1]),
                                       value=(int(years[0]), int(years[-1])))

    # Filter based on selected years
    df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

    # Dropdown filters
    disorder_types = st.sidebar.multiselect("Select Disorder Type", options=df['disorder_type'].unique(),
                                            default=df['disorder_type'].unique())
    event_types = st.sidebar.multiselect("Select Event Type", options=df['event_type'].unique(),
                                         default=df['event_type'].unique())

    # Apply the filters
    df = df[df['disorder_type'].isin(disorder_types) & df['event_type'].isin(event_types)]

    # Calculate statistics
    st_profile_report(pr)

    total_events = len(df)
    unique_event_types = df['event_type'].nunique()
    unique_disorder_types = df['disorder_type'].nunique()
    average_events_per_year = total_events / (selected_years[1] - selected_years[0] + 1) if total_events > 0 else 0
    total_fatalities = df['fatalities'].sum() if 'fatalities' in df.columns else None  # Assuming 'fatalities' column exists
    most_frequent_event_type = df['event_type'].value_counts().idxmax() if total_events > 0 else None

    # Display filtered data summary
    st.subheader("Summary Statistics")
    st.write(f"**Number of events:** {total_events}")
    st.write(f"**Unique Event Types:** {unique_event_types}")
    st.write(f"**Unique Disorder Types:** {unique_disorder_types}")
    st.write(f"**Average Events per Year:** {average_events_per_year:.2f}")
    st.write(f"**Total Fatalities:** {total_fatalities}")
    st.write(f"**Most Frequent Event Type:** {most_frequent_event_type}")

    # Visualizations
    visualize_data(df)

    # Display the entire DataFrame at the bottom
    st.subheader("Filtered Data")
    st.dataframe(df, use_container_width=True)  # Display the filtered DataFrame

def visualize_data(df):
    # Map Visualization - Categorize by Event Type
    st.subheader("Incident Locations by Event Type")
    fig_map = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='location',
        hover_data=['event_type', 'notes'],  # Update hover data to show 'event_type'
        color='event_type',  # Change color categorization to 'event_type'
        color_discrete_sequence=px.colors.qualitative.Plotly,  # Use a qualitative color scale for categories
        zoom=5,
        height=500
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(title="Incident Locations Categorized by Event Type")
    st.plotly_chart(fig_map)

    # Line Graph - Incident Count Over Time
    st.subheader("Incidents Count Over Time")
    incident_count = df.groupby('year').size().reset_index(name='count')
    fig_line = px.line(incident_count, x='year', y='count', title="Incidents Count Over Time")
    fig_line.update_layout(xaxis=dict(dtick=1))  # Show only whole numbers on the x-axis
    st.plotly_chart(fig_line)

    # Pie Chart - Event Types Distribution
    st.subheader("Event Types Proportion")
    event_type_count = df['event_type'].value_counts().reset_index()
    event_type_count.columns = ['event_type', 'count']
    fig_pie_event = px.pie(event_type_count, names='event_type', values='count', title="Event Types Distribution")
    st.plotly_chart(fig_pie_event)

    # Pie Chart - Disorder Types Distribution
    st.subheader("Disorder Types Proportion")
    disorder_type_count = df['disorder_type'].value_counts().reset_index()
    disorder_type_count.columns = ['disorder_type', 'count']
    fig_pie_disorder = px.pie(disorder_type_count, names='disorder_type', values='count',
                              title="Disorder Types Distribution")
    st.plotly_chart(fig_pie_disorder)


if __name__ == "__main__":
    main()
