import os
import os.path as osp

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
CLIENT_SECRETS = 'client_secrets.json'

if __name__ == '__main__':

    SERVICE_ACCOUNT_FILE = 'mcserver-service-account-key.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    try:
        files = drive_service.files()
        aaa = files.list(q="mimeType='image/jpeg'").execute()
        ccc = files.list(q="name='a'").execute()
        bbb = files.list(q="name='mc-server-mods'").execute()
        mods_dir = files.list(q="name='mc-server-mods'").execute()['files'][0]
        mods_dir_id = mods_dir['id']
        already_present_mods = files.list(q=f'{mods_dir_id} in parents').execute()
        for mod_name in os.listdir('../new-mc-server/mods'):
            mod_path = osp.join('../new-mc-server/mods', mod_name)
            print(mod_name, mod_path)
            file_metadata = {'name': 'photo.jpg'}
            media = MediaFileUpload('files/photo.jpg',
                                    mimetype='image/jpeg')
            file = files.create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
            print('File ID: %s' % file.get('id'))
    except HttpError as e:
        print(str(e))
        raise e