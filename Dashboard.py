import streamlit as st 
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import base64


st.set_page_config(page_title="Product Development!!!", page_icon=":bar_chart:", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# User authentication function
def login(username, password):
    # For demonstration purposes, using hardcoded credentials
    # In a real-world application, replace with a secure authentication mechanism
    if username == "admin" and password == "password":
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
    else:
        st.session_state['logged_in'] = False
        st.error("Invalid username or password")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

# Login interface
def login_screen():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        login(username, password)
        
# Function to load data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file format")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Main application interface
def main():
    
    st.subheader(":bar_chart: Streaming Platform Analysis Dashboard")
    
    # Load data
    df = pd.read_csv("streaming_platform_data2022.csv")
    
    # Custom CSS style
    custom_css = """
    <style>
    /* Add your custom CSS styles here */
    /* Styling for multi-select dropdown */
    .stMultiSelect {
        background-color: #f0f0f0;
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 3px;
    }
    .sidebar{
        width: 30px; 
        length: 100px; /* Adjust the width as needed */
    }
    /* Styling for date input */
    .stDateInput {
        background-color: #f0f0f0;
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 3px;
    }
    </style>
    """
    # Display custom CSS styles in sidebar
    st.sidebar.markdown(custom_css, unsafe_allow_html=True)

    # Streamlit layout
    st.sidebar.image("logo1.png")
    st.sidebar.header("Please Filter Here:")

    with st.sidebar:
        start_date = st.date_input("Start Date", pd.to_datetime(df["Date"]).min(), key="start_date_input")
        end_date = st.date_input("End Date", pd.to_datetime(df["Date"]).max(), key="end_date_input")

    with st.sidebar.expander("Choose the Sport"):
        Viewed_Sport = st.multiselect(
            "Choose the Sport:",
            options=df["Viewed_Sport"].unique(),
            default=df["Viewed_Sport"].unique(),
            key="sport_multiselect"
        )

    with st.sidebar.expander("Choose the Country"):
        Country = st.multiselect(
            "Choose the Country:",
            options=df["Country"].unique(),
            default=df["Country"].unique(),
            key="country_multiselect"
        )

    # Filter DataFrame based on user selection
    df["Date"] = pd.to_datetime(df["Date"])
    df_selection = df.query(
        "Country == @Country & Viewed_Sport == @Viewed_Sport & @start_date <= Date <= @end_date"
    )

    st.markdown("""
    <style>
    .column-container {
        display: flex;
        flex-wrap: wrap;
    }
    .column {
        border: 1px solid #ccc;
        padding: 10px;
        margin: 5px;
        flex: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    # Apply CSS to improve visualization
    st.markdown("""
    <style>
    .custom-title {
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        color: #333;
        margin-bottom: 20px;
    }
    .icon {
        margin-right: 10px;
        vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)

    

    # Top KPIs
    Countries = int(df_selection["Country"].nunique())
    Sport = int(df_selection["Viewed_Sport"].nunique())
    URL = int(df_selection["URL"].count())

    total_males = df_selection[df_selection["Gender"] == "Male"].shape[0]
    total_females = df_selection[df_selection["Gender"] == "Female"].shape[0]
    total_population = len(df_selection)
    average_males = (total_males / total_population) * 100
    average_females = (total_females / total_population) * 100

    left_column, middle_column, right_column, fourth_column = st.columns(4)
    with left_column:
        st.subheader("Countries:")
        st.markdown(f"<div class='metric'>{Countries:,}</div>", unsafe_allow_html=True)
    with middle_column:
        st.subheader("Total Visitors:")
        st.markdown(f"<div class='metric'>{URL:,}</div>", unsafe_allow_html=True)
    with right_column:
        st.subheader("Average Males:")
        st.markdown(f"<div class='metric'>{average_males:.2f}%</div>", unsafe_allow_html=True)
    with fourth_column:
        st.subheader("Average Females:")
        st.markdown(f"<div class='metric'>{average_females:.2f}%</div>", unsafe_allow_html=True)

    st.markdown("---")

    fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xls", "xlsx", "pdf"])
    if fl is not None:
        filename = fl.name
        st.write(filename)
        df = pd.read_csv(fl) 
    else:
        df = pd.read_csv("streaming_platform_data2022.csv")
          
      

    left_column, right_column = st.columns(2)

    URLs_by_Country = (df_selection.groupby(by=["Country"]).count().reset_index())
    URLs_by_Country_sorted = URLs_by_Country.sort_values(by="URL", ascending=False)
    top_ten_countries = URLs_by_Country_sorted.head(10)
    fig_urls_by_country = px.bar(
        top_ten_countries,
        x="Country",
        y="URL",
        orientation="v",
        title="<b>Number of Users by Country </b>",
        color_discrete_sequence=["#79ccb3"] * len(top_ten_countries),
        template="plotly_white",
    )
    fig_urls_by_country.update_layout(xaxis=(dict(showgrid=False)))

    sport_counts = df_selection['Viewed_Sport'].value_counts()
    fig_sport_counts = px.pie(names=sport_counts.index, values=sport_counts.values, title='Distribution of Users by Sports')

    df_selection["Date"] = pd.to_datetime(df_selection["Date"])
    time_series_data = df_selection.groupby(pd.Grouper(key="Date", freq="D"))["URL"].count().reset_index()
    fig_time_series = px.line(time_series_data, x="Date", y="URL", title='Number of users daily')
    fig_time_series.update_xaxes(title="Date")
    fig_time_series.update_yaxes(title="Number of URL")

    heatmap_data = df_selection.groupby(["Country", "Viewed_Sport"]).size().reset_index(name='Counts')
    heatmap_pivot = heatmap_data.pivot_table(index="Country", columns="Viewed_Sport", values="Counts", fill_value=0)
    country_sport_counts = heatmap_data.groupby('Country')['Counts'].sum().sort_values(ascending=False)
    top_10_countries = country_sport_counts.head(10).index
    heatmap_pivot_top_10 = heatmap_pivot.loc[top_10_countries]
    fig_heatmap = px.imshow(heatmap_pivot_top_10, labels=dict(x="Viewed Sport", y="Country"),
                           x=heatmap_pivot_top_10.columns, y=heatmap_pivot_top_10.index)

    sport_counts = df_selection.groupby(['Date', 'Viewed_Sport']).size().reset_index(name='Count')
    fig_line = px.line(sport_counts, x='Date', y='Count', color='Viewed_Sport',
                       title='Sport trend over time', labels={'Count': 'Number of Views'})

    country_counts = df_selection.groupby('Country').size().reset_index(name='Request Count')
    fig_map = px.choropleth(country_counts,
                            locations='Country',
                            locationmode='country names',
                            color='Request Count',
                            hover_name='Country',
                            color_continuous_scale='Blues',
                            title='Geographic Distribution of Visitors by Country')

    # Function to convert plotly bar chart data to CSV format
    def bar_chart_to_csv(fig):
        data = fig.data[0]
        x_values = data.x
        y_values = data.y
        df = pd.DataFrame({"Country": x_values, "Number of URLs": y_values})
        csv_string = df.to_csv(index=False)
        return csv_string

    # Function to convert plotly pie chart data to CSV format
    def pie_chart_to_csv(fig):
        names = fig.data[0].labels
        values = fig.data[0].values
        df = pd.DataFrame({"Sport": names, "User Count": values})
        csv_string = df.to_csv(index=False)
        return csv_string

    # Function to convert plotly line chart data to CSV format
    def line_chart_to_csv(fig):
        data = fig.data
        dfs = [pd.DataFrame({'Date': trace.x, 'Viewed_Sport': trace.name, 'Count': trace.y}) for trace in data]
        df = pd.concat(dfs, ignore_index=True)
        csv_string = df.to_csv(index=False)
        return csv_string

    # Function to convert plotly heatmap data to CSV format
    def heatmap_to_csv(fig):
        x_values = fig.layout.xaxis.ticks
        y_values = fig.layout.yaxis.ticks
        z_values = fig.data[0].z
        df = pd.DataFrame(z_values, columns=x_values, index=y_values)
        csv_string = df.to_csv(index=True)
        return csv_string

    # Function to convert plotly choropleth map data to CSV format
    def choropleth_to_csv(fig):
        data = fig.data[0]
        locations = data.locations
        names = data.hovertext
        values = data.z
        df = pd.DataFrame({"Country": names, "Request Count": values})
        csv_string = df.to_csv(index=False)
        return csv_string

    # Function to create a download link for CSV data
    def download_csv(csv_string, filename):
        csv_bytes = csv_string.encode()
        b64 = base64.b64encode(csv_bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
        return href

    left_column.plotly_chart(fig_urls_by_country)
    csv_data_urls_by_country = bar_chart_to_csv(fig_urls_by_country)
    left_column.markdown(download_csv(csv_data_urls_by_country, "urls_by_country_chart"), unsafe_allow_html=True)

    right_column.plotly_chart(fig_sport_counts)
    csv_data_sport_counts = pie_chart_to_csv(fig_sport_counts)
    right_column.markdown(download_csv(csv_data_sport_counts, "sport_counts_chart"), unsafe_allow_html=True)

    left_column.plotly_chart(fig_time_series)
    csv_data_time_series = line_chart_to_csv(fig_time_series)
    left_column.markdown(download_csv(csv_data_time_series, "time_series_chart"), unsafe_allow_html=True)

    right_column.plotly_chart(fig_heatmap)
    csv_data_heatmap = heatmap_to_csv(fig_heatmap)
    right_column.markdown(download_csv(csv_data_heatmap, "heatmap_chart"), unsafe_allow_html=True)

    left_column.plotly_chart(fig_line)
    csv_data_line = line_chart_to_csv(fig_line)
    left_column.markdown(download_csv(csv_data_line, "line_chart"), unsafe_allow_html=True)

    right_column.plotly_chart(fig_map)
    csv_data_map = choropleth_to_csv(fig_map)
    right_column.markdown(download_csv(csv_data_map, "map_chart"), unsafe_allow_html=True)

    st.markdown("---")

# Display login or main app based on authentication status
if st.session_state['logged_in']:
    st.sidebar.write(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        logout()
        st.experimental_rerun()
    main()
else:
    login_screen()
