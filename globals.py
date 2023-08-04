import discord
import re, json, requests
import time
import aiohttp
import asyncio
# for final output of commands
start = time.time()
finalOutput = discord.Embed(title="  ", colour=0x1978E3)


async def req_data(link):
  async with aiohttp.ClientSession() as session:
    async with session.get(link) as response:
      res = await response.json(content_type=None)
      return res

# sb item data for command choices
SB_ITEMS_DATA = asyncio.run(
  req_data("https://api.hypixel.net/resources/skyblock/items"))

SB_BZ_DATA = asyncio.run(
  req_data("https://api.hypixel.net/skyblock/bazaar"))["products"]
BASE_ITEMS = [
  "lapis lazuli", "coal", "diamond", "redstone", "gold ingot", "iron ingot",
  "wheat", "cobblestone", "oak log", "birch log", "bone", "spruce log",
  "dark oak log", "jungle log"
]
# a list for use commands, a dict for data
filter_list = [""]
SB_ITEMS_DICT = {}  # key: item name, value: item id
SB_NAME_FIX = {} # key: item name in lower case, value: item name's proper uppercase form
SB_ID_DICT = {}  # key: item id, value: item name
SB_MAT_DICT = {} # key: item id, value: item material
SB_AH_DICT = {}  # key: item name, value: true or false
SB_BZ_DICT = {}  # key: item name, value: true or false
SB_CRAFTPROFIT_DATA = {}  # key: valid craftprofit item id, value: item crafting recipe
SB_FORGE_ITEMS_DATA = {}  # key: valid forgeprofit item id, value: item forge recipe
SB_NONCRAFTABLES_LIST = [] # list of all items that cannot be crafted or forged
SB_NONCRAFTABLES_DICT = {}  # key: item name, value: true or false
SB_INVALID_ITEMS = []  # just in case if some wacky items appear
SB_MINIONS_LIST = []  # all minions with all tiers
SB_SOULBOUND_LIST = [] # all soulbound items
SB_SOULBOUND_DICT = {}  #key: item name, value: true or false
SB_CATEGORY_LIST = []  # all categories in hypixel sb items data
SB_BITS_DICT = {
  "God Potion": 1500,
  "Kismet Feather": 1350,
  "Kat Flower": 500,
  "Matriarch's Perfume": 1200,
  "Hologram": 2000,
  "Ditto Blob": 600,
  "Builder's Wand": 12000,
  "Block Zapper": 5000,
  "Bits Talisman": 15000,
  "Portalizer": 4800,
  "Autopet Rules 2-Pack": 21000,
  "1 Inferno Fuel Block": 75,
  "64 Inferno Fuel Blocks": 3600,
  "Heat Core": 3000,
  "Hyper Catalyst Upgrade": 300,
  "Ultimate Carrot Candy Upgrade": 8000,
  "Colossal Experience Bottle Upgrade": 1200,
  "Jumbo Backpack Upgrade": 4000,
  "Minion Storage X-pender": 1500,
  "Pocket Sack-in-a-Sack": 8000,
  "Dungeon Sack": 14000,
  "Rune Sack": 14000,
  "Flower Sack": 14000,
  "Dwarven Sack": 14000,
  "Crystal Hollows Sack": 14000,
  "Abiphone Contacts Trio": 6450,
  "Sumsung© G3 Abicase": 15000,
  "Sumsung© GG Abicase": 25000,
  "Rezar® Abicase": 26000,
  "Blue™ but Red Abicase": 17000,
  "Actually Blue™ Abicase": 17000,
  "Blue™ but Green Abicase": 17000,
  "Blue™ but Yellow Abicase": 17000,
  "Lighter Blue™ Abicase": 17000,
  "Pure White Dye": 250000,
  "Pure Black Dye": 250000,
  "Expertise": 4000,
  "Compact": 4000,
  "Cultivating": 4000,
  "Champion": 4000,
  "Hecatomb": 6000
}
SB_ENCHANTS_LIST = {"Expertise: ENCHANTMENT_EXPERTISE_1"}  # all enchants
for item in SB_ITEMS_DATA["items"]:
  itemName = item["name"]
  itemID = item["id"]
  itemMat = item["material"]
  if item.get("furniture") != None:
    test = item["furniture"]
    itemName += "*"
    SB_NONCRAFTABLES_DICT[itemName] = True
    SB_NONCRAFTABLES_LIST += [itemName]
  if item.get("soulbound") != None:
    test = item["soulbound"]
    SB_SOULBOUND_DICT[itemName] = True
    SB_SOULBOUND_LIST += [itemName]
  else:
    SB_SOULBOUND_DICT[itemName] = False
  try:
    test = item["category"]
    if test not in SB_CATEGORY_LIST:
      SB_CATEGORY_LIST += [test]
    if test == "MEMENTO" or test == "COSMETIC" or test == "NONE":
      SB_NONCRAFTABLES_DICT[itemName] = True
      if itemName not in SB_NONCRAFTABLES_LIST:
        SB_NONCRAFTABLES_LIST += [itemName]
    else:
      SB_NONCRAFTABLES_DICT[itemName] = False
  except:
    SB_NONCRAFTABLES_DICT[itemName] = False
  if "Enrichment" in itemName and "Accessory" not in itemName:
    SB_BITS_DICT[itemName] = 5000
  if SB_SOULBOUND_DICT[itemName] == False and "Sack" not in itemName:
    try:
      test = item["generator"]
      SB_MINIONS_LIST += [itemName]
    except:
      try:
        test = SB_BZ_DATA[itemID]
        SB_BZ_DICT[itemID] = True
        SB_AH_DICT[itemName] = False
      except:
        SB_BZ_DICT[itemID] = False
        SB_AH_DICT[itemName] = True
  SB_ITEMS_DICT[itemName] = itemID
  SB_ID_DICT[itemID] = itemName 
  SB_MAT_DICT[itemID] = itemMat
  SB_NAME_FIX[itemName.lower()] = itemName
i = 0
print(len(SB_ITEMS_DATA['items']), "items")
print("items in sb items dict:", len(SB_ITEMS_DICT))
print("soulbound items",len(SB_SOULBOUND_LIST))
print("unique minions", len(SB_MINIONS_LIST))
print("bits shop items", len(SB_BITS_DICT))
print("uncraftable items", len(SB_NONCRAFTABLES_LIST))
print(SB_ITEMS_DICT["Griffin Feather"])
print(SB_SOULBOUND_DICT['Nether Star'])
# manually fix some of them due to strange items in hypixel items
SB_ITEMS_DICT["Griffin Feather"] = 'GRIFFIN_FEATHER'
end = time.time()
print(f"{(end - start)} seconds")
print("Globals Done")
"""
for itemName in SB_ITEMS_DICT:
  if SB_NONCRAFTABLES_DICT[itemName] == False and "glass" not in itemName and "leaves" not in itemName and "dye" not in itemName and itemName not in SB_MINIONS_LIST and SB_SOULBOUND_DICT[itemName] == False:
    itemID = SB_ITEMS_DICT[itemName]
    itemMat = SB_MAT_DICT[itemID]
    if itemID != itemMat:
      try:
        test = asyncio.run(req_data( f'https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master/items/{itemID}.json'))["recipe"]
        print(f"checking if item {i}, {itemName} has rec")
        try:
          test2 = test[0]["type"]
          if test2 == "forge":
            SB_FORGE_ITEMS_DATA[itemID] = test[0]
        except:
          SB_CRAFTPROFIT_DATA[itemID] = test
      except:
        SB_NONCRAFTABLES_DICT[itemName] = True
  i += 1
print(f"{i} end")
"""