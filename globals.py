import discord
import re, json, requests
import time
# for final output of commands
start = time.time()
finalOutput = discord.Embed(title="  ", colour=0x1978E3)

# sb item data for command choices
SB_ITEMS_DATA = requests.get(
  "https://api.hypixel.net/resources/skyblock/items").json()
print(len(SB_ITEMS_DATA['items']), "items")
SB_BZ_DATA = requests.get(
  "https://api.hypixel.net/skyblock/bazaar").json()["products"]
BASE_ITEMS = [
  "lapis lazuli", "coal", "diamond", "redstone", "gold ingot", "iron ingot",
  "wheat", "cobblestone", "oak log", "birch log", "bone", "spruce log",
  "dark oak log", "jungle log"
]
SB_ITEMS_DICT = {}
SB_ITEMS_LIST = []
SB_AH_LIST = []
SB_BZ_LIST = []
SB_CRAFTABLE_ITEMS = []
SB_CRAFTABLE_ITEMS_DATA = {}
SB_FORGE_ITEMS = []
SB_FORGE_ITEMS_DATA = {}
SB_NON_CRAFTABLES = []
SB_INVALID_ITEMS = []
SB_MINIONS_LIST = []
SB_SOULBOUND_LIST = []
SB_CATEGORY_LIST = []
for item in SB_ITEMS_DATA["items"]:
  itemName = item["name"]
  #print(i, itemName)
  itemID = item["id"]
  try:
    test = item["category"]
    if test not in SB_CATEGORY_LIST:
      SB_CATEGORY_LIST += [test]
    if test == "MEMENTO" or test == "COSMETIC" or test == "NONE":
      SB_NON_CRAFTABLES += [itemName]
    else:
      try:
        test = item["soulbound"]
        SB_SOULBOUND_LIST += [itemName]
      except:
        try:
          test = item["generator"]
          SB_MINIONS_LIST += [itemName]
        except:

          SB_ITEMS_DICT[itemName] = itemID
          SB_REFORGE_LIST
          SB_ITEMS_LIST += [itemName]
          try:
            test = SB_BZ_DATA[itemID]
            SB_BZ_LIST += [itemID]
          except:
            SB_AH_LIST += [itemName]
  except:
    temp = 0
  try:
    test = item["soulbound"]
    SB_SOULBOUND_LIST += [itemName]
  except:
    try:
      test = item["generator"]
      SB_MINIONS_LIST += [itemName]
    except:
      try:
        test = item["REFORGE_STONE"]
        SB_REFORGE_LIST += [itemName]
      except:

        SB_ITEMS_DICT[itemName] = itemID
        SB_REFORGE_LIST
        SB_ITEMS_LIST += [itemName]
        try:
          test = SB_BZ_DATA[itemID]
          SB_BZ_LIST += [itemID]
        except:
          SB_AH_LIST += [itemName]
print("categories:", SB_CATEGORY_LIST)
end = time.time()
print(f"{(end - start)} seconds")
print("Is Done")
