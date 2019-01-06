from nbt import nbt, chunk, region, world
from pprint import pprint
import json
import os.path as osp
import yaml
from absl import flags
from absl import logging
from absl import app


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
    playerdata_dir = ''
    usercache_file =
    if not osp.exists(filename):
        raise RuntimeError("File {} does not exist.".format(filename))
    nbtfile = nbt.NBTFile(filename, 'rb')
    print(nbtfile.name)
    data = dict()
    for field in nbtfile:
        value = nbtfile[field]
        data[field] = values_to_struct(value)

    with open(osp.basename(filename) + '.yaml', 'w+') as fp:
        yaml.dump(data, fp, indent=4)


if __name__ == '__main__':
    app.run(main)
