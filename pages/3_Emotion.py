# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:21:30 2023

@author: kaele
"""

import streamlit as st
from friends_functions import * 


header = st.container()
pie = st.container()

with header:
    st.title("The One With All The Emotion")
    
with pie:
    st.subheader("What emotions are the characters showing? ")
    
    col_1, col_2 = st.columns(2)
    season_choice = col_1.selectbox('Season:', options = get_seasons(), index = 0)
    episode_choice = col_2.selectbox('Episode:', options = get_episodes(season=season_choice), index = 0)
    
    st.subheader("Select a character to see the emotions they displayed in the selected episodes")
    speaker_choice = st.multiselect('Character:', options= get_speakers(season_choice, episode_choice))

    include_neutral = st.toggle("Include neutral")
    if len(speaker_choice) > 0:
        if include_neutral:
            st.plotly_chart(create_emotion_pie(season_choice,episode_choice,speaker_choice,include_neutral = True), use_container_width = True)
        else:
            st.plotly_chart(create_emotion_pie(season_choice,episode_choice,speaker_choice), use_container_width = True)
    else:
        st.write("Select minimum of 1 character to display chart")
