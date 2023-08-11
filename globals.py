import discord
import re, json, requests
import time
import aiohttp
import asyncio
import msgspec
import pandas as pd
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
# Vanilla items that have uses in skyblock
USEFUL_VANILLA_ITEMS = [
  "Lapis Lazuli", "Coal", "Diamond", "Redstone", "Gold Ingot", "Iron Ingot",
  "Wheat", "Cobblestone", "Bone", "Emerald", "Slimeball", "Snow Block", "Ice",
  "Packed Ice", "Oak Log", "Birch Log", "Spruce Log", " Dark Oak Log",
  "Acacia Log", "Jungle Log", "Endstone", "Bone", "Rotten Flesh", "Blaze Rod",
  "Spider Eye", "Nether Wart", "Pumpkin", "Melon", "Ink Sac", "Raw Fish",
  "Salmon", "Pufferfish", "Ender Pearl", "Prismarine Shard",
  "Prismarine Crystals", "Flint", "Obsidian", "Raw Porkchop", "Raw Chicken",
  "Cobblestone", "Raw Beef", "Raw Mutton", "Raw Cod", "Raw Salmon", "Potato",
  "Carrot", "Red Mushroom", "Brown Mushroom"
]
USELESS_VANILLA_ITEMS = []
SB_ITEMS_DICT = {}  # key: item name, value: item id
SB_NAME_FIX = {
}  # key: item name in lower case, value: item name's proper uppercase form
SB_ID_DICT = {}  # key: item id, value: item name
SB_MAT_DICT = {}  # key: item id, value: item material
SB_AH_DICT = {}  # key: item name, value: true or false
SB_BZ_DICT = {}  # key: item name, value: true or false
SB_CRAFTPROFIT_DATA = {
}  # key: valid craftprofit item id, value: item crafting recipe
SB_FORGE_ITEMS_DATA = {
}  # key: valid forgeprofit item id, value: item forge recipe
SB_NONCRAFTABLES_LIST = [
]  # list of all items that cannot be crafted or forged
SB_NONCRAFTABLES_DICT = {}  # key: item name, value: true or false
SB_INVALID_ITEMS = []  # just in case if some wacky items appear
SB_MINIONS_LIST = []  # all minions with all tiers
SB_SOULBOUND_LIST = []  # all soulbound items
SB_SOULBOUND_DICT = {}  #key: item name, value: true or false
SB_CATEGORY_LIST = []  # all categories in hypixel sb items data
BASE_ITEMS = [
  "Lapis Lazuli", "Coal", "Diamond", "Redstone", "Gold Ingot", "Iron Ingot",
  "Wheat", "Cobblestone", "Bone", "Emerald", "Slimeball", "Snow Block",
  "Glass Bottle", "Stick"
]
EXCLUDED_ITEMS = [
  "Block of Coal", "Block of Iron", "Block of Gold", "Block of Diamond",
  "Block of Emerald", "Lapis Lazuli Block", "Blaze Powder", "Block of Quartz"
]
BASE_ITEMS_DICT = {} # key: item name, value: true or false
EXCLUDED_ITEMS_DICT = {} # key: item name, value: true or false

