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
  'FISHING_ROD': 'misc',
  'WAND': 'misc',
  'PORTAL': 'misc',
  'BOW': "weapon",
  'NONE': 'misc',
  'DUNGEON_PASS': 'none',
  'ARROW': 'none',
  'SPADE': 'misc',
  'PICKAXE': 'misc',
  'DEPLOYABLE': 'misc',
  'DRILL': 'tools',
  'SHEARS': 'misc',
  'BRACELET': 'misc',
  'GAUNTLET': 'misc',
  'LONGSWORD': 'weapon',
  'TRAVEL_SCROLL': 'misc',
  'ARROW_POISON': 'bz',
  'FISHING_WEAPON': 'misc'
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
# bandanas don't exist in public api for some reason
SB_NAME_DICT["Green Bandana"] = "GREEN_BANDANA"
SB_ITEM_DICT["GREEN_BANDANA"] = {
  'name': "Green Bandana",
  'material': "SKULL_ITEM",
  'tier': "EPIC",
  'category': 'PET_ITEM',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Yellow Bandana"] = "YELLOW_BANDANA"
SB_ITEM_DICT["YELLOW_BANDANA"] = {
  'name': "Yellow Bandana",
  'material': "SKULL_ITEM",
  'tier': "RARE",
  'category': 'PET_ITEM',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'misc',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Hive Barn Skin"] = "HIVE_BARN_SKIN"
SB_ITEM_DICT["HIVE_BARN_SKIN"] = {
  'name': "Hive Barn Skin",
  'material': "STAINED_CLAY",
  'tier': "LEGENDARY",
  'category': 'COSMETIC',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'blocks',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Trading Post Barn Skin"] = "TRADING_POST_BARN_SKIN"
SB_ITEM_DICT["TRADING_POST_BARN_SKIN"] = {
  'name': "Trading Post Barn Skin",
  'material': "FENCE",
  'tier': "UNCOMMON",
  'category': 'COSMETIC',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'blocks',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Autumn Hut Barn Skin"] = "AUTUMN_HUT_BARN_SKIN"
SB_ITEM_DICT["AUTUMN_HUT_BARN_SKIN"] = {
  'name': "Autumn Hut Barn Skin",
  'material': "LEAVES",
  'tier': "UNCOMMON",
  'category': 'COSMETIC',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'blocks',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Castle Barn Skin"] = "CASTLE_BARN_SKIN"
SB_ITEM_DICT["CASTLE_BARN_SKIN"] = {
  'name': "Castle Barn Skin",
  'material': "COBBLESTONE",
  'tier': "LEGENDARY",
  'category': 'COSMETIC',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'blocks',
  'base_item': False,
  'vanilla': False,
}
SB_NAME_DICT["Bamboo Barn Skin"] = "BAMBOO_BARN_SKIN"
SB_ITEM_DICT["BAMBOO_BARN_SKIN"] = {
  'name': "Bamboo Barn Skin",
  'material': "STICK",
  'tier': "EPIC",
  'category': 'COSMETIC',
  'soulbound': 'N/A',
  'furniture': 'N/A',
  'generator': 'N/A',
  'in_bz': False,
  'in_ah': True,
  'ah_category': 'misc',
  'base_item': False,
  'vanilla': False,
}
# item name hay bale has both a furniture and the actual thing, which is dumb
SB_ITEM_DICT["HAY_BLOCK"]['vanilla'] = True
SB_NAME_DICT["Hay Bale"] = "HAY_BLOCK"
# for some reason 2 different griffin feathers exist in item data, with one not even an actual item
SB_NAME_DICT['Griffin Feather'] = 'GRIFFIN_FEATHER'
# Manually processing base items:
BASE_ITEMS = [
  "Lapis Lazuli", "Coal", "Diamond", "Redstone", "Gold Ingot", "Iron Ingot",
  "Wheat", "Cobblestone", "Bone", "Emerald", "Slimeball", "Snow Block",
  "Glass Bottle", "Stick", "Magma Cream", "Leather"
]
for i in BASE_ITEMS:
  itemID = SB_NAME_DICT[i]
  SB_ITEM_DICT[itemID]['base_item'] = True
# adding in abicase ids:
SB_ABICASES = {
  "Sumsung© G3 Abicase": "ABICASE_SUMSUNG_1",
  "Sumsung© GG Abicase": "ABICASE_SUMSUNG_2",
  "Rezar® Abicase": "ABICASE_REZAR",
  "Blue™ but Red Abicase": "ABICASE_BLUE_RED",
  "Actually Blue™ Abicase": "ABICASE_BLUE_BLUE",
  "Blue™ but Green Abicase": "ABICASE_BLUE_GREEN",
  "Blue™ but Yellow Abicase": "ABICASE_BLUE_YELLOW",
  "Lighter Blue™ Abicase": "ABICASE_BLUE_AQUA",
}
for i in SB_ABICASES:
  SB_NAME_DICT[i] = SB_ABICASES[i]
# all salable enchants that can be combined in an anvil or created by combining enchants in an anvil
# and the bits enchants lol
ENCHANTS_LIST = {
  "Expertise": ["I"],
  "Cultivating": ["I"],
  "Compact": ["I"],
  "Champion": ["I"],
  "Hecatomb": ["I"],
  "Sunder": ["I", "II", "III", "IV", "V"],
  "Green Thumb": ["I", "II", "III", "IV", "V"],
  "Dedication": ["I", "II", "III", "IV", "V"],
  "Infinite Quiver": ["VI", "VII", "VIII", "IX", "X"],
  "Feather Falling": ["VI", "VII", "VIII", "IX", "X"],
  "Big Brain": ["III", "IV", "V"],
  "Dragon Hunter": ["I", "II", "III", "IV", "V"],
  "Mana Steal": ["I", "II", "III"],
  "Charm": ["I", "II", "III", "IV", "V"],
  "Pristine": ["I", "II", "III", "IV", "V"],
  "Prosperity": ["I", "II", "III", "IV", "V"],
  "Reflection": ["I", "II", "III", "IV", "V"],
  "Overload": ["I", "II", "III", "IV", "V"],
  "Quantum": ["III", "IV", "V"],
  "Smarty Pants": ["I", "II", "III", "IV", "V"],
  "Transylvanian": ["IV", "V"],
  "Vicious": ["III", "IV", "V"],
  "Rejuvenate": ["I", "II", "III", "IV", "V"],
  "Cayenne": ["IV", "V"],
  "Tabasco": ["II", "III"],
  "Strong Mana": ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Ferocious Mana":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Mana Vampire":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Hardened Mana":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Turbo-Cacti": ["I", "II", "III", "IV", "V"],
  "Turbo-Cane": ["I", "II", "III", "IV", "V"],
  "Turbo-Carrot": ["I", "II", "III", "IV", "V"],
  "Turbo-Cocoa": ["I", "II", "III", "IV", "V"],
  "Turbo-Melon": ["I", "II", "III", "IV", "V"],
  "Turbo_Mushrooms": ["I", "II", "III", "IV", "V"],
  "Turbo-Potato": ["I", "II", "III", "IV", "V"],
  "Turbo-Pumpkin": ["I", "II", "III", "IV", "V"],
  "Turbo-Warts": ["I", "II", "III", "IV", "V"],
  "Turbo-Wheat": ["I", "II", "III", "IV", "V"]
}
# all salable ult enchants that can be combined in an anvil or created by combining enchants in an anvil
ULT_ENCHANTS = {
  "Bank": ["I", "II", "III", "IV", "V"],
  "Bobbin Time": ["III", "IV", "V"],
  "Chimera": ["I", "II", "III", "IV", "V"],
  "Combo": ["I", "II", "III", "IV", "V"],
  "Duplex": ["I", "II", "III", "IV", "V"],
  "Fatal Tempo": ["I", "II", "III", "IV", "V"],
  "Flash": ["I", "II", "III", "IV", "V"],
  "Habanero Tactics": ["IV", "V"],
  "Inferno": ["I", "II", "III", "IV", "V"],
  "Last Stand": ["I", "II", "III", "IV", "V"],
  "Legion": ["I", "II", "III", "IV", "V"],
  "No Pain No Gain": ["I", "II", "III", "IV", "V"],
  "Rend": ["I", "II", "III", "IV", "V"],
  "Soul Eater": ["I", "II", "III", "IV", "V"],
  "Swarm": ["I", "II", "III", "IV", "V"],
  "The One": ["IV", "V"],
  "Ultimate Jerry": ["I", "II", "III", "IV", "V"],
  "Ultimate Wise": ["I", "II", "III", "IV", "V"],
  "Wisdom": ["I", "II", "III", "IV", "V"]
}
BITS_ENCHANTS = {
  "Expertise": ["I"],
  "Cultivating": ["I"],
  "Compact": ["I"],
  "Champion": ["I"],
  "Hecatomb": ["I"]
}
# all these categorized enchants meets the following requiremnts
# all salable enchants that can be combined in an anvil or created by combining enchants in an anvil
DUNGEON_ENCHANTS = {
  "Bank": ["I", "II", "III", "IV", "V"],
  "Combo": ["I", "II", "III", "IV", "V"],
  "Rejuvenate": ["I", "II", "III", "IV", "V"],
  "Infinite Quiver": ["VI", "VII", "VIII", "IX", "X"],
  "Feather Falling": ["VI", "VII", "VIII", "IX", "X"],
  "Overload": ["I", "II", "III", "IV", "V"],
  "Last Stand": ["I", "II", "III", "IV", "V"],
  "Legion": ["I", "II", "III", "IV", "V"],
  "No Pain No Gain": ["I", "II", "III", "IV", "V"],
  "Rend": ["I", "II", "III", "IV", "V"],
  "Soul Eater": ["I", "II", "III", "IV", "V"],
  "Swarm": ["I", "II", "III", "IV", "V"],
  "Ultimate Jerry": ["I", "II", "III", "IV", "V"],
  "Ultimate Wise": ["I", "II", "III", "IV", "V"],
  "Wisdom": ["I", "II", "III", "IV", "V"]
}
FARMING_ENCHANTS = {
  "Sunder": ["I", "II", "III", "IV", "V"],
  "Green Thumb": ["I", "II", "III", "IV", "V"],
  "Dedication": ["I", "II", "III", "IV", "V"],
  "Turbo-Cacti": ["I", "II", "III", "IV", "V"],
  "Turbo-Cane": ["I", "II", "III", "IV", "V"],
  "Turbo-Carrot": ["I", "II", "III", "IV", "V"],
  "Turbo-Cocoa": ["I", "II", "III", "IV", "V"],
  "Turbo-Melon": ["I", "II", "III", "IV", "V"],
  "Turbo_Mushrooms": ["I", "II", "III", "IV", "V"],
  "Turbo-Potato": ["I", "II", "III", "IV", "V"],
  "Turbo-Pumpkin": ["I", "II", "III", "IV", "V"],
  "Turbo-Warts": ["I", "II", "III", "IV", "V"],
  "Turbo-Wheat": ["I", "II", "III", "IV", "V"]
}
FISHING_ENCHANTS = {
  "Flash": ["I", "II", "III", "IV", "V"],
  "Charm": ["I", "II", "III", "IV", "V"],
  "Bobbin Time": ["III", "IV", "V"],
  "Legion": ["I", "II", "III", "IV", "V"]
}
KUUDRA_ENCHANTS = {
  "Strong Mana": ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Ferocious Mana":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Mana Vampire":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Hardened Mana":
  ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
  "Inferno": ["I", "II", "III", "IV", "V"],
  "Fatal Tempo": ["I", "II", "III", "IV", "V"]
}
RIFT_ENCHANTS = {
  "Reflection": ["I", "II", "III", "IV", "V"],
  "Transylvanian": ["IV", "V"],
  "Quantum": ["III", "IV", "V"]
}
EQUIPMENT_ENCHANTS = {
  "Cayenne": ["IV", "V"],
  "Green Thumb": ["I", "II", "III", "IV", "V"],
  "Prosperity": ["I", "II", "III", "IV", "V"],
  "Quantum": ["III", "IV", "V"]
}
SLAYER_ENCHANTS = {
  "Smarty Pants": ["I", "II", "III", "IV", "V"],
  "Mana Steal": ["I", "II", "III"],
}
DA_ENCHANTS = {"Big Brain": ["III", "IV", "V"], "Vicious": ["III", "IV", "V"]}
CHILI_PEPPER_ENCHANTS = {
  "Cayenne": ["IV", "V"],
  "Tabasco": ["II", "III"],
  "Habanero Tactics": ["IV", "V"],
  "Duplex": ["I", "II", "III", "IV", "V"]
}
# idk how to categorize pristine lol
PRISTINE_ENCHANT = {"Pristine": ["I", "II", "III", "IV", "V"]}
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
    modName = modName.replace("-", "_")
    itemID = ""
    if enchant == "Turbo-Cacti":
      itemID = f"ENCHANTMENT_TURBO_CACTUS_{numLvl}"
    else:
      itemID = f"ENCHANTMENT_{modName.upper()}_{numLvl}"
    itemName = ""
    if numEnc == 1:
      SB_NAME_DICT[enchant] = itemID
      itemName = enchant
    else:
      # sunder does not use roman numerals for some reason
      if enchant == "Sunder" and lvl != "I":
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
    SB_NAME_FIX[itemName.lower()] = itemName
for enchant in ULT_ENCHANTS:
  for lvl in ULT_ENCHANTS[enchant]:
    numLvl = ENCHANT_LVLS[lvl]
    modName = enchant.replace(" ", "_")
    modName = modName.replace("-", "_")
    itemID = ""
    if "Ultimate" not in enchant:
      itemID = f"ENCHANTMENT_ULTIMATE_{modName.upper()}_{numLvl}"
    else:
      itemID = f"ENCHANTMENT_{modName.upper()}_{numLvl}"
    itemName = f"{enchant} {lvl}"
    SB_NAME_DICT[itemName] = itemID
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
    SB_NAME_FIX[itemName.lower()] = itemName
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
with open("src/constants/items.json", "w") as outfile:
  json.dump(SB_ITEM_DATA, outfile)
with open("src/constants/bits_shop.json", "w") as outfile:
  json.dump(SB_BITS_SHOP, outfile)
print(SB_ITEM_DICT["SIL_EX"])
end = time.time()
print(f"{(end - start)} seconds")
print("Globals Done")
