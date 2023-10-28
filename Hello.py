# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
from st_files_connection import FilesConnection
from st_pages import Page, show_pages, add_page_title
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="BoardGameWhiz",
    page_icon="👋",
    layout="wide"
)


LOGGER = get_logger(__name__)

@st.cache_resource
def get_data():
    conn = st.experimental_connection('gcs', type=FilesConnection)
    df = conn.read("boardgamewhiz-bucket/boardgames_cleaned.csv", input_format="csv", ttl=600)
    return df


df = get_data()

if 'main_data' not in st.session_state:
    st.session_state['main_data'] = df

# load data
#conn = st.experimental_connection('gcs', type=FilesConnection)
#df = conn.read("boardgamewhiz-bucket/boardgames.csv", input_format="csv", ttl=600)

st.write('''# BoardGameWhiz''')

st.write(":balloon: *Welcome to BoardGameWhiz - Translating Board Game Data into Insights!* 👋")

# rename the sidebar menu labelling
show_pages(
[
    Page("Hello.py", "Home"),
    Page('pages/0_Trends.py', "Recommendation"),
    Page('pages/0_Animation_Demo.py', "Animation"),
    Page('pages/1_Plotting_Demo.py', "Plot"),
    Page('pages/2_Mapping_Demo.py', "Map"),
    Page('pages/3_DataFrame_Demo.py', "DataFrame"),        
]
) 

#st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ### Introduction
    BoardGameWhiz is a user-centric board game visualizer built for the board game community.
    The data source is based on [boardgamegeek](https://boardgamegeek.com/)

    **👈 Select a demo from the sidebar** to navigage to other functions.
"""
)

row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.columns(
(0.1, 1, 0.1, 1, 0.1))


# LINE CHART TO SHOW USER RATINGS TREND
with row3_1:
    st.subheader("Average User Ratings Trend")
    df_ratings = df[['bgg_id', 'name', 'year', 'avg_rating']]
    df_ratings = df_ratings[(df_ratings['year'] >= 2000) & (df_ratings['year'] <= 2023)]
    df_ratings_avg = df_ratings.groupby('year')['avg_rating'].mean().reset_index()

    fig = px.line(df_ratings_avg, x="year", y="avg_rating",
            labels={"year": "Year Published","avg_rating": "Avg User Rating"})

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


# STACKED BAR CHART TO SHOW USER RATING BY GENRE
with row3_2:
    st.subheader("User Rating by Genre")

    df_genre = df[['bgg_id', 'name', 'year', 'avg_rating', 'abstracts', 'cgs', 'childrensgames', 'familygames', 'partygames', 'strategygames', 'thematic', 'wargames']]
    df_genre['avg_rating_group'] = df_genre['avg_rating'].apply(np.floor)
    df_genre = df_genre[df_genre['avg_rating'] > 0.00]
    df_genre = df_genre[['avg_rating_group','abstracts', 'cgs', 'childrensgames', 'familygames', 'partygames', 'strategygames', 'thematic', 'wargames']]
    genre_dict = {'abstracts': 'Abstract', 'cgs': 'Customizable', 'childrensgames': 'Children', 'familygames': 'Family', 'partygames': 'Party',
            'strategygames': 'Strategy', 'thematic': 'Thematic', 'wargames': 'War'}
    df_genre = df_genre.rename(genre_dict, axis = 1)
    df_genre_rating = df_genre.groupby('avg_rating_group').sum().reset_index()
    df_genre_rating = pd.melt(df_genre_rating, id_vars=['avg_rating_group'])
    fig = px.bar(df_genre_rating, x="avg_rating_group", y="value", color="variable",
        labels={"avg_rating_group": "User Rating","value": "Game Count", "variable": "Genre"})

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)        

# if __name__ == "__main__":
#     run(df)
