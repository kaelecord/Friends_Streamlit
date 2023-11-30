# Friends Streamlit App
I501 - Intro to Informatics Final Project Submission

You can find the Streamlit app [here](https://friends.streamlit.app/)

## Abstract
**Goals**: 
1) Provide fans of the Friends TV show with a simple environment to explore unique aspects of the show through the lens of various data visualizations.
 2) Recommend episodes to viewers based on their favorite seasons, favorite characters, and what mood they are in.

## Data Description
The data used to create all aspects of this project comes from the Emory NLP Character Mining Project. The dataset is based on the popular TV show, Friends, which aired from September 22, 1994, through May 6, 2004. All data used was extracted from a collection of JSON files that can be found [here](https://github.com/emorynlp/character-mining/tree/master/json).

The following are the extracted columns:
-   season_id: Unique ID for season number
-   episode_id: Unique ID for episode number within a season
-   scene_id: Unique ID for scene number within an episode
-   utterace_id: Unique ID for an utterance number within a scene
-   speaker: name of character who speaks the line
-   tokens: list of lists - outer list for each sentence within a line - inner list for each word or punctuation within a sentence.
-   transcript: tokens joined to form a line spoken by a speaker for the utterance
-   emotion: the emotion of line determined by results of [Emory NLP Project - Emotion Detection](https://github.com/emorynlp/emotion-detection)
-   character_entities: characters spoken about within the utterance as determined by [Emory NLP Project - Character Identification](https://github.com/emorynlp/character-identification)
-   num_talked_about: integer corresponding to number length of character_entities list
    - added a column that I created during the data-cleaning process 

## Algorithm Description
The only algorithm used throughout this project is the one used to produce episode recommendations. 

The system is based on the following hierarchy of importance (most important to least important): 
1) Season Preference
2) Character Preference
3) Emotion Preference

This hierarchy is implemented through filtering the data and then implementing a scoring system. If a season(s) is selected the data is split into two separate pieces, one with only episodes from the selected season(s) and the other with only the unselected season(s). Once the data has been split each episode is scored. An episode receives 3 points for every time the character(s) selected to appear as a speaker, 2 points for every time the character(s) selected are talked about or mentioned, and 1 point for every time the emotion(s) are displayed.

Once this process has taken place the scores are converted to probabilities by taking the score divided by the total score of all episodes. Then 5, 10, 15, or 20 episodes are randomly chosen based on these probabilities and presented as the suggested episodes. 

If a season or seasons have been selected the system will also recommend 5 additional episodes from seasons that the user did not select based on the character(s) and/or emotion(s) selected. 

## Tools Used
 - Streamlit
     - Used for easy web app creation deployment
 - Plotly Express
     - Used to create interactive and animated visualizations throughout the application
 - NetworkX
     - Used to create a structure that generates the character network
