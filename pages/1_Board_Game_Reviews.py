import numpy as np
import streamlit as st
import pandas as pd
from google.oauth2 import service_account

st.set_page_config(page_title="Board Game Reviews",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Reviews")
st.write(
    """This page shows the board game reviews"""
)

st.write("Board Games Reviews")

df = st.session_state['main_data'].copy()
df['bgg_name'] = df['bgg_id'].astype(str) + ": " + df['name']
bgg = df['bgg_name'].unique()

# QUERY FOR GAME REVIEWS BASED ON USER SELECTION

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)


row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4 = st.columns((0.05, 0.5, 0.05, 0.5, 0.05, 0.5, 0.05))
with row2_1:
    selected_game = st.selectbox(
        "Select Board Game",
        (
        bgg
        ),
        index=None,
        placeholder="Select game...",
    )

with row2_2:
    selected_sentiment = st.selectbox(
        "Select Sentiment",
        (
        ["Positive", "Negative", "Neutral-Positive", "Neutral-Negative"]
        ),
        index=None,
        placeholder="Select sentiment...",
    )

with row2_3:
    selected_rating = st.selectbox(
        "Select Rating",
        (
        [0,1,2,3,4,5,6,7,8,9,10]
        ),
        index=None,
        placeholder="Select rating...",
    )

# UNCOMMENT BELOW TO TEST OR ONCE READY FOR PROD
# THIS IS TO PREVENT UNNECSSARY BIGQUERY

if selected_game:
    selected_bgg_id = int(selected_game.split(":")[0])

if selected_game and selected_sentiment:
    query  = f'''
    select ID, Game, Rating, Review, Sentiment, `Subjectivity Score`
    from (
    SELECT  cast(bgg_id as STRING) as ID, name as Game, rating as Rating, comment as Review, final_sentiment as Sentiment, 
    FORMAT('%.2F', round(subjectivity,2)) as `Subjectivity Score`
    FROM `tensile-walker-401308.eng_reviews.reviews` 
    where bgg_id = {str(selected_bgg_id)}
    and final_sentiment = '{selected_sentiment}'
    order by label_proba desc
    LIMIT 10)
    '''

    reviews_df = pd.read_gbq(query, credentials = credentials)

    st.dataframe(reviews_df, hide_index=True)
