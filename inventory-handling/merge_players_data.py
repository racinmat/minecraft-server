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
    playerdata_dir_new = r'E:\mc backupy\novy soucasny svet backup\braveNewWorld\playerdata'
    usercache_file_new = r'E:\mc backupy\novy soucasny svet backup\usercache.json'
    dir_out = './merged_items'

    forbidden_mod = 'twilightforest'

    old_corrupted_hashes = []
    # old_corrupted_hashes = [    # empirically found
    #     '6220dacd-98ba-3371-873c-baac80c0b989',
    #     '985969ce-f9cc-38b0-a7ea-2a2097f0d513',
    # ]

    with open(usercache_file_old, 'rb') as fp:
        user_hashes_old = json.load(fp)
    with open(usercache_file_new, 'rb') as fp:
        user_hashes_new = json.load(fp)

    uuid_to_name_old = {i['uuid']: i['name'] for i in user_hashes_old}
    uuid_to_name_new = {i['uuid']: i['name'] for i in user_hashes_new}
    name_to_uuid_old = {v: k for k, v in uuid_to_name_old.items()}

    playerdata_files_old = {f: osp.join(playerdata_dir_old, f) for f in os.listdir(playerdata_dir_old)}
    playerdata_files_new = {f: osp.join(playerdata_dir_new, f) for f in os.listdir(playerdata_dir_new)}
    for filename_new, file_path_new in playerdata_files_new.items():
        file_hash_new = osp.splitext(osp.basename(filename_new))[0]
        nbtfile_new = nbt.NBTFile(file_path_new, 'rb')

        if file_hash_new not in uuid_to_name_new:
            print('unknown hash', file_hash_new, 'skipping')
            continue

        player_name = uuid_to_name_new[file_hash_new]
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

        #######################
        # forgecaps resolving #
        #######################
        old_forgecaps = nbtfile_old['ForgeCaps']
        new_forgecaps = nbtfile_new['ForgeCaps']

        # merging thaumcraft progress: knowledge
        old_knowledge = old_forgecaps['thaumcraft:knowledge']['knowledge']
        new_knowledge = new_forgecaps['thaumcraft:knowledge']['knowledge']
        new_knowledge_dict = {i['key'].value: i for i in new_knowledge}
        for item in old_knowledge:
            old_key = item['key'].value
            if old_key in new_knowledge_dict:
                old_val = item['amount'].value
                new_val = new_knowledge_dict[old_key]['amount'].value
                new_knowledge_dict[old_key]['amount'].value = max(old_val, new_val)
            else:
                new_knowledge.append(item)
                new_knowledge.tagID = item.id

        # merging thaumcraft progress: research
        old_research = old_forgecaps['thaumcraft:knowledge']['research']
        new_research = new_forgecaps['thaumcraft:knowledge']['research']
        new_research_dict = {i['key'].value: i for i in new_research}
        for item in old_research:
            old_key = item['key'].value
            if old_key in new_research_dict:
                if 'stage' in item:
                    old_val = item['stage'].value
                    new_val = new_research_dict[old_key]['stage'].value
                    new_research_dict[old_key]['stage'].value = max(old_val, new_val)
            else:
                new_research.append(item)
                new_research.tagID = item.id

        old_forgecaps.update(nbtfile_new['ForgeCaps'])  # old data, merged with new, same parts overwritten by new
        nbtfile_new['ForgeCaps'] = old_forgecaps

        ###################
        # items resolving #
        ###################
        all_slots = list(range(36))
        all_ender_slots = list(range(27))
        new_slots_full = [i['Slot'].value for i in nbtfile_new['Inventory']]
        new_ender_slots_full = [i['Slot'].value for i in nbtfile_new['EnderItems']]

        # filtering out items from forbidden mod
        for i, item in enumerate(nbtfile_old['Inventory']):
            if item['id'].value.startswith(forbidden_mod):
                del nbtfile_old['Inventory'][i]
        for i, item in enumerate(nbtfile_old['EnderItems']):
            if item['id'].value.startswith(forbidden_mod):
                del nbtfile_old['EnderItems'][i]

        old_slots_full = [i['Slot'].value for i in nbtfile_old['Inventory']]
        old_ender_slots_full = [i['Slot'].value for i in nbtfile_old['EnderItems']]
        # old equipped things will go to inventory
        num_new_free_slots = len(list(set(all_slots) - set(new_slots_full))) + len(
            list(set(all_ender_slots) - set(new_ender_slots_full)))
        if len(old_slots_full) + len(old_ender_slots_full) > num_new_free_slots:
            print('Too many items together, cant merge for player', player_name, ', should have', len(old_slots_full),
                  'free slots for transfer')
            continue

        items_to_add = list(nbtfile_old['Inventory']) + list(nbtfile_old['EnderItems'])
        print('player:', player_name, 'going to add', len(items_to_add), 'items to inventory and ender chest')

        free_inventory_slots = list(set(all_slots) - set(new_slots_full))
        print(len(free_inventory_slots), 'free ender chest slots')
        for slot in free_inventory_slots:
            if len(items_to_add) == 0:
                break
            item_to_add = items_to_add.pop(0)
            item_to_add['Slot'].value = slot
            nbtfile_new['Inventory'].append(item_to_add)
            nbtfile_new['Inventory'].tagID = item_to_add.id

        print(len(items_to_add), 'items remaining to put to ender chest after inventory is full')

        free_ender_chest_slots = list(set(all_ender_slots) - set(new_ender_slots_full))
        print(len(free_ender_chest_slots), 'free ender chest slots')
        for slot in free_ender_chest_slots:
            if len(items_to_add) == 0:
                break
            item_to_add = items_to_add.pop(0)
            item_to_add['Slot'].value = slot
            nbtfile_new['EnderItems'].append(item_to_add)
            nbtfile_new['EnderItems'].tagID = item_to_add.id

        if len(items_to_add) > 0:
            print('Failed to add', len(items_to_add), 'items to player', player_name, 'everything is full')

        nbtfile_new.write_file(osp.join(dir_out, filename_new))


if __name__ == '__main__':
    app.run(main)
