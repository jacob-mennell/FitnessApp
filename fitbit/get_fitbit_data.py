import pandas as pd
import datetime
import cherrypy
import fitbit
from gather_keys_oauth2 import OAuth2Server
import os
import json


class FitbitAnalysis:

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

        # create a FitbitOauth2Client object.
        server = OAuth2Server(self.client_id, self.client_secret)
        server.browser_authorize()
        access_token = str(server.fitbit.client.session.token['access_token'])
        refresh_token = str(server.fitbit.client.session.token['refresh_token'])

        self.fit = fitbit.Fitbit(client_id, client_secret, oauth2=True, access_token=access_token,
                                 refresh_token=refresh_token)

    def get_x_days_activity(self, no_days_ago: int) -> pd.DataFrame:
        """_summary_

        Args:
            no_days_ago (int): days of data to return

        Returns:
            pd.DataFrame: activity data frame
        """

        # define last 10 days of data
        days_list = [str((datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")) for i in
                     range(1, no_days_ago + 1)]

        # variable list
        id_list = []
        name_list = []
        calories_list = []
        steps_list = []
        date_list = []

        # get activities for last x days
        for day in days_list:
            activities = self.fit.activities(date=day)['activities']
            [id_list.append(x) for x in [action['activityId'] for action in activities]]
            [name_list.append(x) for x in [action['name'] for action in activities]]
            [calories_list.append(x) for x in [action['calories'] for action in activities]]
            [steps_list.append(x) for x in [action['steps'] for action in activities]]
            [date_list.append(x) for x in [action['startDate'] for action in activities]]

        # make DataFrame
        activity_df = pd.DataFrame({'id': id_list,
                                    'Name': name_list,
                                    'Start_Date': date_list,
                                    'Calories': calories_list,
                                    'Steps': steps_list
                                    })

        # cast data types
        activity_df['id'] = activity_df['id'].astype(int)
        activity_df['Name'] = activity_df['Name'].astype(str)
        activity_df['Start_Date'] = pd.to_datetime(activity_df['Start_Date'], format='%Y-%m-%d')
        activity_df['Steps'] = activity_df['Steps'].astype(int)
        activity_df['Calories'] = activity_df['Calories'].astype(int)

        # return DataFrame
        return activity_df

    def get_x_days_sleep(self, no_days_ago: int) -> pd.DataFrame:
        """_summary_

        Args:
            no_days_ago (int): days of data to return

        Returns:
            pd.DataFrame: sleep data frame
        """

        # define last 10 days of data
        days_list = [str((datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")) for i in
                     range(1, no_days_ago + 1)]

        # get activities for last x days
        sleep_time_list = []
        sleep_val_list = []
        date_of_sleep = []

        for day in days_list:
            sleep_func = self.fit.sleep(date=day)
            for i in sleep_func['sleep'][0]['minuteData']:
                date_of_sleep.append(sleep_func['sleep'][0]['dateOfSleep'])
                sleep_time_list.append(i['dateTime'])
                sleep_val_list.append(i['value'])

        df = pd.DataFrame({'State': sleep_val_list, 'Time': sleep_time_list, 'Date': date_of_sleep})
        df['State_Detail'] = df['State'].map({'2': 'Awake', '3': 'Alert', '1': 'Asleep'})

        return df

    def get_x_days_sleep_agg(self, no_days_ago: int) -> pd.DataFrame:
        """_summary_

        Args:
            no_days_ago (int): days of data to return

        Returns:
            pd.DataFrame: Aggregated sleep data frame
        """

        # define last 10 days of data
        days_list = [str((datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")) for i in
                     range(1, no_days_ago + 1)]

        # create blank DataFrame
        agg_df = pd.DataFrame(
            columns=[
                'dateOfSleep',
                'isMainSleep',
                'efficiency',
                'duration',
                'minutesAsleep',
                'minutesAwake',
                'awakeCount',
                'restlessCount',
                'restlessDuration',
                'timeInBed']
        )

        for day in days_list:
            sleep_func = self.fit.sleep(date=day)['sleep'][0]

            agg_df_temp = pd.DataFrame({'dateOfSleep': sleep_func['dateOfSleep'],
                                        'isMainSleep': sleep_func['isMainSleep'],
                                        'efficiency': sleep_func['efficiency'],
                                        'duration': sleep_func['duration'],
                                        'minutesAsleep': sleep_func['minutesAsleep'],
                                        'minutesAwake': sleep_func['minutesAwake'],
                                        'awakeCount': sleep_func['awakeCount'],
                                        'restlessCount': sleep_func['restlessCount'],
                                        'restlessDuration': sleep_func['restlessDuration'],
                                        'timeInBed': sleep_func['timeInBed']
                                        }, index=[0])

            agg_df = pd.concat([agg_df, agg_df_temp], join="inner")

        return agg_df


if __name__ == "__main__":
    # get credentials for api and google sheet source
    with open('cred.json') as data_file:
        data = json.load(data_file)

    # export fitbit data to pkl file
    fitinst = FitbitAnalysis(data['client_id'], data['client_secret'])
    activity = fitinst.get_x_days_activity(30)
    activity.to_pickle('activity.pkl')

    sleep = fitinst.get_x_days_sleep_agg(30)
    sleep.to_pickle('sleep.pkl')
