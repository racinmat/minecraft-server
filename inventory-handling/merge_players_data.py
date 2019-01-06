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
    playerdata_dir_old = r'E:\mc backupy\soucasny server svety\scitaniautismus\playerdata'
    usercache_file_old = r'E:\mc backupy\soucasny-server\usercache.json'
    playerdata_dir_new = r'E:\Projects\minecraft\new-mc-server\braveNewWorld\playerdata'
    usercache_file_new = r'E:\Projects\minecraft\new-mc-server\usercache.json'
    dir_out = '.'

    old_corrupted_hashes = [    # empirically found
        '6220dacd-98ba-3371-873c-baac80c0b989',
        '985969ce-f9cc-38b0-a7ea-2a2097f0d513',
    ]

    with open(usercache_file_old, 'rb') as fp:
        user_hashes_old = json.load(fp)
    with open(usercache_file_new, 'rb') as fp:
        user_hashes_new = json.load(fp)

    uuid_to_name_old = {i['uuid']: i['name'] for i in user_hashes_old}
    uuid_to_name_new = {i['uuid']: i['name'] for i in user_hashes_new}
    name_to_uuid_old = {v: k for k, v in uuid_to_name_old.items()}

    playerdata_files_old = {f: osp.join(playerdata_dir_old, f) for f in os.listdir(playerdata_dir_old)}
    playerdata_files_new = {f: osp.join(playerdata_dir_new, f) for f in os.listdir(playerdata_dir_new)}
    for filename, file_path in playerdata_files_new.items():
        file_hash = osp.splitext(osp.basename(filename))[0]
        nbtfile_new = nbt.NBTFile(file_path, 'rb')

        if file_hash not in uuid_to_name_old:
            print('unknown hash', file_hash, 'skipping')
            continue

        player_name = uuid_to_name_new[file_hash]
        if player_name not in name_to_uuid_old:
            print('player', player_name, 'not found in old usercache')
            continue

        player_hash_old = name_to_uuid_old[player_name]
        player_filename_old = player_hash_old + '.dat'

        if player_hash_old in old_corrupted_hashes:
            print('corrupted old data for player', player_name, 'not recovering')
            continue

        if player_filename_old not in playerdata_files_old:
            print('player', player_name, 'with hash', player_filename_old, 'not found in old dat files')
            continue

        nbtfile_old = nbt.NBTFile(playerdata_files_old[player_filename_old], 'rb')
        old_forgecaps = nbtfile_old['ForgeCaps']
        old_forgecaps.update(nbtfile_new['ForgeCaps'])  # old data, merged with new, same parts overwritten by new
        nbtfile_new['ForgeCaps'] = old_forgecaps
        nbtfile_new['Inventory'].extend(nbtfile_old['Inventory'])   # just appending data

        nbtfile_new.write_file(osp.join(dir_out, filename))


if __name__ == '__main__':
    app.run(main)
