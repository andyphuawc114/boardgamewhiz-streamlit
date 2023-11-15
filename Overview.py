import streamlit as st
from streamlit.logger import get_logger
from st_files_connection import FilesConnection
from st_pages import Page, show_pages, add_page_title
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="BoardGameWhiz",
    page_icon="👋",
    layout="wide"
)


LOGGER = get_logger(__name__)

@st.cache_resource(ttl=3600)
def get_data():
    conn = st.experimental_connection('gcs', type=FilesConnection)
    df = conn.read("boardgamewhiz-bucket/boardgames_cleaned_20XX.csv", input_format="csv", ttl=600)
    return df

df = get_data()

# if 'main' not in st.session_state:
#     st.session_state['main'] = df

# load data
#conn = st.experimental_connection('gcs', type=FilesConnection)
#df = conn.read("boardgamewhiz-bucket/boardgames.csv", input_format="csv", ttl=600)

st.write('''# BoardGameWhiz''')

st.write(":balloon: *Welcome to BoardGameWhiz - Translating Board Game Data into Insights!* 👋")

# rename the sidebar menu labelling
show_pages(
[
    Page("Overview.py", "Overview"),
    Page('pages/0_Recommender.py', "Recommender"),
    Page('pages/1_Board_Game_Reviews.py', "Board Game Reviews")      
]
) 

#st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ### Introduction
    BoardGameWhiz is a user-centric board game visualizer built for the board game community.
    The data source is based on [boardgamegeek](https://boardgamegeek.com/)

    **👈 Select from the sidebar** to navigate to other functions.
"""
)

st.divider() 

st.markdown(
    """
    Below are visuals to show the popularity and trends in the board game industry.
    The board games are pre-filtered to those published between year 2000 to 2023 to examine the most recent trends.
    You can interact with the visuals by hovering over the data point, or zooming into specific part of the visuals
    for more focused analysis.
"""
)

@st.cache_data(ttl=3600)
def line_chart(df):
    df_ratings = df[['bgg_id', 'name', 'year', 'avg_rating']]
    #df_ratings = df_ratings[(df_ratings['year'] >= 2000) & (df_ratings['year'] <= 2023)]
    #df_ratings_avg = df_ratings.groupby('year')['avg_rating'].mean().reset_index()

    df_ratings_avg = df_ratings.groupby('year').agg(avg_rating=('avg_rating', np.mean),count_game=('year', 'count')).reset_index()

    # fig = px.line(df_ratings_avg, x="year", y="avg_rating",
    #         labels={"year": "Year Published","avg_rating": "Avg User Rating"})

    # fig.add_bar(x=df_ratings_avg["year"], y=df_ratings_avg["count_game"], name="Game Count")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig2 = px.line(df_ratings_avg, x="year", y="avg_rating",
             labels={"year": "Year Published","avg_rating": "Avg User Rating"})
    for t in fig2.select_traces():
        fig.add_trace(t, secondary_y = False)

    fig.add_trace(go.Bar(x = df_ratings_avg["year"], y = df_ratings_avg["count_game"], name="Game Count"), secondary_y = True)
    fig.update_yaxes(range=[4,6.8], secondary_y=False)
    fig.update_yaxes(range=[1000,10000], showgrid=False, secondary_y=True)

    fig.update_layout(legend=dict(
    yanchor="top",
    y=1.1,
    xanchor="left",
    x=0.01
    ))

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

@st.cache_data(ttl=3600)
def bar_chart(df):
    df_genre = df[['bgg_id', 'name', 'year', 'avg_rating','avg_rating_group', 'abstracts', 'cgs', 'childrensgames', 'familygames', 'partygames', 'strategygames', 'thematic', 'wargames']].copy()
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

@st.cache_data(ttl=3600)
def scatter_chart(df):
    df_weights = df[['bgg_id', 'name', 'year', 'avg_rating', 'avg_weights', 'user_rating']].copy()
    df_weights['avg_rating'] = df_weights['avg_rating'].round(2)
    df_weights['avg_weights'] = df_weights['avg_weights'].round(2)

    df_weights =  df_weights[df_weights['user_rating'] >= 1000]

    fig = px.scatter(df_weights, x="avg_weights", y="avg_rating", opacity=0.5, hover_data=['name','year','user_rating'], 
                 labels={"name":"Game","avg_weights": "Complexity","avg_rating": "Rating",'year':'Year','user_rating':'Votes'})

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)          

@st.cache_data(ttl=3600)
def heatmap(df):
    #new_df = df[(df['year'] >= 2000) & (df['year'] <= 2023)].copy()
    new_df = df.copy()
    my_col = new_df.columns[new_df.columns.str.contains('cat_')].to_list()
    my_col.append('year')
    new_df = new_df[my_col]

    # top 1000 games
    df_test = new_df.iloc[:1000].copy()

    col_to_delete = df_test.sum(axis=0, numeric_only = True).reset_index().rename({0:'value'}, axis = 1)
    col_to_delete = col_to_delete[col_to_delete['value'] == 0.0]['index'].to_list()
    col_to_delete = [i for i in col_to_delete if 'cat_' in i]
    df_matrix = df_test.drop(columns=col_to_delete)

    df_matrix.columns = df_matrix.columns.str.replace("cat_","")
    df_matrix = df_matrix.rename({'Industry / Manufacturing': 'Industry'}, axis = 1)
    df_matrix = df_matrix.groupby('year').sum()
    game_idx = df_matrix.sum().reset_index()
    fifty_idx = game_idx[game_idx[0] > 50]

    df_matrix = df_matrix[fifty_idx['index']]
    fig = px.imshow(df_matrix.T, labels={"x":"Year","y": "Category",'color':'Count'})
    fig.update_layout(yaxis_title=None, yaxis = dict(tickfont = dict(size=10)))

    #st.dataframe(df_matrix)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)   

row1_1, row1_space1, row1_2 = st.columns((0.45, 0.1, 0.45))

# LINE CHART TO SHOW USER RATINGS TREND
with row1_1:

    st.subheader("Average User Ratings Trend")
    line_chart(df)

# STACKED BAR CHART TO SHOW USER RATING BY GENRE
with row1_2:
    st.subheader("User Rating by Genre")
    bar_chart(df)

row2_1, row1_space1, row2_2 = st.columns((0.45, 0.1, 0.45))

# SCATTER PLOT CHART OF WEIGHT-RATING

with row2_1:
    st.subheader("Complexity-Rating Trend")
    scatter_chart(df)

with row2_2:
    st.subheader("Game Category Count")
    heatmap(df)


# if __name__ == "__main__":
#     run(df)
