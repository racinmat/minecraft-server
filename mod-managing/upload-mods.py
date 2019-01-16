from googleapiclient.discovery import build, Resource
from httplib2 import Http
from googleapiclient.http import MediaFileUpload
from oauth2client import file, client, tools
import os
import os.path as osp

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'

if __name__ == '__main__':
    store = file.Storage('token.json')
    storage_client = store.Client.from_service_account_json(
        'service_account.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
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
