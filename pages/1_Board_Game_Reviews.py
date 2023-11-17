import numpy as np
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, ColumnsAutoSizeMode
from st_files_connection import FilesConnection
import gc

st.set_page_config(page_title="Board Game Reviews",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Reviews")
st.write(
    """This page shows the board game reviews. Although board game reviews are tagged with a user rating,
    the numerical rating of a review may not necessarily represent the true sentiment. 
    We hope that this will aid users to better discover the reviews 
    which are most relevant to their perferences. The sentiment analysis is performed using a [Sentence Transformer](https://github.com/huggingface/setfit) model
    with transfer learning based on the reviews. 
    We labelled the reviews with four classes: Positive, Negative, Neutral-Positive, and Neutral-Negative.
"""
)


st.write(" ")

@st.cache_resource(ttl=3600)
def get_game_data():
    conn = st.experimental_connection('gcs', type=FilesConnection)
    df = conn.read("boardgamewhiz-bucket/game_info_reviews.csv", input_format="csv", ttl=600)
    return df

df = get_game_data()

#df['bgg_name'] = df['bgg_id'].astype(str) + ": " + df['name']
bgg = df['name'].unique()

# QUERY FOR GAME REVIEWS BASED ON USER SELECTION

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)


row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3, row1_3, row1_spacer4 = st.columns((0.05, 0.5, 0.05, 0.5, 0.05, 0.5, 0.05))
with row1_1:
    selected_game = st.selectbox(
        "Select Board Game",
        (
        bgg
        ),
        index=None,
        placeholder="Select game...",
    )

with row1_2:
    selected_sentiment = st.selectbox(
        "Select Sentiment",
        (
        ["Positive", "Negative", "Neutral-Positive", "Neutral-Negative"]
        ),
        index=None,
        placeholder="Select sentiment...",
    )

with row1_3:
    selected_rating = st.selectbox(
        "Select Rating (Optional)",
        (
        ['0','1','2','3','4','5','6','7','8','9','10']
        ),
        index=None,
        placeholder="Select rating...",
    )

st.text("")

# GAME INFO TO MAKE SURE CORRECT SELECTION OF GAME BY USER

run_algo = False

row2_1, row2_spacer1, row2_2, row2_spacer2, row2_3 = st.columns((0.2, 0.05, 0.2, 0.05, 0.5))

if selected_game:
    with row2_1:
        img_url = df[df['name'] == selected_game]['image'].values[0]
        st.image(img_url, width =200)

    with row2_2:
        game_id = df[df['name'] == selected_game]['bgg_id'].values[0]
        game_name = df[df['name'] == selected_game]['name'].values[0]
        game_year = df[df['name'] == selected_game]['year'].values[0]

        st.write(f":envelope: **Game ID**: :black[{game_id}]")
        st.write(f":game_die: **Game Name**: :black[{game_name}]")
        st.write(f":date: **Year Published**: :black[{game_year}]")

    with row2_3:
        if st.button("Click Me to Retrieve Reviews! :rocket:", type="primary"):
            if selected_sentiment:
                run_algo = True       
            else:
                "You need to select a \"Sentiment\" first :open_mouth:"


st.text("")

# UNCOMMENT BELOW TO TEST OR ONCE READY FOR PROD
# THIS IS TO PREVENT UNNECSSARY BIGQUERY

# if selected_game:
#     selected_bgg_id = int(selected_game.split(":")[0])

if selected_game and selected_sentiment and run_algo:

    if selected_rating:
        query  = f'''
        select ID, Game, Rating, Review, Sentiment, `Subjectivity Score`
        from (
        SELECT  cast(bgg_id as STRING) as ID, name as Game, rating as Rating, comment as Review, final_sentiment as Sentiment, 
        FORMAT('%.2F', round(subjectivity,2)) as `Subjectivity Score`
        FROM `tensile-walker-401308.eng_reviews.reviews` 
        where name = '{selected_game}' 
        and final_sentiment = '{selected_sentiment}'
        and cast(rating_group as string) = '{selected_rating}'
        order by label_proba desc)
        '''
    else:
        query  = f'''
        select ID, Game, Rating, Review, Sentiment, `Subjectivity Score`
        from (
        SELECT  cast(bgg_id as STRING) as ID, name as Game, rating as Rating, comment as Review, final_sentiment as Sentiment, 
        FORMAT('%.2F', round(subjectivity,2)) as `Subjectivity Score`
        FROM `tensile-walker-401308.eng_reviews.reviews` 
        where name = '{selected_game}' 
        and final_sentiment = '{selected_sentiment}'
        order by label_proba desc)
        '''
    with st.spinner('Retrieving Reviews In-Progress...'):
        reviews_df = pd.read_gbq(query, credentials = credentials)

#     st.dataframe(reviews_df, hide_index=True)

# TEST USING AGGRID FOR MORE CONTROL

    #Infer basic colDefs from dataframe types

        st.text("")
        
        gb = GridOptionsBuilder.from_dataframe(reviews_df)
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)

        #gb.configure_default_column(tooltipField="Review")
        gb.configure_column(field="Review", maxWidth=400, tooltipField="Review", tooltipComponent = JsCode("""
                                                            class CustomTooltip {
                                                                eGui;
                                                                init(params) {
                                                                    const eGui = (this.eGui = document.createElement('div'));
                                                                    const color = params.color || 'black';
                                                                    const data = params.api.getDisplayedRowAtIndex(params.rowIndex).data;
                                                                    eGui.classList.add('custom-tooltip');
                                                                    //@ts-ignore
                                                                    eGui.style['background-color'] = color;
                                                                    eGui.style['color'] = 'white';     
                                                                    eGui.style['padding'] = "5px 5px 5px 5px";  
                                                                    eGui.style['font-size'] = "15px";                                         
                                                                    eGui.style['border-style'] = 'double';                                                             
                                                                    this.eGui.innerText = data.Review;
                                                                }
                                                                getGui() {
                                                                    return this.eGui;
                                                                }
                                                                }"""))
        
        gb.configure_grid_options(domLayout='normal')
        gb.configure_columns("Review",wrapText = True,cellStyle= {"wordBreak": "normal"})
        gb.configure_columns("Review",autoHeight = True)
        gridOptions = gb.build()
        
        grid_height = 700

        st.write("*You can hover your mouse over the 'Review' text. A tooltip will display the full review text* :wink:")
        st.text("")

        grid_response = AgGrid(
            reviews_df, 
            gridOptions=gridOptions,
            height=grid_height, 
            width='100%',
            fit_columns_on_grid_load=False,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,   # FIT_ALL_COLUMNS_TO_VIEW
            allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
            custom_css={"#gridToolBar": {"padding-bottom": "0px !important"}}
            )

        del reviews_df
        gc.collect()








