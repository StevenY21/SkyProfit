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
      itemID = itemID[12:(idLen - 2)]
      itemID += (f";{enchLvl}")
      print(itemID)
    #get the id from the name
    itemID.replace(":", "-")
    itemData2 = asyncio.run(
      req_data(
        f'https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master/items/{itemID}.json'
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
        fixedID = itemID.replace("-", ":")
        itemName2 = SB_ITEM_DATA[fixedID]['name']
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
        #print(f' recipe for {material} found: {temp}')
      except:
        temp = get_item_recipe(material)
      if temp == -1 or temp == -2:
        if material in rawRecipe:
          rawRecipe[material] += tempRec[material]
        else:
          rawRecipe[material] = tempRec[material]
        numDone += 1
      else:
        #print(temp)
        for mat in temp:
          itemID = SB_NAME_ID[mat]
          if SB_ITEM_DATA[itemID]["vanilla"] and SB_ITEM_DATA[itemID]["in_ah"]:
            if mat not in EXCEPTION_ITEMS:
              hasExcluded = True
          if mat in rawRecipe:
            rawRecipe[mat] += int(math.ceil(tempRec[material] * temp[mat]))
          else:
            rawRecipe[mat] = int(math.ceil(tempRec[material] * temp[mat]))
      procRecs[material] = temp
    if numDone == recSize:
      break
    else:
      #print(f"raw recipe so far {rawRecipe}")
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
def findCost(itemID, bzData):
  #print(f"item id being checked: {item_ID}")
  itemName = SB_ITEM_DATA[itemID]['name']
  if SB_ITEM_DATA[itemID]["in_bz"] == False:
    if SB_ITEM_DATA[itemID]["soulbound"] != 'N/A':  # if it is soulboumd
      return -3
    elif SB_ITEM_DATA[itemID]['vanilla'] and SB_ITEM_DATA[itemID][
        'in_ah']:  # for vanilla items found in auction
      # for vanilla items with no recipe
      if itemName in EXCEPTION_ITEMS:  # if it is sold by npc
        return EXCEPTION_ITEMS[itemName]
      else:
        return -4
    else:
      return -1
  else:
    itemSellPrice = bzData["products"][itemID]['sell_summary']
    if itemSellPrice == []:  # if no one is selling it bazaar
      return -2
    else:
      return itemSellPrice[0]["pricePerUnit"]
