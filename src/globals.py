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
# key is category name (some of my own creation and some not), value is what they would be in auction category terms
SB_CATEGORIES = {
  'ENCHANTMENT': 'bz',
  'REFORGE_STONE': 'bz',
  'N/A': 'blocks and tools and misc',
  'SWORD': 'weapon',
  'BOOTS': 'armor',
  'BELT': 'misc',
  'NECKLACE': 'misc',
  'GLOVES': 'misc',
  'HELMET': 'armor',
  'CHESTPLATE': 'armor',
  'ACCESSORY': "accessories",
  'CLOAK': 'misc',
  'LEGGINGS': 'misc',
  'AXE': 'misc',
  'HOE': 'misc',
  'COSMETIC': 'misc',
  'MEMENTO': 'misc',
  'PET_ITEM': 'blocks and tools and misc',
  'BAIT': 'bz',
  'FISHING_ROD': 'tool',
  'WAND': 'tools',
  'PORTAL': 'misc',
  'BOW': "weapon",
  'NONE': 'tools and misc',
  'DUNGEON_PASS': 'none',
  'ARROW': 'none',
  'SPADE': 'tools',
  'PICKAXE': 'tools',
  'DEPLOYABLE': 'tools',
  'DRILL': 'tools',
  'SHEARS': 'tools and misc',
  'BRACELET': 'misc',
  'GAUNTLET': 'misc',
  'LONGSWORD': 'weapon',
  'TRAVEL_SCROLL': 'misc',
  'ARROW_POISON': 'bz',
  'FISHING_WEAPON': 'tools'
}
#with open("src/data/test.json", "w") as outfile:
#  json.dump(SB_CATEGORIES, outfile)
catDict = {
  "weapon": False,
  "armor": False,
  "accessories": True,
  "consumables": True,
  "blocks": True,
  "tools": True,
  "misc": True
}
USEFUL_VANILLA_ITEMS = [
  "Lapis Lazuli", "Coal", "Diamond", "Redstone", "Gold Ingot", "Iron Ingot",
  "Wheat", "Cobblestone", "Bone", "Emerald", "Slimeball", "Snow Block", "Ice",
  "Packed Ice", "Oak Log", "Birch Log", "Spruce Log", " Dark Oak Log",
  "Acacia Log", "Jungle Log", "Endstone", "Bone", "Rotten Flesh", "Blaze Rod",
  "Spider Eye", "Nether Wart", "Pumpkin", "Melon", "Melon Block", "Ink Sac",
  "Raw Fish", "Salmon", "Pufferfish", "Ender Pearl", "Prismarine Shard",
  "Prismarine Crystals", "Flint", "Obsidian", "Raw Porkchop", "Raw Chicken",
  "Cobblestone", "Raw Beef", "Raw Mutton", "Raw Cod", "Raw Salmon", "Potato",
  "Carrot", "Red Mushroom", "Brown Mushroom", "Hay Bale", "Magma Cream"
]
SB_UNIQUE_CAT = {}  # all categories in hypixel sb items data
SB_UNIQUE_TIER = {"SUPREME": False}  # all tiers in hypixel sb items data
# key: item id, value: {'item name':, 'item'}
SB_NAME_DICT = {}  # key: item name, value: item id
SB_NAME_FIX = {
}  # key: item name in lower case, value: item name's proper uppercase form
BASE_ITEMS = [
  "Lapis Lazuli", "Coal", "Diamond", "Redstone", "Gold Ingot", "Iron Ingot",
  "Wheat", "Cobblestone", "Bone", "Emerald", "Slimeball", "Snow Block",
  "Glass Bottle", "Stick", "Magma Cream"
]
EXCLUDED_ITEMS = [
  "Block of Coal", "Block of Iron", "Block of Gold", "Block of Diamond",
  "Block of Emerald", "Lapis Lazuli Block", "Blaze Powder", "Block of Quartz",
  "Golden Carrot", "Glistering Melon"
]

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
#create the filters for cookieprofit
SB_BITS_FILTER = {
  "None": "no_filter",
  "No Abicase": "no_abicases",
  "No Enrichment": "no_enrichments",
  "No Abicase and Enrichment": "no_abicases_and_enrichments"
}
# Stars
SB_STARS = ["✪✪✪✪✪", "➊", "➋", "➌", "➍", "➎"]
SB_ITEM_DICT = {}  # my own version of hypixel sb item data set
"""
example of an item in SB_ITEM_DICT
[item ID]: {
  'name': ,
  'material': ,
  'tier': ,
  'category': ,
  'soulbound': ,
  'furniture': ,
  'generator': ,
  'in_bz': ,
  'in_ah': ,
  'ah_category': ,
  'base_item': ,  
  'vanilla': ,
}
"""

