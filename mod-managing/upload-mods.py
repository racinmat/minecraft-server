import hashlib
import os
import os.path as osp

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()


if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/drive']
    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
    SERVICE_ACCOUNT_FILE = 'mcserver-service-account-key.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)
    # is you want to use directories from service account, you must share it with its email and transfer ownership to it
    files = drive_service.files()
    list_dir_q = files.list(q="name='mc-server-mods'")
    mods_dir = list_dir_q.execute()['files'][0]
    mods_dir_id = mods_dir['id']
    list_mods_q = files.list(q=f"'{mods_dir_id}' in parents", fields="files(id, name, kind, mimeType, md5Checksum)")
    already_present_res = list_mods_q.execute()
    already_present = {i['name']: i['md5Checksum'] for i in already_present_res['files']}
    for mod_name in os.listdir('../new-mc-server/mods'):
        mod_path = osp.join('..', 'new-mc-server', 'mods', mod_name)
        if mod_name in already_present:
            local_checksum = md5sum(mod_path)
            if local_checksum == already_present[mod_name]:
                continue    # same file, skip it
            file_metadata = {'name': mod_name, 'parents': [mods_dir_id]}
            media = MediaFileUpload(mod_path, mimetype='application/java-archive')
            file = files.update(body=file_metadata, media_body=media).execute()
        else:
            file_metadata = {'name': mod_name, 'parents': [mods_dir_id]}
            media = MediaFileUpload(mod_path, mimetype='application/java-archive')
            file = files.create(body=file_metadata, media_body=media).execute()
        print('File ID: %s' % file.get('id'))
