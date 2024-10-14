import seaborn
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

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


def main():
    # Set page configuration to wide mode
    st.set_page_config(page_title="Armed Conflicts in Israel and Palestine (2016-2024)", layout="wide",
                       page_icon=":chart_with_upwards_trend:")

    st.title("Armed Conflicts in Israel and Palestine (2016-2024)")
    st.markdown("""
        This interactive data visualization project showcases incidents of armed conflict in Israeli and Palestinian territories. 
        Since 2016, the occurrence of these conflicts has nearly doubled each year, frequently taking place in densely populated areas. 
        Users can examine patterns in these armed conflicts by using the filters on the right side to see how various factors evolve over time. 
        This project is still under development, and I am continuously working to improve it. 
        My aim is to transform it into a valuable tool for understanding these conflicts and revealing underlying patterns. 

        You are welcome to contribute [here](https://github.com/ptrrrrk/Armed-Conflicts-in-Israel-and-Palestine-2016-2024/tree/main).

        **Data Source:** This data is sourced from the Armed Conflict Location & Event Data Project (ACLED) Curated Data Files. 
        ACLED provides real-time data on political violence and protest events around the world, making it a vital resource for understanding the dynamics of conflict.
        [ACLED Curated Data Files](https://acleddata.com/curated-data-files/)
    """)

    # Load the data
    df = load_data()

    # Sidebar filter options
    st.sidebar.header("Filter options")
    country_options = ["Palestine", "Israel", "Both"]
    selected_country = st.sidebar.selectbox("Select Country", options=country_options, index=2)  # Default to "Both"
    if selected_country == "Both":
        df = df[df['country'].isin(["Palestine", "Israel"])]
    else:
        df = df[df['country'] == selected_country]

    years = sorted(df['year'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(years[0]), max_value=int(years[-1]),
                                       value=(int(years[0]), int(years[-1])))
    df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

    disorder_types = st.sidebar.multiselect("Select Disorder Type", options=df['disorder_type'].unique(),
                                            default=df['disorder_type'].unique())
    event_types = st.sidebar.multiselect("Select Event Type", options=df['event_type'].unique(),
                                         default=df['event_type'].unique())
    df = df[df['disorder_type'].isin(disorder_types) & df['event_type'].isin(event_types)]

    # Calculate statistics
    total_events = len(df)
    unique_event_types = df['event_type'].nunique()
    unique_disorder_types = df['disorder_type'].nunique()
    average_events_per_year = total_events / (selected_years[1] - selected_years[0] + 1) if total_events > 0 else 0
    total_fatalities = df['fatalities'].sum() if 'fatalities' in df.columns else None
    most_frequent_event_type = df['event_type'].value_counts().idxmax() if total_events > 0 else None

    # Summary Display
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", f"{total_events}", help="Total number of recorded conflict events")
    col2.metric("Unique Event Types", f"{unique_event_types}", help="Number of distinct types of events")
    col3.metric("Unique Disorder Types", f"{unique_disorder_types}", help="Number of distinct disorder types")

    # Add an empty column for the second row
    st.markdown("---")  # Add a horizontal line separator
    st.write("")  # This creates an empty line between rows

    col4, col5, col6 = st.columns(3)
    col4.metric("Average Events per Year", f"{average_events_per_year:.2f}")
    col5.write(f"**Most Frequent Event Type: {most_frequent_event_type}**" if most_frequent_event_type else "No events")  # Empty column
    col6.metric("Total Fatalities", f"{total_fatalities}")



    visualize_data(df)
    st.subheader("Filtered Data")
    st.dataframe(df, use_container_width=True)


def visualize_data(df):
    # Map Visualization - Categorize by Event Type
    st.subheader("Incident Locations by Event Type")
    fig_map = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='location',
        hover_data=['event_type', 'notes'],
        color='event_type',
        color_discrete_sequence=px.colors.qualitative.Plotly,
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
    fig_line.update_layout(xaxis=dict(dtick=1))
    st.plotly_chart(fig_line)

    # Pie Chart - Event Types Distribution
    st.subheader("Event Types Proportion")
    event_type_count = df['event_type'].value_counts().reset_index()
    event_type_count.columns = ['event_type', 'count']
    fig_pie_event = px.pie(event_type_count, names='event_type', values='count', title="Event Types Distribution",
                           width=300, height=300)

    # Pie Chart - Disorder Types Distribution
    st.subheader("Disorder Types Proportion")
    disorder_type_count = df['disorder_type'].value_counts().reset_index()
    disorder_type_count.columns = ['disorder_type', 'count']
    fig_pie_disorder = px.pie(disorder_type_count, names='disorder_type', values='count',
                              title="Disorder Types Distribution", width=300, height=300)

    # Display pie charts in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie_event)
    with col2:
        st.plotly_chart(fig_pie_disorder)

    # Bar Chart - Civilian Fatalities by Event Type
    if 'civilian_fatalities' in df.columns:
        st.subheader("Civilian Fatalities by Event Type")
        civilian_fatalities_by_event = df.groupby('event_type')['civilian_fatalities'].sum().reset_index()
        fig_civilian = px.bar(civilian_fatalities_by_event, x='event_type', y='civilian_fatalities',
                              title="Civilian Fatalities by Event Type")
        st.plotly_chart(fig_civilian)



    # Variables list
    with st.expander("See the list of variables with explanation"):
        st.markdown('''
            - :red[event_id_cnty:] A unique identifier for the event within the country, combining the country code and event ID.
            - :red[event_date:] The date when the event occurred, formatted as YYYY.MM.DD.
            - :red[year:] The year of the event (e.g., 2024).
            - :red[time_precision:] Indicates the precision of the event date:
                - 1 = Exact date
                - 2 = Approximate date (e.g., within a few days)
                - 3 = Aggregated to a period (e.g., a month or a week).

            - :red[disorder_type:] Describes the type of disorder, such as "Political violence," "Demonstrations," "Riots," etc.
            - :red[event_type:] General categorization of the event, like "Riots," "Protests," "Violence against civilians," etc.
            - :red[sub_event_type:] Provides further detail about the event type (e.g., "Mob violence," "Violent demonstration").
            - :red[actor1:] The main actor or group initiating the event (e.g., "Rioters (Palestine)").
            - :red[assoc_actor_1]: An associated actor working with actor1, if any (e.g., "Muslim Group (Palestine)").
            - :red[inter1:] Interaction code for actor1, indicating their type or affiliation:
                For example, "1" could be for state forces, "2" for rebel groups, "3" for militias, etc.
            - :red[actor2:] The secondary actor involved in the event, often the opposing side or defender (e.g., "Military Forces of Israel (2022-)").
            - :red[assoc_actor_2:] An associated actor working with actor2, if any.
            - :red[inter2:] Interaction code for actor2, similar to inter1, indicating their type or affiliation.
            - :red[interaction:] Describes the type of interaction between actor1 and actor2. It’s a numeric code that combines the types of both actors (e.g., "Rioters-External/Other forces").
            - :red[civilian_targeting:] Indicates whether civilians were targeted in the event. If civilians are targeted, there may be additional information.
            - :red[iso:] The ISO country code (e.g., Israel (ISR), Palestine (PSE)).
            - :red[region:] The geographical region (e.g., "Middle East").
            - :red[country:] Name of the country related to the event.
            - :red[admin1:] Administrative region or area in the country.
            - :red[admin2:] Further administrative region or area in the country.
            - :red[admin3:] More granular administrative region or area in the country.
            - :red[location:] Specific location where the event took place (e.g., city or neighborhood).
            - :red[latitude:] Latitude coordinate for the event location.
            - :red[longitude:] Longitude coordinate for the event location.
            - :red[geo_precision:] A measure of how accurately the location is identified (e.g., "Exact," "Approximate").
            - :red[source:] Data source or reporting entity for the event (e.g., ACLED).
            - :red[source_scale:] Scale of the source reporting the event (e.g., local, national, international).
            - :red[notes:] Additional notes or context about the event.
            - :red[fatalities:] Total number of fatalities reported from the event.
            - :red[civilian_fatalities:] Number of civilian fatalities reported from the event (if available).
        ''')


if __name__ == "__main__":
    main()
