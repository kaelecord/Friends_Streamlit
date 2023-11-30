# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:21:31 2023

@author: kaele
"""

import streamlit as st
from friends_functions import * 


header = st.container()
char_network = st.container()

with header:
    st.title("The One Where You Find Out Who Talks to Who")
    
with char_network:
    st.subheader("How are the characters in Friends related?")
    st.write("Let's look at a character network to find out.")
    
    st.subheader("Select a season or episode to see the character network!")
    col_1, col_2 = st.columns(2)
    season_choice = col_1.selectbox('Season:', options = get_seasons(), index = 1)
    episode_choice = col_2.selectbox('Episode:', options = get_episodes(season=season_choice), index = 0)
    st.write("Select Characters you want to know more about (this will highlight them in the below network)")
    character_choice = st.multiselect('Character:', options= get_speakers(season_choice, episode_choice))
    if season_choice == "ALL" and episode_choice != "ALL":
        st.write("Invalid Input. Select full show, full season, or single episode.")
    else:
        st.plotly_chart(generate_network(season_choice, episode_choice, character_choice), use_container_width = True)
    