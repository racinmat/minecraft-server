from nbt import nbt, chunk, region, world
from pprint import pprint
import json
import os.path as osp
import yaml
from absl import flags
from absl import logging
from absl import app
import os


def values_to_struct(value):
    if isinstance(value, nbt.TAG_List):
        return [values_to_struct(i) for i in value]
    elif isinstance(value, nbt.TAG_Compound):
        return {k: values_to_struct(value[k]) for k in value}
    elif isinstance(value, (nbt._TAG_Numeric, nbt.TAG_String, nbt.TAG_Int_Array)):
        return value.value
    else:
        return value


def main(_):
    playerdata_dir = r'E:\mc backupy\soucasny server svety\scitaniautismus\playerdata'
    usercache_file = r'E:\mc backupy\soucasny-server\usercache.json'

    with open(usercache_file, 'rb') as fp:
        user_hashes = json.load(fp)

    uuid_to_name = {i['uuid']: i['name'] for i in user_hashes}
    for filename in os.listdir(playerdata_dir):
        file_hash = osp.splitext(osp.basename(filename))[0]
        nbtfile = nbt.NBTFile(osp.join(playerdata_dir, filename), 'rb')
        data = values_to_struct(nbtfile)

        if file_hash in uuid_to_name:
            with open(uuid_to_name[file_hash] + '.yaml', 'w+') as fp:
                yaml.dump(data, fp, indent=4)
        else:
            print('unknown hash', file_hash)
            with open(file_hash + '.yaml', 'w+') as fp:
                yaml.dump(data, fp, indent=4)

if __name__ == '__main__':
    app.run(main)
