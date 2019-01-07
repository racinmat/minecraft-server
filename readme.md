# These are files for private minecraft server

Just configuration, mods and some other stuff.

During the playing, we encountered few issues.

There are few python scripts for handling the player data in `inventory-handling` directory, 
you can use it to merge neder chest contents, inventories, thaumcraft progres...
but use only at your own risk and always backup.
 
## Lessons learned
- If you use Biomes'o'Plenty as a worldgen, it lags the server during new chunk generation. 
    - Either don't use BoP as a worldgen
    - Or use a [world pregenerator](https://minecraft.curseforge.com/projects/chunkpregenerator) with BoP, and then switch to default worldgen
- Don't place mekanism's Digital Miner on chunk border, it might disappear. There is bug in core minecraft, 
trashing multiblock items on chunk borders when one chunk is unloaded in different time than the other.
- Probably don'T use the twilight forest's charm of keeping, it seemd to be bugging the server in combination with graves.  