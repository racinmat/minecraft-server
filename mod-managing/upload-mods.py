import httplib2
from googleapiclient.discovery import build, Resource
from httplib2 import Http
from googleapiclient.http import MediaFileUpload
from oauth2client import file, client, tools
import os
import os.path as osp
import googleapiclient.http
import oauth2client.client

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
CLIENT_SECRETS = 'client_secrets.json'

if __name__ == '__main__':
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
    SERVICE_ACCOUNT_FILE = 'E:\Projects\minecraft\mod-managing\mcserver-service-account-key.json'

    credentials_2 = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #
    # storage = file.Storage('token.json')
    # credentials = storage.get()

    # Create an authorized Drive API client.
    # http = httplib2.Http()
    # credentials.authorize(http)
    # drive_service = build('drive', 'v2', http=http)
    drive_service = build('drive', 'v2', credentials=credentials_2)

    files = drive_service.files()
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
