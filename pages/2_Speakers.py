# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:25:31 2023

@author: kaele
"""

import pandas as pd
import numpy as np
import plotly.express as px
import networkx as nx
import streamlit as st
from friends_functions import * 


speakers = st.container()

friends_data = pd.read_csv('data/friends_transcript_data.csv')

with speakers:
    st.title("The One Where You Find Out Whose Talking")
    unique_speakers = go.Figure()
    unique_speakers.add_trace(go.Indicator(
        mode = "number",
        value = len(list(friends_data['speaker'].unique())),
        title = {"text": "Total Unique Speakers"}))
    unique_speakers.update_layout(height = 400)

    st.plotly_chart(unique_speakers, use_container_width = True)
    st.subheader("Filter to get characters from specific episodes")
    col_1, col_2 = st.columns(2)
    season_choice = col_1.selectbox('Season:', options = get_seasons(), index = 0)
    episode_choice = col_2.selectbox('Episode:', options = get_episodes(season=season_choice), index = 0)
    
    st.subheader("Select a character to see their speaking history throughout the show")
    speaker_choice = st.multiselect('Character:', options= get_speakers(season_choice, episode_choice))
    
    if len(speaker_choice) > 0:
        fig = create_speaker_plot(speaker_choice)
        
        st.plotly_chart(fig, use_container_width = True)
        
        fig2 = create_speaker_bar(speaker_choice)
        
        st.plotly_chart(fig2, use_container_width = True)
    else:
        st.write("Select at least 1 character to display plots.")
