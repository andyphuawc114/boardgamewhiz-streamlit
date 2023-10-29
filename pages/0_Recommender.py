import pandas as pd
import streamlit as st
from distython import HEOM
from sklearn.neighbors import NearestNeighbors

st.set_page_config(page_title="Recommendation",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Recommendation")
st.write(
    """This page recommends similar board games to the selected board game"""
)

# bring the cache data from overview to this page
raw_df = st.session_state['main_data']

@st.cache_data
def get_game_df(raw_df):
    df = raw_df[raw_df['game_type'] == 'boardgame'].copy()
    df = df[df['max_playtime'] != 0].copy()
    df = df.drop(columns = ['rank','game_type','image','description','expansion','designer','artist','publisher',
                            'reimplementation','user_rating','avg_rating','bayes_rating','std_dev', 'median','owned',
                            'trading','wanting','wishing','num_comments','family_list', 'num_weights','playtime'])
    game_df = df.copy()
    print(game_df.columns)
    return game_df

game_df = get_game_df(raw_df)

game_attributes_df = game_df[['bgg_id','name','year','thumbnail']]
game_attributes_df['link'] = game_attributes_df['bgg_id'].apply(lambda x: "https://boardgamegeek.com/boardgame/" + str(x))

# FUNCTIONS TO CONVERT TO HTML TABLE
# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="60" >'

def path_to_url_html(ID):
    return '<a href="https://boardgamegeek.com/boardgame/' + str(ID) + '">' + str(ID) + "<" + "/" "a>"

@st.cache_data
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
        
    game_df = pd.concat([game_df, selected_row])
    processed_name = game_df[['name','bgg_id','year']]
    game_df = game_df.drop(columns = ['name','family_group','bgg_id','year','thumbnail'])
    selected_row = selected_row.drop(columns = ['name','family_group','bgg_id','year','thumbnail'])
    
    nan_eqv = 9999
    categorical_ix = [i+6 for i in range(284)]
    game_df = game_df.fillna(9999)
    heom_metric = HEOM(game_df, categorical_ix, nan_equivalents = [nan_eqv])
    neighbor = NearestNeighbors(metric = heom_metric.heom)
    neighbor.fit(game_df)
    result = neighbor.kneighbors(selected_row, n_neighbors=12)
    
    # print(result[0][0])
    # print(result[1][0])
    
    if fam != " ":
        final_idx = result[1][0][0:11]
        final_measure = result[0][0][0:11]
    else:
        final_idx = result[1][0][1:12]
        final_measure = result[0][0][1:12]

    return processed_name, final_idx, final_measure

games = game_df['name']
game_name = pd.DataFrame(game_df['name'])

row2_spacer1, row2_1, row2_spacer2 = st.columns((0.05, 0.5, 0.05))
with row2_1:
    selected_game = st.selectbox(
        "Select Board Game",
        (
        games
        ),
        index=None,
        placeholder="Select game...",
    )

if selected_game:
    index = game_name[game_name['name'] == selected_game].index[0]
    selected_row = game_df.loc[[index]]

    processed_name, final_idx, final_measure = find_games(game_df, selected_row, False)
    recommended_df = pd.concat([processed_name.iloc[final_idx],pd.DataFrame(final_measure).set_index(processed_name.iloc[final_idx].index)], axis = 1)

    final_df = game_attributes_df[game_attributes_df['bgg_id'].isin(recommended_df['bgg_id'].to_list())].copy()
    final_df = final_df.rename({'bgg_id': 'ID', 'name': 'Game', 'year':'Year Published', 'thumbnail': 'Image', 'link':'URL'}, axis=1)

    html = convert_df(final_df)

    st.markdown(
    html,
    unsafe_allow_html=True)

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

