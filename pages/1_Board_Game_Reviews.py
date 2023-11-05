import numpy as np
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode

st.set_page_config(page_title="Board Game Reviews",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Reviews")
st.write(
    """This page shows the board game reviews"""
)

st.write("Board Games Reviews")

df = st.session_state['main_data'].copy()
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
        "Select Rating",
        (
        [0,1,2,3,4,5,6,7,8,9,10]
        ),
        index=None,
        placeholder="Select rating...",
    )

st.text("")

# GAME INFO TO MAKE SURE CORRECT SELECTION OF GAME BY USER

row2_1, row2_spacer2, row2_2 = st.columns((0.2, 0.05, 0.75))

with row2_1:
    if selected_game:
        img_url = df[df['name'] == selected_game]['image'].values[0]
        st.image(img_url, width =200)

with row2_2:
    if selected_game:
        game_id = df[df['name'] == selected_game]['bgg_id'].values[0]
        game_name = df[df['name'] == selected_game]['name'].values[0]
        game_year = df[df['name'] == selected_game]['year'].values[0]

        st.write(f":envelope: **Game ID**: :black[{game_id}]")
        st.write(f":game_die: **Game Name**: :black[{game_name}]")
        st.write(f":date: **Year Published**: :black[{game_year}]")


st.text("")

# UNCOMMENT BELOW TO TEST OR ONCE READY FOR PROD
# THIS IS TO PREVENT UNNECSSARY BIGQUERY

# if selected_game:
#     selected_bgg_id = int(selected_game.split(":")[0])

if selected_game and selected_sentiment:
    with st.spinner('Retrieving Reviews In-Progress...'):
        query  = f'''
        select ID, Game, Rating, Review, Sentiment, `Subjectivity Score`
        from (
        SELECT  cast(bgg_id as STRING) as ID, name as Game, rating as Rating, comment as Review, final_sentiment as Sentiment, 
        FORMAT('%.2F', round(subjectivity,2)) as `Subjectivity Score`
        FROM `tensile-walker-401308.eng_reviews.reviews` 
        where name = '{selected_game}' 
        and final_sentiment = '{selected_sentiment}'
        order by label_proba desc
        limit 10)
        '''
        reviews_df = pd.read_gbq(query, credentials = credentials)

#     st.dataframe(reviews_df, hide_index=True)

# TEST USING AGGRID FOR MORE CONTROL

    #Infer basic colDefs from dataframe types

        st.text("")
        st.write("*You can hover your mouse over the 'Review' text. A tooltip will display the full review text* :wink:")
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
        gridOptions = gb.build()
        
        grid_height = 380

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









