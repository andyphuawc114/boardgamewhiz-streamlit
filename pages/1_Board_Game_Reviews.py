import numpy as np
import streamlit as st
import pandas as pd
from google.oauth2 import service_account

st.set_page_config(page_title="Recommendation",
                   page_icon="📊",
                   layout = 'wide')
st.markdown("# Board Game Recommendation")
st.write(
    """This page shows the board game reviews"""
)

st.write("Board Games Reviews")

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

query  = '''
SELECT  * FROM `tensile-walker-401308.eng_reviews.reviews` 
where bgg_id = 224517
LIMIT 10;
'''
new_df = pd.read_gbq(query, credentials = credentials)

st.dataframe(new_df, hide_index=True)
