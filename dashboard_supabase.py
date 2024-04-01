import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px

from streamlit_option_menu import option_menu
from custom_dynamic_filters import DynamicFilters
#from streamlit_file_browser import st_file_browser
from st_supabase_connection import SupabaseConnection


from graphviz import Digraph

st.set_page_config(layout="wide")

# Assuming Supabase connection is set up like this
conn = st.connection("supabase", type=SupabaseConnection)



with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Throughput", "Workforce Allocation", "Utilization"],
        icons=["bar-chart-steps", "gear", "folder"],
        menu_icon="menu-app",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": '#256b6d'},
        }
    )

def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)

custom_css = """
<style>
    .st-bo {
        background-color: #256b6d !important;
    }
    [data-baseweb="select"] .st-b6 {
        color: white; /* Attempting to target the displayed value */
        background-color: #256b6d
    }
</style>


"""

st.markdown(custom_css, unsafe_allow_html=True)

# Function to fetch data from Supabase
#def fetch_data(table_name):
    #return pd.DataFrame(conn.query("*", table=table_name, ttl="10m").execute())

def fetch_data(table_name):
    # Execute the query to fetch data from the specified Supabase table
    response = conn.query("*", table=table_name, ttl="10m").execute()

    # Directly work with the .data attribute, assuming it's a list of dictionaries
    if hasattr(response, 'data') and isinstance(response.data, list):
        return pd.DataFrame(response.data)
    else:
        # Log an error or handle the case where data is not as expected
        print("Unexpected response format or no data found.")
        return pd.DataFrame()


if selected == "Throughput":

    st.title(f":grey[{selected} Analysis]")

    df = fetch_data("ch1_bags_count_prod")
    #print(df)
    #print(df.head())
    #df = df.sort_values(by='Variant Rank', ascending=True)

    # Ensure the time column is datetime format
    df["time"] = pd.to_datetime(df["time"])


    #df_filtered= df.loc[df['time_column'].between(start_datetime, end_datetime)]
    df_filtered= df


    dynamic_filters = DynamicFilters(df_filtered, filters=['color', 'section'], identifier='set1')
    #dynamic_filters.set_default_values({'machine': "M001"})
    dynamic_filters.display_filters(location='columns', num_columns=2, gap='large')
    #dynamic_filters.set_default_values({'Variant Rank': "1"})


    color_filter_value = dynamic_filters.get_filter_value('color')[0] if dynamic_filters.get_filter_value('color') else None
    section_filter_value = dynamic_filters.get_filter_value('section')[0] if dynamic_filters.get_filter_value('section') else None

    #image_placeholder = st.empty()
    '''
    if color_filter_value and section_filter_value:
        #image_filename = f'data/{machine_filter_value}__{variant_filter_value}.png'

        kpi1, kpi2, kpi3 = st.columns(3)

        avg_duration = np.mean(dynamic_filters.filter_df()['Duration (Seconds)'])/60
        avg_duration_all = np.mean(df['Duration (Seconds)'])/60

        filtered_count = dynamic_filters.filter_df()['Case ID'].count()
        all_count = df['Case ID'].count()

        kpi1.metric(label="Duration (Min) ", value=round(avg_duration,1), delta= round(avg_duration_all,1))
        kpi2.metric(label="Variants ", value= round(filtered_count), delta=round(all_count))

        fig_col1, fig_col0, fig_col2 = st.columns([3,1.5,2])
        with fig_col1:
            df_filtered = dynamic_filters.filter_df()
            df_filtered['Duration (Minutes)'] = df_filtered['Duration (Seconds)'] / 60
            fig2 = px.histogram(
                data_frame=df_filtered,
                x='Duration (Minutes)',
                nbins=20,
                color_discrete_sequence=['#256b6d'],
                marginal="rug",
            )
            fig2.update_traces(marker=dict(line=dict(width=1, color='#0f3d3e')))
            fig2.update_layout(
                title="Cycle Duration Histogram",
                xaxis_title="Duration (Minutes)",
                yaxis_title="Count",
                dragmode='pan'
            )
            st.write(fig2)


        with fig_col2:

            st.markdown("<h6>Process Map</h6>", unsafe_allow_html=True)

            #st.markdown("Process Map")
            #print(dynamic_filters.filter_df()['Variant'])
            filtered_variant = str(dynamic_filters.filter_df()['Variant'].iloc[0])
            #st.header(f'Variant Rank 1 Flow Diagram for {machine_filter_value}')
            diagram = create_variant_diagram(filtered_variant)
            st.graphviz_chart(str(diagram))
            #st.image(image_filename)
    '''

    st.markdown("### Detailed Data View")
    dynamic_filters.display_df()

