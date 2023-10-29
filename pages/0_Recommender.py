import pandas as pd
import streamlit as st

st.set_page_config(page_title="Recommendation",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Recommendation")
st.write(
    """This page is a trend visualizer to shows the trends and characteristics
    of various board games"""
)

df = st.session_state['main_data']

st.write("Top 10 Board Games")

selected_df = df.iloc[0:10].copy()
selected_df['year'] = selected_df['year'].astype('str')
selected_df = selected_df[['rank', 'bgg_id','name','year','thumbnail']]
#selected_df['link'] = selected_df['bgg_id'].apply(lambda x: "https://boardgamegeek.com/boardgame/" + str(x))

# Converting links to html tags
def path_to_image_html(path):
    return '<img src="' + path + '" width="60" >'

def path_to_url_html(bgg_id):
    return '<a href="https://boardgamegeek.com/boardgame/' + str(bgg_id) + '">' + str(bgg_id) + "<" + "/" "a>"

@st.cache_data
def convert_df(input_df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return input_df.to_html(escape=False, formatters=dict(thumbnail=path_to_image_html, bgg_id=path_to_url_html))

html = convert_df(selected_df)

st.markdown(
    html,
    unsafe_allow_html=True
)

# st.dataframe(selected_df, hide_index=True)
