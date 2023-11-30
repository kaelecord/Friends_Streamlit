# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 15:24:12 2023

@author: kaele
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from ast import literal_eval
import math
import streamlit as st

full_data = pd.read_csv('data/friends_transcript_data.csv')
plots = pd.read_csv('data/friends_plots_cleaned_data.csv') 
speaker = pd.read_csv('data/speaker_cleaned_data.csv')
char_net = pd.read_csv('data/character_network_cleaned_data.csv')
emotion_data = pd.read_csv('data/emotion_cleaned_data.csv')
episode_dates_titles = pd.read_csv('data/episodeDateTitle.csv')
speaker['season_ep'] = speaker['season_id'] + "_" + speaker['episode_id']

def get_seasons():
    season_ = list(full_data['season_id'].unique())
    season_.insert(0,"ALL")
    return season_

def get_seasons_rec_sys():
    season_ = list(full_data['season_id'].unique())
    return season_

def get_episodes(season = 'ALL'):
    if season == "ALL":
        episode_ = list(full_data['episode_id'].unique())
    else:
        episode_ = list(full_data['episode_id'][full_data['season_id'] == season].unique())
    episode_.insert(0,"ALL")
    return episode_

def get_scenes(season = 'ALL', episode = 'ALL'):
    if season == "ALL" and episode == "ALL":
        scene_ = list(full_data['scene_id'].unique())
    elif season != "ALL" and episode == "ALL":
        scene_ = list(full_data['scene_id'][full_data['season_id'] == season].unique())
    elif season == "ALL" and episode != "ALL":
        scene_ = list(full_data['scene_id'][full_data['episode_id'] == episode].unique())
    else:
        scene_ = list(full_data['scene_id'][(full_data['season_id'] == season) & (full_data['episode_id'] == episode)].unique())
    scene_.insert(0, "ALL")
    return scene_

def get_plot(season, episode, scene):
    if (season == "ALL" or episode == "ALL"):
        return "Please refine search to at least 1 episode."
    if scene == "ALL":
        temp = plots[(plots['season_id'] == season) & (plots['episode_id'] == episode) & (plots['plot'] != 'No plot availble for scene')]
        temp['scene_plot'] = "SCENE(" + temp['scene_id'] + ") " + temp['plot']
        plots_joined = ' ' .join(temp['scene_plot'])
        return plots_joined
    else:
        temp = plots[(plots['season_id'] == season) & (plots['episode_id'] == episode) & (plots['scene_id'] == scene)]
    if len(temp) == 0:
        return "No plot information for selected filters. Sorry :("
    else:
        plots_joined = ' ' .join(temp['plot'])
        return plots_joined
    
