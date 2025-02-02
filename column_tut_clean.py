import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk

st.title("Rental properties in New York City")

## function to get property locations and data
@st.cache(allow_output_mutation=True)
def get_df():
    new_df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonv4.csv', na_values= '#DIV/0!')
    new_df = new_df.dropna(axis=0, how='any')
    new_df = new_df[new_df["price"] < 10000]
    new_df = new_df[new_df["price"] > 999]
    new_df["solo_salary"] = new_df["price_per_bed"] / 0.025
    new_df["unit_salary"] = new_df["price"] / 0.025
    return new_df

new_df = get_df()


## shootings data
@st.cache
def get_crime():
    crime_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/NYPD_Shooting_Incident_Data__Year_To_Date_Clean.csv')
    crime_data.columns = crime_data.columns.str.lower()
    crime_data = crime_data.rename(columns={'longitude': 'lon', 'latitude': 'lat'})
    return crime_data

crime_data = get_crime()

## get tree data (massive file so needs to be cached)
@st.cache
def get_trees():
    tree_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/Forestry_Tree_Points_clean.csv')
    return tree_data

#tree_data = get_trees()


## colour scale for tree heat map
COLOR_BREWER_BLUE_SCALE = [
    [0,100,0],
    [34,139,34],
    [50,205,50],
    [152,251,152],
    [0,250,154],
    [32,178,170],
]

## for salary and affordability calcs, start at nyc average of 45k
salary = 45000

## this allows users to input their salary and filter the visible properties using this field
number = st.number_input("Insert your yearly salary")
if number == 0:
    salary = 0
else:
    salary = number

new_df["afford"] = np.where(new_df["price_per_bed"] < (salary/12) * 0.3, "affordable", "not affordable")

show_afford = st.checkbox("show only those properties avaialble to your budget")

if show_afford:
    new_df = new_df[new_df["afford"] == "affordable"]

    
with st.expander('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(new_df)
#print(df.info())


#st.map(new_df)

#st.map(df)
#data = df.to_json(orient='table')
#print(data)


## initial view state for pydeck
view = pdk.ViewState(
         latitude=40.65,
         longitude=-74.00,
         zoom=10,
         pitch=50,
     )

## properties map layer, height dictates cost, colour grade dictates proximity to metro
column_layer = pdk.Layer(
    "ColumnLayer",
    data=new_df,
    #data=crime_data,
    get_position=["lon", "lat"],
    get_elevation="price_per_bed_scale",
    elevation_scale=5,
    radius=100,
    #get_fill_color=[255, 100, 255, 255],
    #get_fill_color=["price_per_bed_scale ", "price_per_bed_scale / 8", "price_per_bed_scale", 255],
    get_fill_color=["100 / distance_between ", "distance_between", "100 / distance_between", 140],
    pickable=True,
    auto_highlight=True,
)

## shows tree coverage over the city
#tree_heat = pdk.Layer(
#     "HeatmapLayer",
#     data=tree_data,
#     #data=new_df,
#     opacity=0.9,
#     get_position=["lon", "lat"],
#     aggregation=pdk.types.String("MEAN"),
#     color_range=COLOR_BREWER_BLUE_SCALE,
#     threshold=1,
#     #get_weight="weight",
#     pickable=True,
# )

## not used
# crime_layer = pdk.Layer(
#     "ScatterplotLayer",
#     crime_data,
#     pickable=True,
#     opacity=0.8,
#     stroked=True,
#     filled=True,
#     radius_scale=5,
#     radius_min_pixels=1,
#     radius_max_pixels=100,
#     line_width_min_pixels=1,
#     get_position=["lon", "lat"],
#     get_radius=100,
#     get_fill_color=[255, 140, 0],
#     get_line_color=[0, 0, 0],
# )

## shows shooting concentration in the city
hex_layer = pdk.Layer(
    "HexagonLayer",
    crime_data,
    get_position=["lon", "lat"],
    auto_highlight=True,
    elevation_scale=0,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)

tooltip = {
    "html": "<b>${price_per_bed}</b> per bed, location: {borough} (<b>{lat}, {lon}</b>), <br/> Nearest metro: <b>{nearest_station}</b>, {distance_between}km away",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}




r_prop = pdk.Deck(
    #[column_layer, hex_layer],
    column_layer,
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)

# r_crime = pdk.Deck(
#     hex_layer,
#     initial_view_state=view,
#     tooltip=tooltip,
#     map_provider="mapbox",
#     map_style=pdk.map_styles.SATELLITE,
# )

#r_tree = pdk.Deck(
#     tree_heat,
#     initial_view_state=view,
#     map_provider="mapbox",
#     map_style=pdk.map_styles.SATELLITE
# )


st.pydeck_chart(r_prop)
st.write("_The elevation of the columns in the above chart indicate the price of the property. The colour gradient indicates how close the nearest metro station is, with darker colours being further away than the lighter pink_")

# with st.expander("Show shootings info"):
#     st.subheader('Police data on shootings in NYC in last year')
#     st.pydeck_chart(r_crime)

#st.subheader('Tree coverage in the city')
#st.pydeck_chart(r_tree)




