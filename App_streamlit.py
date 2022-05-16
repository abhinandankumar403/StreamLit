import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


DATA_URL = ("A:\Projects\Motor_Vehicle_Collisions_-_Crashes.csv")
st.title("MOTOR VEHIVLE COLLISION DATA OF NEW YORK")
# FUNCTION FOR LOADING THE DATA
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH DATE','CRASH TIME']])
    #DROPPING NULL VALUES FTO SHOW DATA ON GEGRAPHICAL MAP
    #LATITUDE, LONGITUDE CAN NEVER BE NULL WHILE SHOWCASING DATA ON A GEOGRAPHICAL MAP[
    data.dropna(subset=['LATITUDE', 'LONGITUDE'],inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'CRASH DATE_CRASH TIME':'DATE/TIME'})
    return data

data = load_data(10000)
original_data = data
st.header("Where are most people injured in NYC")
injured_people = st.slider("Number of people injured in Vehicle Collisins",0,19)
st.map(data.query("`number of persons injured`>= @injured_people")[["latitude",'longitude']].dropna(how='any'))
st.header("How many collisions occur during a given time of day")
hour = st.sidebar.slider("Hour of the day",0,23)
data = data[data['crash date_crash time'].dt.hour==hour]
midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.markdown("Vehicle collsion between %i:00 and %i:00"%(hour,(hour+1) % 24))
st.write(pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
         initial_view_state={'latitude':midpoint[0],
                             'longitude':midpoint[1],
                             'zoom':11,
                             'pitch':50,},
         layers=[
             pdk.Layer(
                          "HexagonLayer",
                          data=data[['crash date_crash time',
                                     'latitude','longitude']],
                          get_position=['longitude','latitude'],
                          radius=100,
                          extruded=True,
                          pickable=True,
                          elevation_scale=4,
                          elevation_range=[0,1000],),],
         ))
# USING plotly.express FOR BAR GRAPH
st.subheader("Breakdown by minute between %i:00 and %i:00"%(hour,(hour+1)%24))
filtered = data[(data['crash date_crash time'].dt.hour>=hour)&data['crash date_crash time'].dt.hour<=(hour+1)]
hist = np.histogram(filtered['crash date_crash time'].dt.minute,bins=60,range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})
fig = px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

# USING select box FOR DATA VISUALIZATION
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people",['Pedestrian','Cyclists','Motorist'])
if select == 'Pedestrian':
    st.write(original_data.query('`number of pedestrians injured` >= 1')[
                 ['on street name','number of pedestrians injured']].sort_values(by=['number of pedestrians injured'],
                                                                                 ascending=False).dropna(how='any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query('`number of cyclist injured` >= 1')[
                 ['on street name', 'number of cyclist injured']].sort_values(by=['number of cyclist injured'],
                                                                                  ascending=False).dropna(how='any')[:5])
else:
    st.write(original_data.query('`number of motorist injured` >= 1')[
                 ['on street name', 'number of motorist injured']].sort_values(by=['number of motorist injured'],
                                                                                  ascending=False).dropna(how='any')[:5])
if st.checkbox("SHOW RAW DATA "):
    st.subheader("RAW HEADER")
    st.write(data)