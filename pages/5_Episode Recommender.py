# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:33:26 2023

@author: kaele
"""

import streamlit as st
from friends_functions import * 


header = st.container()
rec_sys1 = st.container()
rec_sys2 = st.container()
rec_sys3 = st.container()
rec_sys4 = st.container()


with header:
    st.title("The One Where We Tell You What To Watch")
    
with rec_sys1:
    st.subheader("What kind of episode do you want to see?")
    
    col_1, col_2, col_3 = st.columns(3)
    season_choice = col_1.multiselect('Season(s):', options = get_seasons_rec_sys())
    character_choice = col_2.multiselect('Character(s):', options= get_speakers_rec_sys(season_choice))
    emotion_choice = col_3.multiselect('Emotion(s):', options = get_emotion())
    num_recs = st.slider('Max number of episodes to recommend:', min_value = 5, max_value = 20, step = 5)
    
with rec_sys2:
    if len(season_choice) + len(character_choice) + len(emotion_choice) == 0:
        st.write("Select at least 1 filter to generate recommendations!")
    elif len(season_choice) > 0  and len(character_choice) + len(emotion_choice) == 0:
        st.write("For recommenadations to be accurate you must also select at least one character or emotion.")
    elif len(season_choice) == 0:
        df = recommend_episodes(season_choice,character_choice,emotion_choice, num_recs)
        st.subheader("Enjoy the following episode recommendations from season(s) of choice:")
        st.dataframe(df, hide_index = True, use_container_width = True)
    else:
        df1, df2 = recommend_episodes(season_choice,character_choice,emotion_choice, num_recs)
        st.subheader("Enjoy the following episode recommendations from season(s) of choice:")
        st.dataframe(df1, hide_index = True, use_container_width = True)
        st.subheader("You may also like: ")
        if df2 is None:
            st.write("No other episodes match criteria :( Sorry!")
        else:
            st.dataframe(df2, hide_index = True, use_container_width = True)
    
with rec_sys4:
    if (len(season_choice) + len(character_choice) + len(emotion_choice)) > 0:
        st.write("The above selections are based on the following priorities (in order of wieght)")
    if len(season_choice) > 0:
        st.write("- Season episode took place in: you have selected - ", list_to_string(season_choice))
    if len(character_choice) > 0:
        st.write("- Number of times", list_to_string(character_choice), "spoke or was talked about during the episode")
    if len(emotion_choice) == 1:
        st.write("- Number of times the emotion,", list_to_string(emotion_choice), ", was displayed by all characters.")
    elif len(emotion_choice) > 1:
        st.write("- Number of times the emotions,", list_to_string(emotion_choice), ", were displayed by all characters.")

    