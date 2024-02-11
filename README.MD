# Fitness Project

## Table of Contents

- [Aims](#aims)
- [Secondary](#secondary)
- [Learnings](#learnings)
- [Application](#application)
- [Requirements](#requirements)
- [Future Development](#future-development)
- [Chat Bot](#chat-bot)
  - [System Requirements](#system-requirements)
  - [Getting Started](#getting-started)
- [License](#license)

## Aims

- Record and visualize lift data from workouts, e.g., exercises, sets, reps, and weight.
- Use Google Sheets as a flexible data store to write gym session data via the gspread module.
- Develop Streamlit web app (streamlit_app_gym.py) for user interface to input data to google cloud and to visualize lift trends.
- All users can monitor existing users' performance; however, a password is required to create new users and to input data.
- Integrate with OpenAI GPT-3.5 to query fitness data in natural language providing addition insight. 

## Secondary

- Combine Fitbit data with recorded data from workouts, e.g., exercises, sets, reps, and weights.
- Currently, Fitbit data is read from a _.pkl_ file due to issues accessing the data directly in the Streamlit environment.
- Develop Streamlit web app (streamlit_app_fitbit.py) for user interface to collate fitness and lifestyle data.

## Learnings

- Streamlit App Production using Streamlit Cloud
- Streamlit Front-End development, key features include password functionality.
- Simple Unit Testing
- Authenticating API with OAuth2

## Application 
**Link to Gym Performance Tracker Streamlit App:**
[https://gym-tracker.streamlit.app/](https://gym-tracker.streamlit.app/)

## Requirements

Refer to the `environment.yml` file for the required dependencies.

## Chat Bot

The Fitness Project includes an AI Fitness Advisor chat bot powered by OpenAI's GPT-3.5. This bot provides insights, answers questions related to workouts, and analyzes gym data to offer personalized recommendations. The chat bot is integrated into the Streamlit web app, allowing users to interact with the AI advisor seamlessly.

### System Requirements

- [OpenAI GPT-3.5](https://beta.openai.com/signup/): To access the powerful language model for the chat bot.
- Python packages listed in [environment.yml](#environment.yml): Ensure you have the necessary dependencies installed.

### Getting Started

1. Obtain API Key from OpenAI: Sign up for access to the GPT-3.5 model and obtain your API key.
2. Set Up Streamlit App: Make sure you have the Streamlit app running with the required [dependencies](#requirements).
3. Add API Key: Insert your OpenAI API key in the appropriate configuration file or as an environment variable.
4. Interact with the Chat Bot: Open the Fitness Project Streamlit app and start interacting with the AI Fitness Advisor. Ask questions related to your workout, progress, or seek personalized recommendations.

```python
# Sample code snippet for interacting with the chat bot
from openai import OpenAI
import streamlit as st

# Initialize the chat messages history
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
```

## Future Development

- Indication of key areas of growth e.g. leg exercises vs upper body
- Future prediction/planning to target growth of muscle groups and hit lifting goals, involving construction of a simple regression model
- Integration with Strava API as an alternative to Fitbit, this will be more versatile to app users. Opportunity for advanced analytics, for example looking at heart rate zones.

## Licence

Feel free to customize it further based on your specific needs.
