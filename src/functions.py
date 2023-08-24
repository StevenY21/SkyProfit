import re, json, requests
#import globals
import math
import asyncio
import aiohttp
import time


# for getting JSON data
async def req_data(link):
  async with aiohttp.ClientSession() as session:
    async with session.get(link) as response:
      res = await response.json(content_type=None)
      return res


# items that have recipe that isn't accurate in repo
ITEM_FACTOR = {
  "Blaze Powder": 0.5,
  "Sulphuric Coal": 0.25,
  "Gold Nugget": 0.111
}
# more useful vanilla items that have npc prices, or just can't be excluded due to recipes
EXCEPTION_ITEMS = {"Glass Bottle": 6, "Stick": 0, "Vines": 0}
ITEMS_JSON = asyncio.run(
  req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/constants/items.json'
  ))
SB_ITEM_DATA = ITEMS_JSON["item_data"]  # key: item id, value: item data
SB_NAME_ID = ITEMS_JSON["name_to_id"]  # key: item name, value: item id

# note for SB_NAME_ID, due to some ids sharing the same names, IDs for items with "less usefulness" to me are overwritten by the ones that I deem more useful for my commands


# check what item tier and item ah category combo exists in item list
def checkTierCats(itemLst):
  start = time.time()
  tierCats = {
    'SUPREME': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'RARE': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'MYTHIC': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'LEGENDARY': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'EPIC': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'UNCOMMON': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'UNTIERED': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'COMMON': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'VERY_SPECIAL': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'SPECIAL': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    },
    'UNOBTAINABLE': {
      "weapon": [],
      "armor": [],
      "accessories": [],
      "consumables": [],
      "blocks": [],
      "tools": [],
      "misc": []
    }
  }
  for item in itemLst:
    itemID = SB_NAME_ID[item]
    itmTier = SB_ITEM_DATA[itemID]['tier']
    itmCat = SB_ITEM_DATA[itemID]['ah_category']
    if itmCat == 'blocks and tools and misc':
      tierCats[itmTier]["blocks"] += [item]
      tierCats[itmTier]["tools"] += [item]
      tierCats[itmTier]["misc"] += [item]
    else:
      tierCats[itmTier][itmCat] += [item]
  print(tierCats)
  end = time.time()
  print(f'checkTierCats done in {end-start} seconds')
  return tierCats


#get item name to item recipe
# assume item name is fixed to proper form
def get_item_recipe(itemName):
  print(f"item being checked {itemName}")

  try:
    itemID = SB_NAME_ID[itemName]
    if SB_ITEM_DATA[itemID]['base_item'] == True:
      return -2
    if SB_ITEM_DATA[itemID]["category"] == "ENCHANTMENT":
      idLen = len(itemID)
      enchLvl = itemID[-1]
      itemID = itemID[12:(idLen-2)]
      itemID += (f";{enchLvl}")
      print(itemID)
    #get the id from the name
    newItemID = ''
    if ':' in itemID:
      for j in itemID:
        if j == ':':
          newItemID += '-'
        else:
          newItemID += j
    else:
      newItemId = itemID
    itemData2 = asyncio.run(
      req_data(
        f'https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master/items/{newItemId}.json'
      ))
    recipeData = itemData2['recipe']
    #make english readable
    properRecipe = {}
    #print('recipeData that neesd processing', recipeData)
    for section in recipeData:
      #print(recipeData[section])
      if recipeData[section] != '':
        item = recipeData[section].split(':')
        itemID = item[0]
        fixedID = ""
        itemName2 = ""
        if "-" in itemID:
          for chr in itemID:
            if chr == '-':
              fixedID += ':'
            else:
              fixedID += chr

          itemName2 = SB_ITEM_DATA[fixedID]['name']
        else:
          itemName2 = SB_ITEM_DATA[itemID]['name']
        if itemName2 in properRecipe:
          properRecipe[itemName2] += int(item[1])
        else:
          properRecipe[itemName2] = int(item[1])
    try:
      factor = ITEM_FACTOR[itemName]
      print(f"special item hit {itemName}")
      for item in properRecipe:
        properRecipe[item] = properRecipe[item] * factor
      return properRecipe
    except:
      return properRecipe
  # note that this sometimes doesn't work, and just returns None in the try part, look into it later but for now its working fine
  except:
    return -1


# assume recipe given has all valid items
def get_raw_recipe(recipe):
  start = time.time()
  tempRec = recipe
  recipelst = []  # all recipes that have been created so far
  rawRecipe = {}
  temp = None
  recSize = len(recipe)
  numDone = 0  # number of items in recipe that have reached its most basic component
  hasExcluded = False  # has vanilla items that are salable on ah, but shouldn't be bought from AH
  # the only exception is Vines so far
  procRecs = {}  # all the recipes that have already been processed stored here
  #print(recipe, "recipe to be processed into raw form")
  while True:
    for material in tempRec:
      #print(material, "curr material to process in get_raw_recipe")
      try:
        temp = procRecs[material]
        print(f' recipe for {material} found: {temp}')
      except:
        temp = get_item_recipe(material)
      if temp == -1 or temp == -2:
        rawRecipe[material] = tempRec[material]
        numDone += 1
      else:
        #print(temp)
        for mat in temp:
          #print(mat, f"in {temp}")
          itemID = SB_NAME_ID[mat]
          if SB_ITEM_DATA[itemID]["vanilla"] and SB_ITEM_DATA[itemID]["in_ah"]:
            if mat not in EXCEPTION_ITEMS:
              hasExcluded = True
          if mat not in rawRecipe:
            rawRecipe[mat] = int(math.ceil(tempRec[material] * temp[mat]))
          else:
            rawRecipe[mat] += int(math.ceil(tempRec[material] * temp[mat]))
      procRecs[material] = temp
    if numDone == recSize:
      break
    else:
      print(f"raw recipe so far {rawRecipe}")
      if hasExcluded == False:
        recipelst.append(rawRecipe)
      tempRec = rawRecipe
      recSize = len(rawRecipe)
      rawRecipe = {}
      numDone = 0
      hasExcluded = False
  end = time.time()
  print(f"get_raw_recipe time {end - start} seconds")
  return recipelst


# gets items bazaar cost
# can assume id is valid
def findCost(itemID):
  #print(f"item id being checked: {item_ID}")
  start = time.time()
  itemName = SB_ITEM_DATA[itemID]['name']
  SB_ITEM_DATA[itemID]["in_bz"]
  if SB_ITEM_DATA[itemID]["in_bz"] == False:
    if SB_ITEM_DATA[itemID]["soulbound"] != 'N/A':  # if it is soulboumd
      return -3
    elif itemName in EXCEPTION_ITEMS:  # if it is sold by npc
      return EXCEPTION_ITEMS[itemName]
    elif SB_ITEM_DATA[itemID]['vanilla'] and SB_ITEM_DATA[itemID][
        'in_ah']:  # for vanilla items found in auction
      # for vanilla items with no recipe
      # so far only applied to vines
      return -4
    else:
      return -1
  else:
    itemSellPrice = asyncio.run(
      req_data("https://api.hypixel.net/skyblock/bazaar")
    )["products"][itemID]['sell_summary']
    end = time.time()
    print(f"findCost time for {itemID} is {end - start}")
    if itemSellPrice == []:  # if no one is selling it bazaar
      return -2
    else:
      return itemSellPrice[0]["pricePerUnit"]