SB_BITS_SHOP_1 = {
  "God Potion": 1500,
  "Kismet Feather": 1350,
  "Kat Flower": 500,
  "Matriarch's Perfume": 1200,
  "Hologram": 2000,
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
  "Hecatomb": 6000,
  "Accessory Enrichment Swapper": 200
}
# no abicase filter
SB_BITS_SHOP_2 = {
  "God Potion": 1500,
  "Kismet Feather": 1350,
  "Kat Flower": 500,
  "Matriarch's Perfume": 1200,
  "Hologram": 2000,
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
  "Abiphone Contacts Trio": 6450,
  "Pure White Dye": 250000,
  "Pure Black Dye": 250000,
  "Expertise": 4000,
  "Compact": 4000,
  "Cultivating": 4000,
  "Champion": 4000,
  "Hecatomb": 6000,
  "Accessory Enrichment Swapper": 200
}
# no enrichments filter
SB_BITS_SHOP_3 = {
  "God Potion": 1500,
  "Kismet Feather": 1350,
  "Kat Flower": 500,
  "Matriarch's Perfume": 1200,
  "Hologram": 2000,
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
# no abicase and enrichments filter
SB_BITS_SHOP_4 = {
  "God Potion": 1500,
  "Kismet Feather": 1350,
  "Kat Flower": 500,
  "Matriarch's Perfume": 1200,
  "Hologram": 2000,
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
  "Abiphone Contacts Trio": 6450,
  "Pure White Dye": 250000,
  "Pure Black Dye": 250000,
  "Expertise": 4000,
  "Compact": 4000,
  "Cultivating": 4000,
  "Champion": 4000,
  "Hecatomb": 6000,
}
# bits multiplier based on fame rank
SB_BITS_FACTOR = {
  "New Player": 1.0,
  'Settler': 1.1,
  'Citizen': 1.2,
  'Contributor': 1.3,
  'Philanthropist': 1.4,
  'Patron': 1.6,
  'Famous Player': 1.8,
  'Attaché': 1.9,
  'Ambassador': 2.0,
  'Stateperson': 2.04,
  'Senator': 2.08,
  'Dignitary': 2.12,
  'Councilor': 2.16,
  'Minister': 2.2,
  'Premier': 2.22,
  'Chancellor': 2.24,
  'Supreme': 2.26
}
# all enchants
BITS_ENCHANTS_LIST = [
  "Expertise", "Cultivating", "Compact", "Champion", "Hecatomb"
]
# Stars
SB_STARS = ["✪✪✪✪✪", "➊", "➋", "➌", "➍", "➎"]
# Sorting out all the items
for item in SB_ITEMS_DATA["items"]:
  itemName = item["name"]
  itemID = item["id"]
  itemMat = item["material"]
  if item.get("furniture") != None:
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
    SB_BITS_SHOP_1[itemName] = 5000
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
        if itemID == itemMat and itemName not in USEFUL_VANILLA_ITEMS:
          SB_BZ_DICT[itemID] = False
          SB_AH_DICT[itemName] = False
        else:
          SB_BZ_DICT[itemID] = False
          SB_AH_DICT[itemName] = True
  SB_ITEMS_DICT[itemName] = itemID
  SB_ID_DICT[itemID] = itemName
  SB_MAT_DICT[itemID] = itemMat
  SB_NAME_FIX[itemName.lower()] = itemName
  if "Stairs" in itemName or "Fence" in itemName or "Chiseled" in itemName or "Granite" in itemName or "Diorite" in itemName or "Andesite" in itemName or "Slab" in itemName or "Planks" in itemName:
    
    EXCLUDED_ITEMS_DICT[itemName] = True
  else:
    EXCLUDED_ITEMS_DICT[itemName] = False
  BASE_ITEMS_DICT[itemName] = False
#i = 0
# Processing excluded items and base items:
for i in BASE_ITEMS:
  BASE_ITEMS_DICT[i] = True
for i in EXCLUDED_ITEMS:
  EXCLUDED_ITEMS_DICT[i] = True
#Processing Enchants Here:
for enchant in BITS_ENCHANTS_LIST:
  SB_ITEMS_DICT[enchant] = f"ENCHANTMENT_{enchant.upper()}_1"
  SB_ID_DICT[f"ENCHANTMENT_{enchant.upper()}_1"] = enchant
  SB_SOULBOUND_DICT[enchant] = False
  EXCLUDED_ITEMS_DICT[enchant] = False
  BASE_ITEMS_DICT[enchant] = False
#create the filters for cookieprofit
SB_BITS_FILTER = {
  "None": SB_BITS_SHOP_1,
  "No Abicase": SB_BITS_SHOP_2,
  "No Enrichment": SB_BITS_SHOP_3,
  "No Abicase and Enrichment": SB_BITS_SHOP_4
}
# manually fix some of them due to strange items in hypixel items data
# currently going to manually fix the enchantments
SB_ITEMS_DICT["Griffin Feather"] = 'GRIFFIN_FEATHER'
SB_ITEMS_DICT["Hay Bale"] = "HAY_BLOCK"
SB_ID_DICT["HAY_BLOCK"] = "Hay Bale"
SB_ITEMS_DICT["Jumbo Backpack"] = "JUMBO_BACKPACK"
SB_ITEMS_DICT["JUMBO_BACKPACK"] = "Jumbo Backpack"
SB_ITEMS_DICT["Greater Backpack"] = "GREATER_BACKPACK"
SB_ITEMS_DICT["GREATER_BACKPACK"] = "Greater Backpack"
SB_ITEMS_DICT["Large Backpack"] = "LARGE_BACKPACK"
SB_ITEMS_DICT["LARGE_BACKPACK"] = "Large Backpack"
SB_ITEMS_DICT["Medium Backpack"] = "MEDIUM_BACKPACK"
SB_ITEMS_DICT["MEDIUM_BACKPACK"] = "Medium Backpack"
SB_ITEMS_DICT["Small Backpack"] = "SMALL_BACKPACK"
SB_ITEMS_DICT["SMALL_BACKPACK"] = "Small Backpack"
# for personal debugging
print(len(SB_ITEMS_DATA['items']), "items")
print("items in sb items dict:", len(SB_ITEMS_DICT))
print("soulbound items", len(SB_SOULBOUND_LIST))
print("unique minions", len(SB_MINIONS_LIST))
print("bits shop items", len(SB_BITS_SHOP_1))
print("uncraftable items", len(SB_NONCRAFTABLES_LIST))
end = time.time()
print(f"{(end - start)} seconds")
print("Globals Done")

