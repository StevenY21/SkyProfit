import discord
import re, json, requests
import time
import aiohttp
import asyncio
# for final output of commands
start = time.time()
finalOutput = discord.Embed(title="  ", colour=0x1978E3)


async def req_data(api):
  async with aiohttp.ClientSession() as session:
    async with session.get(api) as response:
      res = await response.json()
      return res


# sb item data for command choices
SB_ITEMS_DATA = asyncio.run(
  req_data("https://api.hypixel.net/resources/skyblock/items"))
print(len(SB_ITEMS_DATA['items']), "items")
SB_BZ_DATA = asyncio.run(
  req_data("https://api.hypixel.net/skyblock/bazaar"))["products"]
BASE_ITEMS = [
  "lapis lazuli", "coal", "diamond", "redstone", "gold ingot", "iron ingot",
  "wheat", "cobblestone", "oak log", "birch log", "bone", "spruce log",
  "dark oak log", "jungle log"
]
SB_ITEMS_DICT = {}
SB_ITEMS_LIST = []
SB_AH_LIST = []
SB_BZ_LIST = []
SB_CRAFTPROFIT_LIST = []
SB_CRAFTABLE_ITEMS_DATA = {}
SB_FORGE_ITEMS = []
SB_FORGE_ITEMS_DATA = {}
SB_NON_CRAFTABLES = []
SB_INVALID_ITEMS = []
SB_MINIONS_LIST = []
SB_SOULBOUND_LIST = []
SB_CATEGORY_LIST = []
SB_BITS_LIST = [
  "God Potion", "Kat Flower", "Heat Core", "Hyper Catalyst Upgrade",
  "Ultimate Carrot Candy Upgrade", "Colossal Experience Bottle Upgrade",
  "Jumbo Backpack Upgrade", "Minion Storage X-pender", "Matriarch's Perfume",
  "Pocket Sack-in-a-Sack", "Portalizer", "Autopet Rules 2-Pack",
  "Abiphone Contacts Trio", "Accessory Enrichment Swapper", "Pure White Dye",
  "Kismet Feather", "Kat Flower", "Actually Blue™ Abicase", "Bits Talisman",
  "Block Zapper", "Blue™ But Green Abicase", "Blue™ But Red Abicase",
  "Blue™ But Yellow Abicase", "Builder's Wand", "Crystal Hollows Sack",
  "Ditto Blob", "Expertise", "Compact", "Cultivating", "Champion", "Hecatomb",
  "Inferno Fuel Block", "Sumsung© GG Abicase", "Sumsung© G3 Abicase",
  "Rezar® Abicase", "Rezar® Abicase", "Lighter Blue™ Abicase",
  "Pure White Dye", "Pure Black Dye", ""
]
SB_ENCHANTS_LIST = {"Expertise: ENCHANTMENT_EXPERTISE_1"}
for item in SB_ITEMS_DATA["items"]:
  itemName = item["name"]
  #print(i, itemName)
  itemID = item["id"]
  try:
    test = item["soulbound"]
    SB_SOULBOUND_LIST += [itemName]
  except:
    test = 0
  try:
    test = item["category"]
    if test not in SB_CATEGORY_LIST:
      SB_CATEGORY_LIST += [test]
    if test == "MEMENTO" or test == "COSMETIC" or test == "NONE":
      SB_NON_CRAFTABLES += [itemName]
    try:
      test = item["generator"]
      SB_MINIONS_LIST += [itemName]
    except:
      test = 0
  except:
    test = 0
  if "Enrichment" in itemName:
    SB_BITS_LIST += [itemName]
  try:
    test = SB_BZ_DATA[itemID]
    SB_BZ_LIST += [itemID]
  except:
    SB_AH_LIST += [itemName]

  SB_ITEMS_DICT[itemName] = itemID
  SB_ITEMS_LIST += [itemName]
print("categories:", SB_CATEGORY_LIST)
end = time.time()
print(f"{(end - start)} seconds")
print("Globals Done")