for item in SB_ITEMS_DATA["items"]:
  itemID = item["id"]
  SB_ITEM_DICT[itemID] = {}
  # name
  itemName = item["name"]
  SB_ITEM_DICT[itemID]['name'] = itemName
  # for special dictionaries
  SB_NAME_FIX[itemName.lower()] = itemName
  # processing some enrichments that I am too lazy to type out
  if "Enrichment" in itemName and "Accessory" not in itemName:
    SB_BITS_SHOP_1[itemName] = 5000
    SB_BITS_SHOP_2[itemName] = 5000
  # material
  itemMat = item["material"]
  SB_ITEM_DICT[itemID]['material'] = itemMat
  # tier
  itemTier = ""
  if item.get('tier') != None:
    itemTier = item["tier"]
  else:
    itemTier = "UNTIERED"
  SB_ITEM_DICT[itemID]['tier'] = itemTier
  SB_UNIQUE_TIER[itemTier] = False
  # category
  itemCat = item.get('category')
  if item.get('category') != None:
    SB_UNIQUE_CAT[itemCat] = False
    SB_ITEM_DICT[itemID]['category'] = itemCat
  else:
    SB_UNIQUE_CAT["N/A"] = False
    SB_ITEM_DICT[itemID]['category'] = 'N/A'
  itemSB = item.get("soulbound")
  # soulbound
  if itemSB != None:
    SB_ITEM_DICT[itemID]['soulbound'] = itemSB
  else:
    SB_ITEM_DICT[itemID]['soulbound'] = 'N/A'
  # furniture
  itemFurn = item.get("furniture")
  if itemFurn != None:
    SB_ITEM_DICT[itemID]['furniture'] = itemFurn
  else:
    SB_ITEM_DICT[itemID]['furniture'] = 'N/A'
  # filtering out some decor blocks that I don't need for my purposes
  if 'BUILDER_' not in itemID:
    SB_NAME_DICT[itemName] = itemID
  # generator
  itemGen = item.get('generator')
  if itemGen != None:
    SB_ITEM_DICT[itemID]['generator'] = itemGen
  else:
    SB_ITEM_DICT[itemID]['generator'] = 'N/A'
  # in_bz and in_ah
  if SB_ITEM_DICT[itemID]['soulbound'] == 'N/A' and SB_ITEM_DICT[itemID][
      'generator'] == 'N/A' and 'sack' not in itemName:
    try:
      test = SB_BZ_DATA[itemID]
      SB_ITEM_DICT[itemID]['in_bz'] = True
      SB_ITEM_DICT[itemID]['in_ah'] = False
    except:
      SB_ITEM_DICT[itemID]['in_bz'] = False
      SB_ITEM_DICT[itemID]['in_ah'] = True
  else:
    SB_ITEM_DICT[itemID]['in_bz'] = False
    if itemName == 'Pocket Sack-in-a-Sack':
      SB_ITEM_DICT[itemID]['in_ah'] = True
    else:
      SB_ITEM_DICT[itemID]['in_ah'] = False
  # ah_category
  if SB_ITEM_DICT[itemID]['in_bz'] == True:
    SB_ITEM_DICT[itemID]['ah_category'] = 'bz'
  elif SB_ITEM_DICT[itemID]['in_ah'] == False:
    SB_ITEM_DICT[itemID]['ah_category'] = 'N/A'
  else:
    SB_ITEM_DICT[itemID]['ah_category'] = SB_CATEGORIES[SB_ITEM_DICT[itemID]
                                                        ['category']]
  #base_item gonna be set to false initially
  SB_ITEM_DICT[itemID]['base_item'] = False
  # vanilla
  if itemID == itemMat or 'INK_SAC:' in itemID or 'LOG' in itemID:
    SB_ITEM_DICT[itemID]['vanilla'] = True
  elif "Stairs" in itemName or "Fence" in itemName or "STONE:" in itemID or "Slab" in itemName or "Planks" in itemName or "Rail" in itemName:
    SB_ITEM_DICT[itemID]['vanilla'] = True
  else:
    SB_ITEM_DICT[itemID]['vanilla'] = False
