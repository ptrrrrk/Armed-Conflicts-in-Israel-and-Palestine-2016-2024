import seaborn
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
from PIL import Image

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
        This interactive data visualization project showcases incidents of armed conflicts in Israeli and Palestinian territories. 
        Since 2016, the occurrence of these conflicts has nearly doubled each year, frequently taking place in densely populated areas. 
        Users can examine patterns in these armed conflicts by using the filters on the right side to see how various factors evolve over time. 
        This project is still under development, and I am continuously working to improve it. 
        My aim is to transform it into a valuable tool for understanding these conflicts and revealing underlying patterns. 

        You are welcome to contribute [here](https://github.com/ptrrrrk/Armed-Conflicts-in-Israel-and-Palestine-2016-2024).

        **Data Source:** This data is sourced from the Armed Conflict Location & Event Data Project (ACLED) Curated Data Files. 
        ACLED provides real-time data on political violence and protest events around the world, making it a vital resource for understanding the dynamics of conflict.
        [ACLED Curated Data Files](https://acleddata.com/curated-data-files/)
    """)

    # Load the data
    df = load_data()

    # Sidebar filter options
    st.sidebar.header("Filter options")
    country_options = ["Palestine", "Israel", "Israel and Palestine"]
    selected_country = st.sidebar.selectbox("Select Country", options=country_options, index=2)  # Default to "Both"
    if selected_country == "Israel and Palestine":
        df = df[df['country'].isin(["Palestine", "Israel"])]
    else:
        df = df[df['country'] == selected_country]

    years = sorted(df['year'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(years[0]), max_value=int(years[-1]),
                                       value=(int(years[0]), int(years[-1])))
    df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

    event_types = st.sidebar.multiselect("Select Event Type", options=df['event_type'].unique(),
                                         default=df['event_type'].unique())
    df = df[df['event_type'].isin(event_types)]

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

    # Second row of summary statistics
    col4, col5, col6 = st.columns(3)
    col4.empty()  # Empty column for alignment purposes
    col5.metric("Total Fatalities", f"{total_fatalities}")
    col6.metric("Average Events per Year", f"{average_events_per_year:.2f}")

    # Display the most frequent event type
    st.write(f"**Most Frequent Event Type: {most_frequent_event_type}**" if most_frequent_event_type else "No events")

    # Visualize data
    visualize_data(df)

    st.subheader("Filtered Data")
    st.dataframe(df, use_container_width=True)

    # Add GitHub link and creator info at the bottom of the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="text-align: center;">'
        '<a href="https://github.com/ptrrrrk/Armed-Conflicts-in-Israel-and-Palestine-2016-2024">'
        '<img src="https://1000logos.net/wp-content/uploads/2021/05/GitHub-logo.png" width="100" height="60" style="display:inline-block; vertical-align:middle;"/>'
        '</a><br>'
        'Made by K. Patrik'
        '</div>', unsafe_allow_html=True
    )

def visualize_data(df):
    # Map Visualization - Categorize by Event Type
    st.subheader("Incident Locations by Event Type")
    df['hover_text'] = df['location'] + '<br>' + df['event_type'] + '<br>' + df['notes']

    fig_map = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='hover_text',
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
    st.plotly_chart(fig_pie_event)

    # Bar Chart of Fatalities vs. Events by Location
    st.subheader("Fatalities by Location")
    bar_data = df.groupby(['location', 'country']).agg({'event_id_cnty': 'count', 'fatalities': 'sum'}).reset_index()
    bar_data.rename(columns={'event_id_cnty': 'Event Count'}, inplace=True)

    fig_bar = px.bar(bar_data, x='location', y='fatalities', text='Event Count',
                     color='country',
                     color_discrete_map={'Israel': 'blue', 'Palestine': 'red'},
                     width=800, height=600)
    st.plotly_chart(fig_bar)

    # Variables list
    with st.expander("See the list of variables with explanation"):
        st.markdown('''
            - :red[event_id_cnty:] A unique identifier for the event within the country, combining the country code and event ID.
            - :red[event_date:] The date when the event occurred, formatted as YYYY.MM.DD.
            - :red[year:] The year in which the event took place.
            - :red[time_precision:] The precision of the event's timestamp, such as "date" or "month".
            - :red[disorder_type:] The category of disorder represented by the event.
            - :red[event_type:] The nature of the event, indicating the type of conflict or violence that occurred.
            - :red[sub_event_type:] More specific classification within the main event type.
            - :red[actor1:] The primary actor involved in the event.
            - :red[assoc_actor_1:] Any associated actors with the primary actor.
            - :red[inter1:] Any international actors associated with the primary actor.
            - :red[actor2:] The second actor involved in the event.
            - :red[assoc_actor_2:] Any associated actors with the second actor.
            - :red[inter2:] Any international actors associated with the second actor.
            - :red[interaction:] The type of interaction between the actors.
            - :red[civilian_targeting:] Indicates if civilians were targeted during the event.
            - :red[iso:] The ISO country code for the location.
            - :red[region:] The broader region where the event occurred.
            - :red[country:] The country where the event took place.
            - :red[admin1:] The first-level administrative division within the country.
            - :red[admin2:] The second-level administrative division.
            - :red[admin3:] The third-level administrative division.
            - :red[location:] The specific place where the event occurred.
            - :red[latitude:] The latitude of the event's location.
            - :red[longitude:] The longitude of the event's location.
            - :red[geo_precision:] The precision of the geographical data.
            - :red[source:] The source of the event information.
            - :red[source_scale:] The scale of the source, indicating its geographic focus.
            - :red[notes:] Additional details and context about the event.
            - :red[fatalities:] The number of deaths associated with the event.
        ''')

if __name__ == '__main__':
    main()
