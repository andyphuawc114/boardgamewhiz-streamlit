import pandas as pd
import streamlit as st
from st_files_connection import FilesConnection

def trend_visual():
    @st.cache_data
    def get_data():
        conn = st.experimental_connection('gcs', type=FilesConnection)
        df = conn.read("boardgamewhiz-bucket/boardgames.csv", input_format="csv", ttl=600)
        return df

    df = get_data()
    st.write(df.iloc[0]['name'])

st.set_page_config(page_title="Trends Visualizer", page_icon="📊")
st.markdown("# Trends")
st.write(
    """This page is a trend visualizer to shows the trends and characteristics
    of various board games"""
)

trend_visual()