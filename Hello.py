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
import pandas as pd

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="BoardGameWhiz",
        page_icon="👋",
    )

    conn = st.experimental_connection('gcs', type=FilesConnection)
    df = conn.read("boardgamewhiz-bucket/boardgames.csv", input_format="csv", ttl=600)
    st.write(":balloon: # Welcome to BoardGameWhiz! 👋")
    #st.write(df.iloc[0]['name'])
    
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        ### Introduction
        BoardGameWhiz is a user-centric board game visualizer built for the board game community.
        The data source is based on [boardgamegeek](https://boardgamegeek.com/)

        **👈 Select a demo from the sidebar** to navigage to other functions.
    """
    )


if __name__ == "__main__":
    run()