# manually fix some strange items
SB_ITEM_DICT["SPECKLED_MELON"]['vanilla'] = True
SB_ITEM_DICT["SPECKLED_MELON"]['in_ah'] = True
SB_NAME_DICT["Jumbo Backpack"] = "JUMBO_BACKPACK"
SB_ITEM_DICT["JUMBO_BACKPACK"] = {
  'name': "Jumbo Backpack",
  'material': "SKULL_ITEM",
  'tier': 'LEGENDARY',
  'category': 'N/A',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'tools and misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Greater Backpack"] = "GREATER_BACKPACK"
SB_ITEM_DICT["GREATER_BACKPACK"] = {
  'name': "Greater Backpack",
  'material': "SKULL_ITEM",
  'tier': "EPIC",
  'category': 'N/A',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'tools and misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Large Backpack"] = "LARGE_BACKPACK"
SB_ITEM_DICT["LARGE_BACKPACK"] = {
  'name': "Large Backpack",
  'material': "SKULL_ITEM",
  'tier': "EPIC",
  'category': 'N/A',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'tools and misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Medium Backpack"] = "MEDIUM_BACKPACK"
SB_ITEM_DICT["MEDIUM_BACKPACK"] = {
  'name': "Medium Backpack",
  'material': "SKULL_ITEM",
  'tier': "RARE",
  'category': 'N/A',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'tools and misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Small Backpack"] = "SMALL_BACKPACK"
SB_ITEM_DICT["SMALL_BACKPACK"] = {
  'name': "Small Backpack",
  'material': "SKULL_ITEM",
  'tier': "UNCOMMON",
  'category': 'N/A',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'tools and misc',
  'base_item': False,
  'vanilla': False,
}
# item name hay bale has both a furniture and the actual thing, which is dumb
SB_ITEM_DICT["HAY_BLOCK"]['vanilla'] = True
SB_NAME_DICT["Hay Bale"] = "HAY_BLOCK"
# for some reason 2 different griffin feathers exist in item data, with one not even an actual item
SB_NAME_DICT['Griffin Feather'] = 'GRIFFIN_FEATHER'
# Manually processing base items:
for i in BASE_ITEMS:
  itemID = SB_NAME_DICT[i]
  SB_ITEM_DICT[itemID]['base_item'] = True
# all salable enchants
ENCHANTS_LIST = {
  "Expertise": ["I"],
  "Cultivating": ["I"],
  "Compact": ["I"],
  "Champion": ["I"],
  "Hecatomb": ["I"],
  "sunder": ["I", "II", "III", "IV", "V"],
  "green thumb": ["I", "II", "III", "IV", "V"],
  "dedication": ["I", "II", "III", "IV", "V"]
}
# all possible enchant levels
ENCHANT_LVLS = {
  "I": "1",
  "II": "2",
  "III": "3",
  "IV": "4",
  "V": "5",
  "VI": "6",
  "VII": "7",
  "VIII": "8",
  "IX": "9",
  "X": "10"
}
# creating item data for all enchants
for enchant in ENCHANTS_LIST:
  numEnc = len(ENCHANTS_LIST[enchant])
  for lvl in ENCHANTS_LIST[enchant]:
    numLvl = ENCHANT_LVLS[lvl]
    modName = enchant.replace(" ", "_")

    itemID = f"ENCHANTMENT_{modName.upper()}_{numLvl}"
    if numEnc == 1:
      SB_NAME_DICT[enchant] = itemID
      itemName = enchant
    else:
      # sunder does not use roman numerals for some reason
      if enchant == "sunder" and lvl != "I":
        SB_NAME_DICT[f"{enchant} {numLvl}"] = itemID
        itemName = f"{enchant} {numLvl}"
      else:
        SB_NAME_DICT[f"{enchant} {lvl}"] = itemID
        itemName = f"{enchant} {lvl}"
    SB_ITEM_DICT[itemID] = {
      'name': itemName,
      'material': "ENCHANTED_BOOK",
      'tier': "UNTIERED",
      'category': 'ENCHANTMENT',
      'soulbound': 'N/A',
      'furniture': 'N/A',
      'generator': 'N/A',
      'in_bz': True,
      'in_ah': False,
      'ah_category': 'bz',
      'base_item': False,
      'vanilla': False,
    }
SB_BITS_SHOP = {
  "fame_rank": SB_BITS_FACTOR,
  "filter": SB_BITS_FILTER,
  "no_filter": SB_BITS_SHOP_1,
  "no_abicases": SB_BITS_SHOP_2,
  "no_enrichments": SB_BITS_SHOP_3,
  "no_abicases_and_enrichments": SB_BITS_SHOP_4
}
SB_ITEM_DATA = {
  "item_data": SB_ITEM_DICT,
  "name_to_id": SB_NAME_DICT,
  "fix_item_name": SB_NAME_FIX
}
# for updating constants files
#with open("src/constants/items.json", "w") as outfile:
#  json.dump(SB_ITEM_DATA, outfile)
#with open("src/constants/bits_shop.json", "w") as outfile:
#  json.dump(SB_BITS_SHOP, outfile)
print(SB_ITEM_DICT["SIL_EX"])
end = time.time()
print(f"{(end - start)} seconds")
print("Globals Done")
