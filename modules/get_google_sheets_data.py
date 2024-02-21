import pandas as pd
import gspread as gs
import gspread_dataframe as gd


def google_sheet_auth(sheet_url: str, sheet_name: str, credentials: dict) -> tuple:
    """
    Authenticate connection to google sheet and return worksheet object
    :param sheet_url: str, url of the google sheet
    :param sheet_name: str, name of the worksheet in the google sheet
    :param credentials: dict, google sheet credentials from service_account.json
    :return: tuple, (gs.Client, gs.Worksheet)
    """
    try:
        gc = gs.service_account_from_dict(credentials)
    except Exception as e:
        raise ValueError(f"Invalid credentials {e}")

    # open from url
    sh = gc.open_by_url(sheet_url)

    return sh.worksheet(sheet_name)


def get_google_sheet(
    sheet_url: str, sheet_name: str, credentials: dict
) -> pd.DataFrame:
    """
    Retrieve data from google sheet and convert it to a pandas dataframe
    :param sheet_url: str, url of google sheet
    :param sheet_name: str, name of the worksheet in the google sheet
    :param credentials: dict, google sheet credentials from service_account.json
    :return: pd.DataFrame, the data from the google sheet in a pandas dataframe
    """
    # select workbook
    sheet = google_sheet_auth(sheet_url, sheet_name, credentials)

    # create Data Frame
    df = pd.DataFrame(sheet.get_all_records())

    # convert all string columns to upper case
    df = df.applymap(lambda s: s.upper() if type(s) == str else s)

    return df


def export_to_google_sheets(
    sheet_url: str, sheet_name: str, df_new: pd.DataFrame, credentials: dict
) -> None:
    """
    Export dataframe to google sheet
    :param sheet_url: str, url of the google sheet
    :param sheet_name: str, name of the worksheet in the google sheet
    :param df_new: pd.DataFrame, the dataframe containing the data to be exported
    :param credentials: dict, google sheet credentials from service_account.json
    """

    # Include some error handling to make sure input dataframe is not empty
    # if df_new.empty:
    #     raise ValueError("Input dataframe is empty")

    # select workbook
    sheet = google_sheet_auth(sheet_url, sheet_name, credentials)

    # add rows from df
    df_current = get_google_sheet(sheet_url, sheet_name, credentials)

    # concat new data with existing
    final_df = pd.concat([df_current, df_new], join="outer")

    # clear data
    sheet.clear()

    # add new concat final_df_data
    gd.set_with_dataframe(
        worksheet=sheet,
        dataframe=final_df,
        include_index=False,
        include_column_header=True,
        resize=True,
    )