elif selected == "Steps":
    st.title(f":grey[{selected} Analysis]")

    # Define the machine options for the selector
    machine_options = ["M001", "M002", "M003"]

    # Use st.selectbox to let the user choose a machine.
    # Set "M001" as the default option by specifying index=0, since "M001" is the first item in the list.
    selected_machine = st.selectbox("Select a machine:", machine_options, index=0)

    # Map machine filter value to Supabase table names
    table_map = {
        "M001": "M001_Data",
        "M002": "M002_Data",
        "M003": "M003_Data",
    }

    table_name = table_map.get(selected_machine)
    #print(table_name)

    df = fetch_data(table_name)
    df = df.sort_values(by='Variant Rank', ascending=True)
    #print(df)
    # Display the dynamic filters
    dynamic_filters2 = DynamicFilters(df, filters=['Variant Rank','concept:name'], identifier='set2')
    #dynamic_filters2.set_default_values({'Variant Rank': "1"})
    #print(dynamic_filters2)

    dynamic_filters2.display_filters(location='columns', num_columns=2, gap='large')

    if table_name:
        # Query data from Supabase
        response = conn.query("*", table=table_name, ttl="10m").execute()
        df = pd.DataFrame(response.data)
    else:
        st.error("Invalid machine selection.")
        df = pd.DataFrame()

    if df.empty:
        st.write("No data available for the selected machine.")
    else:
        variant_filter_value = dynamic_filters2.get_filter_value('Variant Rank')[0] if dynamic_filters2.get_filter_value(
            'Variant Rank') else None

        # Here we add KPIs and visualization code
        filtered_df = dynamic_filters2.filter_df()
        avg_duration = np.mean(filtered_df['Duration (Seconds)']) / 60
        avg_duration_all = np.mean(df['Duration (Seconds)']) / 60
        filtered_count = filtered_df['Case ID'].count()
        all_count = df['Case ID'].count()

        # Creating KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Average Duration (Min)", value=f"{avg_duration:.2f}")
        kpi2.metric(label="Filtered Variants Count", value=f"{filtered_count}")
        kpi3.metric(label="Total Variants Count", value=f"{all_count}")


        # Example histogram for cycle durations
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:

            variant_rank_filter_values = dynamic_filters2.get_filter_value('Variant Rank') if dynamic_filters2.get_filter_value('Variant Rank') else None
            if variant_rank_filter_values:
                for i,variant_rank in enumerate(variant_rank_filter_values):
                    st.markdown(f"<h6>Process Map {variant_rank} </h6>", unsafe_allow_html=True)
                    # st.markdown("Process Map")
                    # print(dynamic_filters.filter_df()['Variant'])
                    filtered_variant_text = str(filtered_df[filtered_df['Variant Rank'] == variant_rank]['Variant'].iloc[0])
                    print(filtered_variant_text)
                    # st.header(f'Variant Rank 1 Flow Diagram for {machine_filter_value}')
                    diagram = create_variant_diagram(filtered_variant_text)
                    st.graphviz_chart(str(diagram))
            else:
                count_filtered_variants = filtered_df['Variant Rank'].unique().shape[0]
                if count_filtered_variants >= 3:
                    variant_rank_show_graph = filtered_df['Variant Rank'].unique()[:3]
                else:
                    variant_rank_show_graph = filtered_df['Variant Rank'].unique()
                    print(variant_rank_show_graph)

                for variant_rank in variant_rank_show_graph:  # Corrected iteration here
                    st.markdown(f"<h6>Process Map {variant_rank} </h6>", unsafe_allow_html=True)
                    # Make sure to filter the DataFrame safely
                    filtered_variant_df = filtered_df[filtered_df['Variant Rank'] == variant_rank]
                    if not filtered_variant_df.empty:
                        filtered_variant_text = str(filtered_variant_df['Variant'].iloc[0])
                        # Here you can include your logic for creating and displaying the diagram
                        diagram = create_variant_diagram(filtered_variant_text)
                        st.graphviz_chart(str(diagram))
                    else:
                        st.markdown(f"<h6>No data available for Variant Rank {variant_rank}.</h6>",
                                    unsafe_allow_html=True)

        with fig_col2:

            step_filter_values = dynamic_filters2.get_filter_value('concept:name') if dynamic_filters2.get_filter_value('concept:name') else None

            if not filtered_df.empty:

                steps_to_graph = filtered_df['concept:name'].unique()

                for i, step in enumerate(steps_to_graph):
                    filtered_df_and_by_step= filtered_df[filtered_df['concept:name']== step]
                    filtered_df_and_by_step['Duration (Minutes)']= filtered_df_and_by_step['Duration (Seconds)']/60
                    fig = px.histogram(filtered_df_and_by_step, x='Duration (Minutes)', nbins=20, title=f'{step} Duration Distribution',
                                   color_discrete_sequence=['#256b6d'])
                    st.plotly_chart(fig, use_container_width=True)

        # Display detailed data view
        st.markdown("### Detailed Data View")
        dynamic_filters2.display_df()
elif selected == "Reports":
    st.title(f":grey[{selected}]")
    event = st_file_browser("reports")

# Note: Remember to replace placeholders and assumptions with your actual
