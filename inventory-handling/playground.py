from nbt import nbt, chunk, region, world
from pprint import pprint
import json
import os.path as osp
import yaml


def print_value(value, depth=0):
    if isinstance(value, nbt.TAG_List):
        print()
        for valvalue in value:
            print_value(valvalue, depth + 1)
    elif isinstance(value, nbt.TAG_Compound):
        print()
        for k in value:
            print('  ' * depth, k, ':', end='')
            print_value(value[k], depth + 1)
    else:
        print('  ' * depth, value)


def values_to_struct(value):
    if isinstance(value, nbt.TAG_List):
        return [values_to_struct(i) for i in value]
    elif isinstance(value, nbt.TAG_Compound):
        return {k: values_to_struct(v) for k, v in value.items()}
    elif isinstance(value, (nbt._TAG_Numeric, nbt.TAG_String, nbt.TAG_Int_Array)):
        return value.value
    else:
        return value


if __name__ == '__main__':
    filename = r'E:\mc backupy\soucasny server svety\scitaniautismus\playerdata\0caa1425-e0ec-3150-9027-9b06a72d572e.dat'
    nbtfile = nbt.NBTFile(filename, 'rb')
    print(nbtfile.name)
    data = values_to_struct(nbtfile)

    # print(json.dumps(data, indent='  '))
    # with open(osp.basename(filename) + '.json', 'w+') as fp:
    #     json.dump(data, fp, indent=4)
    with open(osp.basename(filename) + '.yaml', 'w+') as fp:
        yaml.dump(data, fp, indent=4)

    filename_2 = r'E:\mc backupy\soucasny server svety\scitaniautismus\playerdata\5e08b14e-fba4-3956-92f0-eb95c5286908.dat'
    nbtfile_2 = nbt.NBTFile(filename_2, 'rb')
    data_2 = values_to_struct(nbtfile_2)

    with open(osp.basename(filename_2) + '.yaml', 'w+') as fp:
        yaml.dump(data_2, fp, indent=4)

    # adding content of nbtfile to nbtfile_2
    nbtfile_2['Inventory'].extend(nbtfile['Inventory'])
    nbtfile_2['ForgeCaps'].update(nbtfile['ForgeCaps'])

    nbtfile_2.write_file('merged_files.dat')

    nbtfile_merged = nbt.NBTFile('merged_files.dat', 'rb')
    data_merged = values_to_struct(nbtfile_merged)

    with open('merged_files.yaml', 'w+') as fp:
        yaml.dump(data_merged, fp, indent=4)