def get_speakers(season, episode):
    if season == "ALL" and episode == "ALL":
        temp = speaker.groupby(['speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[temp['speakercount']>10]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
        return list(temp['speaker'])
    elif season != "ALL" and episode == "ALL":
        temp = speaker.groupby(['season_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[(temp['speakercount']>5) & (temp['season_id'] == season)]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
    else:
        temp = speaker.groupby(['season_id','episode_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[(temp['speakercount']>1) & (temp['season_id'] == season) & (temp['episode_id'] == episode)]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
    return list(temp['speaker'])

def get_speakers_rec_sys(season):
    if len(season) == 0:
        return list(speaker['speaker'].unique())
    else:
        temp = speaker.groupby(['season_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[(temp['speakercount']>5) & (temp['season_id'].isin(season))]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
        return list(temp['speaker'])

def get_emotion():
    return list(emotion_data['emotion'].unique())

def create_speaker_plot(speaker_list):
    speaker_grouped = speaker.groupby(['season_id','episode_id','speaker']).agg({'speaker': ['count']}).reset_index()
    speaker_grouped.columns = ["".join(col).strip() for col in speaker_grouped.columns.values]
    speaker_grouped['season_ep'] = speaker_grouped['season_id'] + '_' +speaker_grouped['episode_id']
    if len(speaker_list) == 0:
        return "Select character to see plot"
    else:
        speaker_data = speaker_grouped[speaker_grouped['speaker'].isin(speaker_list)].reset_index()
        fig = px.line(speaker_data, x="season_ep", y="speakercount", hover_name="speaker",color = 'speaker',
                      line_shape="spline", render_mode="svg", color_discrete_sequence=px.colors.qualitative.G10).update_layout(
                      xaxis_title="Season_Episode", yaxis_title="Speaker Count", title = "Speaker Count by Episode")
        fig.update_xaxes(categoryorder='array', categoryarray= list(speaker_data['season_ep']))

        return fig
    
def create_network_dict(df):
    speakers = set(df['speaker'])
    outer_dict = {key: {} for key in speakers}
    for i in range(len(df['speaker'])):
        for key in set(literal_eval(df['character_entities'][i])):
            if key not in outer_dict[df['speaker'][i]]:
                outer_dict[df['speaker'][i]][key] = list(literal_eval(df['character_entities'][i])).count(key)
            else:
                outer_dict[df['speaker'][i]][key] += list(literal_eval(df['character_entities'][i])).count(key)
    return outer_dict

def create_network_df(network_dict):
    restructured_data = [(outer_key, inner_key, value)
                     for outer_key, inner_dict in network_dict.items()
                     for inner_key, value in inner_dict.items()]
    df = pd.DataFrame(restructured_data, columns=['Source', 'Target', 'Value'])
    return df

def create_network(df, highlight_chars):
    G = nx.from_pandas_edgelist(df, 'Source', 'Target', 'Value')
    pos = nx.spring_layout(G, k= 0.5, iterations = 25)
    degree_centrality = nx.degree_centrality(G)
    
    # Extract node and edge positions
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_text = [f"{node, round(degree_centrality[node],4)}" for node in G.nodes()]

    # Create nodes trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        hoverinfo='text',
        hovertext = node_text,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color = ['red' if node in highlight_chars else 'black' for node in G.nodes()],
            size=[15 if node in highlight_chars else 10 for node in G.nodes()],
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    # Create edges trace
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1, color='gray'),
        hoverinfo='text'
    )
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    # Show figure
    return fig

def generate_network(season, episode, characters):
    if season == "ALL" and episode == "ALL":
        df = char_net
    elif season != "ALL" and episode == "ALL":
        df = char_net[char_net['season_id'] == season]
    elif season == "ALL" and episode != "ALL":
        df = char_net[char_net['episode_id'] == episode]
    else:
        df = char_net[(char_net['season_id'] == season) & (char_net['episode_id'] == episode)]
    network_dict = create_network_dict(df.reset_index())
    network_df = create_network_df(network_dict)
    fig = create_network(network_df, characters)
    return fig

def create_emotion_pie(season, episode, character_list, include_neutral = False):
    if len(character_list) == 0:
        return "Please select character to see visualization"
    if season == "ALL" and episode == "ALL":
        emotion_grouped = emotion_data.groupby(['speaker','emotion']).agg({'emotion': ['count']}).reset_index()
        emotion_grouped.columns = ["".join(col).strip() for col in emotion_grouped.columns.values]
        emotion_filtered = emotion_grouped[(emotion_grouped['speaker'].isin(character_list))]
    elif season != "ALL" and episode == "ALL":
        emotion_grouped = emotion_data.groupby(['season_id','speaker','emotion']).agg({'emotion': ['count']}).reset_index()
        emotion_grouped.columns = ["".join(col).strip() for col in emotion_grouped.columns.values]
        emotion_filtered = emotion_grouped[(emotion_grouped['speaker'].isin(character_list)) & (emotion_grouped['season_id'] == season)]
    elif season != "ALL" and episode != "ALL":
        emotion_grouped = emotion_data.groupby(['season_id', 'episode_id','speaker','emotion']).agg({'emotion': ['count']}).reset_index()
        emotion_grouped.columns = ["".join(col).strip() for col in emotion_grouped.columns.values]
        emotion_filtered = emotion_grouped[(emotion_grouped['speaker'].isin(character_list)) & (emotion_grouped['season_id'] == season) & (emotion_grouped['episode_id'] == episode)]
    else:
        return "Please change filters. Must select full show, full season, or single episode."
    if not include_neutral:
         emotion_filtered = emotion_filtered[(emotion_grouped['emotion'].isin(['Mad', 'Joyful', 'Scared', 'Sad', 'Powerful', 'Peaceful']))]

    if episode != "ALL":
        episode_name  = get_ep_title(season, episode)
        fig = px.pie(emotion_filtered, values='emotioncount', names='emotion', title=f'Emotion Pie Charts for Season: {season} | Episode: {episode} | {episode_name}', facet_col = "speaker", facet_col_wrap=4)
    else:
        fig = px.pie(emotion_filtered, values='emotioncount', names='emotion', title=f'Emotion Pie Charts for Season: {season} | Episode: {episode}', facet_col = "speaker", facet_col_wrap=4)
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autosize=True,height=400*math.ceil(len(character_list)/4))
    
    return fig

def get_ep_title(season,episode):
    if (season == "ALL" or episode == "ALL"):
        return None
    else:
        return episode_dates_titles[(episode_dates_titles['season_id'] == season) & (episode_dates_titles['episode_id'] == episode)].reset_index()['episode_title'][0]
def get_ep_airdate(season,episode):
    if (season == "ALL" or episode == "ALL"):
        return None
    else:
        return episode_dates_titles[(episode_dates_titles['season_id'] == season) & (episode_dates_titles['episode_id'] == episode)].reset_index()['air_date'][0]
    
def create_speaker_bar(character_list):
    if len(character_list) == 0:
        return "Select at least 1 character then press play!"
    else:
        temp = speaker.groupby(['season_id','episode_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        speaker_date = pd.merge(temp, episode_dates_titles, on = ['season_id', 'episode_id'], how = 'inner')
        speaker_date_filtered = speaker_date[speaker_date['speaker'].isin(character_list)]
        fig = px.bar(speaker_date_filtered, x='speaker', y='speakercount', color='speaker', animation_group = 'speaker', animation_frame = 'air_date', range_y=[0, 100], labels={'speaker': 'Speaker', 'speakercount':'Speaker Count'})

        fig.update_layout(title='Speaker Count by Episode (animated)')

        return fig
    
def list_to_string(ls):
    if len(ls) == 0:
        return ""
    elif len(ls) == 1:
        return ls[0]
    elif len(ls) == 2:
        ls.insert(-1,"and")
        return " ".join(ls)
    else:
        ls.insert(-1,"and")
        tempa = ", ".join(ls[:-1])
        tempb = " ".join(ls[-1:])
        return tempa + " " + tempb
    
def create_character_entity_df(speaker_df):
    episodes = set(speaker_df['season_ep'])
    outer_dict = {key: {} for key in episodes}
    speaker_df = speaker_df.reset_index()
    for i in range(len(speaker_df['season_ep'])):
        for key in set(literal_eval(speaker_df['character_entities'][i])):
            if key == 0:
                continue
            if key not in outer_dict[speaker_df['season_ep'][i]]:
                outer_dict[speaker_df['season_ep'][i]][key] = list(literal_eval(speaker_df['character_entities'][i])).count(key)
            else:
                outer_dict[speaker_df['season_ep'][i]][key] += list(literal_eval(speaker_df['character_entities'][i])).count(key)

    episode_list = []
    character_list = []
    count_list = []

    # Get data from the nested dictionary
    for episode, characters in outer_dict.items():
        for character, count in characters.items():
            episode_list.append(episode)
            character_list.append(character)
            count_list.append(count)

    character_entities_df = pd.DataFrame({'episode': episode_list, 'character': character_list, 'count': count_list})
    return character_entities_df

def create_emotion_grouped_df(speaker_df):
    emotion_grouped = speaker_df.groupby(['season_ep','emotion']).agg({'emotion': ['count']}).reset_index()
    emotion_grouped.columns = ["".join(col).strip() for col in emotion_grouped.columns.values]
    
    return emotion_grouped

def create_speaker_grouped_df(speaker_df):   
    speaker_grouped = speaker_df.groupby(['season_ep','speaker']).agg({'speaker': ['count']}).reset_index()
    speaker_grouped.columns = ["".join(col).strip() for col in speaker_grouped.columns.values]

    return speaker_grouped

def normalize_scores(score_df):
    total = np.sum(score_df['ep_score'])
    normalized_score = []
    for i in range(len(score_df)):
        normalized_score.append(score_df['ep_score'][i] / total)
    return normalized_score

def score_episodes_no_season(speaker_df, characters, emotions):
    char_ent_grouped = create_character_entity_df(speaker_df)
    speaker_grouped = create_speaker_grouped_df(speaker_df)
    emotion_grouped = create_emotion_grouped_df(speaker_df)
    
    score_dict = {key: 0 for key in list(speaker_df['season_ep'].unique())}
    if len(characters) == 0 and len(emotions) == 0:
        return "Select at least 1 character or emotion get recommendation"
    if len(characters) != 0:
        for i in range(len(char_ent_grouped)):
            episode = char_ent_grouped['episode'][i]
            if char_ent_grouped['character'][i] in characters:
                score_dict[episode] += 2*char_ent_grouped['count'][i]
        for i in range(len(speaker_grouped)):
            episode = speaker_grouped['season_ep'][i]
            if speaker_grouped['speaker'][i] in characters:
                score_dict[episode] += 3*speaker_grouped['speakercount'][i]
    if len(emotions) != 0:
        for i in range(len(emotion_grouped)):
            episode = emotion_grouped['season_ep'][i]
            if emotion_grouped['emotion'][i] in emotions:
                score_dict[episode] += 1*emotion_grouped['emotioncount'][i]

    return score_dict

def recommend_episodes(seasons, characters, emotions, num_recs=5):
    if len(seasons) == 0:
        score_dict = score_episodes_no_season(speaker,characters, emotions)
        score_dict_filtered = {episode: count for episode, count in score_dict.items() if count != 0}
        score_df = pd.DataFrame.from_dict(score_dict_filtered, orient = 'index', columns = ['ep_score'])
        score_df['ep_norm_score'] = normalize_scores(score_df)
        if len(score_dict_filtered) <num_recs:
            selected_rows = list(np.random.choice(score_df.index, size=len(score_dict_filtered), p=score_df['ep_norm_score'], replace = False))
        else:
            selected_rows = list(np.random.choice(score_df.index, size=num_recs, p=score_df['ep_norm_score'], replace = False))
        season = []
        episodes = []
        title = []
        air_date = []
        for episode in [ep.split("_") for ep in selected_rows]:
            season.append(episode[0])
            episodes.append(episode[1])
            title.append(get_ep_title(episode[0],episode[1]))
            air_date.append(get_ep_airdate(episode[0],episode[1]))
        df = pd.DataFrame(list(zip(season, episodes, title, air_date)),
                       columns =['Season', 'Episode', 'Episode Title', 'Air Date'])
        return df
    
    else:
        speaker_in = speaker[speaker['season_id'].isin(seasons)]
        score_dict_in = score_episodes_no_season(speaker_in, characters, emotions)
        score_dict_in_filtered = {episode: count for episode, count in score_dict_in.items() if count != 0}
        score_df_in = pd.DataFrame.from_dict(score_dict_in_filtered, orient = 'index', columns = ['ep_score'])
        score_df_in['ep_norm_score'] = normalize_scores(score_df_in)
        if len(score_dict_in_filtered) <num_recs:
            selected_rows_in = list(np.random.choice(score_df_in.index, size=len(score_dict_in_filtered), p=score_df_in['ep_norm_score'], replace = False))
        else:
            selected_rows_in = list(np.random.choice(score_df_in.index, size=num_recs, p=score_df_in['ep_norm_score'], replace = False))        
        
        season = []
        episodes = []
        title = []
        air_date = []
        for episode in [ep.split("_") for ep in selected_rows_in]:
            season.append(episode[0])
            episodes.append(episode[1])
            title.append(get_ep_title(episode[0],episode[1]))
            air_date.append(get_ep_airdate(episode[0],episode[1]))
        df_in = pd.DataFrame(list(zip(season, episodes, title, air_date)),
                       columns =['Season', 'Episode', 'Episode Title', 'Air Date'])

        season_out = speaker[~speaker['season_id'].isin(seasons)]
        score_dict_out = score_episodes_no_season(season_out, characters, emotions)
        score_dict_out_filtered = {episode: count for episode, count in score_dict_out.items() if count != 0}        
        score_df_out = pd.DataFrame.from_dict(score_dict_out_filtered, orient = 'index', columns = ['ep_score'])
        score_df_out['ep_norm_score'] = normalize_scores(score_df_out)
        if np.sum(score_df_out['ep_norm_score']) == 0:
            return df_in, None
        
        if len(score_dict_out_filtered) <=5:
            selected_rows_out = list(np.random.choice(score_df_out.index, size=len(score_dict_out_filtered), p=score_df_out['ep_norm_score'], replace = False))
        else:
            selected_rows_out = list(np.random.choice(score_df_out.index, size=5, p=score_df_out['ep_norm_score'], replace = False))        
                
        season = []
        episodes = []
        title = []
        air_date = []
        for episode in [ep.split("_") for ep in selected_rows_out]:
            season.append(episode[0])
            episodes.append(episode[1])
            title.append(get_ep_title(episode[0],episode[1]))
            air_date.append(get_ep_airdate(episode[0],episode[1]))
        df_out = pd.DataFrame(list(zip(season, episodes, title, air_date)),
                       columns =['Season', 'Episode', 'Episode Title', 'Air Date'])
        return df_in, df_out
    
