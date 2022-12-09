from __future__ import print_function

from datetime import date
import google.auth
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SAMPLE_SPREADSHEET_ID = 'Put the SpredSheetID here'
SAMPLE_RANGE_NAME = 'SpreadSheetRange'

date = str(date.today())
# If modifying these scopes, delete the file token.json.
def main_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    global creds
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("Path to you OAuth token"):
        creds = Credentials.from_authorized_user_file("Path to you OAuth token", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token_google_drive.json', 'w') as token:
            token.write(creds.to_json())
    return(creds)
            
def main_google_sheets():
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    return values

def create_folder(nameSubreddit):
        folder_id = 'Folder ID that you want to create the folders inside'

        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': [nameSubreddit + ' ' + date],
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                    ).execute()
        print(F'Folder {nameSubreddit}: "{file.get("id")}".')
        main_folder = file.get('id')

        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': 'images',
            'parents': [main_folder],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                    ).execute()
        images_folder = file.get('id')

        print(F'Folder_images: "{file.get("id")}".')
        
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': 'videos',
            'parents': [main_folder],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                    ).execute()
        videos_folder = file.get('id')

        print(F'Folder_videos ID: "{file.get("id")}".')

        return main_folder,images_folder,videos_folder


def upload_basic(name_of_the_file, folder_id, name_of_the_folder,image_or_video):
        print(folder_id)
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=creds)
            file_metadata = {
                'name': [name_of_the_file],
                'parents': [folder_id],
                'mimeType': ['image/jpeg','image/png']
            }
            media = MediaFileUpload(fr'Path to the files that you downloaded with the main.py{name_of_the_folder}\{image_or_video}\{name_of_the_file}')
            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, media_body=media,
                                        fields="id").execute()
            print(file)
            print(F'File ID: {file.get("id")}')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.get('id')

def GoogleDriveUploader():
    folders_id = []
    folders_names = []
    Image_Videos_Folder_Id = {}
    counter = 0
    counter_of_id = 0
    for root, dir, file in os.walk(r'Path to you download folder'):
        for dirs in dir:
            print(counter_of_id)
            if dirs not in("images", "videos"):
                folders_names.append(dirs)
                folder_id = create_folder(nameSubreddit= dirs)
                folders_id.append(folder_id)
                Image_Videos_Folder_Id[counter_of_id] = folder_id
                counter_of_id += 1
                print(counter_of_id)
        for root, dir, file in os.walk(r'Path to you download folder'):
            number_of_folder = len(folders_names)
            if counter > number_of_folder-1:
                break
            for dirs in dir:
                for root, dir, file in os.walk(fr'Path to you download folder\{dirs}'):
                    for files in file:
                        if files.endswith((".png",".jpeg",".jpg")):
                            path = 'images'
                            id_for_the_files = Image_Videos_Folder_Id[counter][1]
                        if files.endswith('.mp4'):
                            path = 'videos'
                            id_for_the_files = Image_Videos_Folder_Id[counter][2]
                        upload_basic(name_of_the_file= files, folder_id= id_for_the_files, name_of_the_folder=folders_names[counter], image_or_video=path)
                counter += 1