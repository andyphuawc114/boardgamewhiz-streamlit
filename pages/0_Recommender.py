import pandas as pd
import streamlit as st
from distython import HEOM
from sklearn.neighbors import NearestNeighbors
from st_files_connection import FilesConnection
import gower

st.set_page_config(page_title="Recommendation",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Recommendation")
st.write(
    """This page recommends similar board games to the selected board game"""
)

# # bring the cache data from overview to this page
# raw_df = st.session_state['main_data']


@st.cache_resource(ttl=3600)
def get_game_data():
    conn = st.experimental_connection('gcs', type=FilesConnection)
    df = conn.read("boardgamewhiz-bucket/game_df.csv", input_format="csv", ttl=600)
    return df

# @st.cache_data(ttl=3600)
# def get_game_df(raw_df):
#     df = raw_df[raw_df['game_type'] == 'boardgame'].copy()
#     df = df[df['max_playtime'] != 0].copy()
#     df = df.drop(columns = ['rank','game_type','description','expansion','designer','artist','publisher',
#                             'reimplementation','user_rating','avg_rating','avg_rating_group','bayes_rating','std_dev', 'median','owned',
#                             'trading','wanting','wishing','num_comments','family_list', 'num_weights','playtime',
#                              'player_recommend','age_recommend'])
#     game_df = df.copy()
#     print(game_df.columns)
#     return game_df

game_df = get_game_data()

# game_attributes_df = game_df[['bgg_id','name','year','thumbnail']].copy()
# game_attributes_df['link'] = game_attributes_df['bgg_id'].apply(lambda x: "https://boardgamegeek.com/boardgame/" + str(x))

# FUNCTIONS TO CONVERT TO HTML TABLE
# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="60" >'

def path_to_url_html(ID):
    return '<a href="https://boardgamegeek.com/boardgame/' + str(ID) + '">' + str(ID) + "<" + "/" "a>"

@st.cache_data(ttl=3600)
def convert_df(input_df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return input_df.to_html(escape=False, formatters=dict(Image=path_to_image_html, ID=path_to_url_html))

# RECOMMENDATION ALGO
def find_games(game_df, selected_row, solo = None, year_after = None):
    fam = selected_row['family_group'].iloc[0]
    if fam != " ":
        game_df = game_df[game_df['family_group'] != fam]
    if solo:
        #print('Solo selected...')
        game_df = game_df[game_df['min_player'] == 1]
    if year_after:
        game_df = game_df[game_df['year'] >= year_after]
        
    processed_name = game_df[['name','bgg_id','year']]

    game_df = game_df.drop(columns = ['name','image','thumbnail','family_group','bgg_id','year','link'])
    selected_row = selected_row.drop(columns = ['name','image','thumbnail','family_group','bgg_id','year','link'])

    sim_measure = gower.gower_matrix(game_df, selected_row)
    idx = sim_measure.flatten().argsort()[:11]
    
    if fam != " ":
        final_idx = idx[1:11]
    else:
        final_idx = idx[0:11]
    game_idx = game_df.iloc[final_idx].index
    final_measure = sim_measure.flatten()[final_idx]
    game_measure = (1 - final_measure)[1:]

    return processed_name, game_idx, game_measure

games = game_df['name']
game_name = pd.DataFrame(game_df['name'])

row1_spacer1, row1_1, row1_spacer2 = st.columns((0.05, 0.9, 0.05))
with row1_1:
    selected_game = st.selectbox(
        "Select Board Game",
        (
        games
        ),
        index=None,
        placeholder="Select game...",
    )


st.text("")

row2_1, row2_spacer1, row2_2, row2_spacer2, row2_3 = st.columns((0.2, 0.05, 0.2, 0.05, 0.5))

run_algo = False

if selected_game:
    with row2_1:
        img_url = game_df[game_df['name'] == selected_game]['image'].values[0]
        st.image(img_url, width =200)

    with row2_2:
        game_id = game_df[game_df['name'] == selected_game]['bgg_id'].values[0]
        game_naming = game_df[game_df['name'] == selected_game]['name'].values[0]
        game_year = game_df[game_df['name'] == selected_game]['year'].values[0]

        st.write(f":envelope: **Game ID**: :black[{game_id}]")
        st.write(f":game_die: **Game Name**: :black[{game_naming}]")
        st.write(f":date: **Year Published**: :black[{game_year}]")

    with row2_3:
        if st.button("Click Me to Run Recommendation! :rocket:", type="primary"):
            run_algo = True

st.text("")

if selected_game and run_algo:
    with st.spinner('Recommendation In-Progress...'):
        index = game_name[game_name['name'] == selected_game].index[0]
        selected_row = game_df.loc[[index]]

        processed_name, final_idx, final_measure = find_games(game_df, selected_row, False)
        #recommended_df = processed_name.iloc[final_idx]

        final_df = game_df.iloc[final_idx][['bgg_id','name','year','thumbnail','link']].copy()
        final_df = final_df.rename({'bgg_id': 'ID', 'name': 'Game', 'year':'Year Published', 'thumbnail': 'Image', 'link':'URL'}, axis=1)

        html = convert_df(final_df)

        st.markdown(
        html,
        unsafe_allow_html=True)

        del final_df

    #st.dataframe(recommended_df, hide_index = True)

# TEMP JUST TO SHOW TOP 10 BOARD GAMES AS A TABLE

# st.write("Top 10 Board Games")

# selected_df = df.iloc[0:10].copy()
# selected_df['year'] = selected_df['year'].astype('str')
# selected_df = selected_df[['rank', 'bgg_id','name','year','thumbnail']]
# #selected_df['link'] = selected_df['bgg_id'].apply(lambda x: "https://boardgamegeek.com/boardgame/" + str(x))

# # Converting links to html tags
# def path_to_image_html(path):
#     return '<img src="' + path + '" width="60" >'

# def path_to_url_html(bgg_id):
#     return '<a href="https://boardgamegeek.com/boardgame/' + str(bgg_id) + '">' + str(bgg_id) + "<" + "/" "a>"

# @st.cache_data
# def convert_df(input_df):
#      # IMPORTANT: Cache the conversion to prevent computation on every rerun
#      return input_df.to_html(escape=False, formatters=dict(thumbnail=path_to_image_html, bgg_id=path_to_url_html))

# html = convert_df(selected_df)

# st.markdown(
#     html,
#     unsafe_allow_html=True
# )

