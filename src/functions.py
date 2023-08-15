import re, json, requests
import globals
import math
import asyncio
import aiohttp
import time

skyblockItems = globals.SB_ITEMS_DATA
sbItemDict = globals.SB_NAME_DICT
sbIDDict = globals.SB_ID_DICT
sbAHDict = globals.SB_AH_DICT
sbBzDict = globals.SB_BZ_DICT
sbSBDict = globals.SB_SOULBOUND_DICT
sbCatDict = globals.SB_CAT_DICT
sbTierDict = globals.SB_TIER_DICT
BASE_ITEMS = globals.BASE_ITEMS_DICT
sbTiers = globals.SB_UNIQUE_TIER


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
NPC_ITEMS = {"Glass Bottle": 6, "Stick": 0}
# these items can't be bought on bazaar, but are made of items from bz
EXCLUDED_ITEMS = globals.EXCLUDED_ITEMS_DICT
SB_ITEM_DATA = asyncio.run(
  req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/data/items.json'
  ))


# check what item tiers and what item categories exist in list of items
def checkTiers(itemLst):
  tierLst = sbTiers
  for item in itemLst:
    itemID = sbItemDict[item]
    itmTier = SB_ITEM_DATA[itemID]['tier']
    itmCat = SB_ITEM_DATA[itemID]['ah_category']
    tierLst[itmTier] = True
  return tierLst


#get item name to item recipe
# assume item name is fixed to proper form
def get_item_recipe(itemName):
  print(f"item being checked {itemName}")

  try:
    itemID = sbItemDict[itemName]
    if SB_ITEM_DATA[itemID]['base_item'] == True:
      return -2
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
      globals.req_data(
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

          itemName2 = sbIDDict[fixedID]
        else:
          itemName2 = sbIDDict[item[0]]
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
  recipelst = []
  rawRecipe = {}
  temp = None
  recSize = len(recipe)
  numDone = 0  # number of items in recipe that have reached its most basic component
  procRecs = {}  # all the recipes that have already been processed stored here
  #print(recipe, "recipe to be processed into raw form")
  while True:
    for material in tempRec:
      #print(material, "curr material to process in get_raw_recipe")
      try:
        temp = procRecs[material]
      except:
        temp = get_item_recipe(material)
      if temp == -1 or temp == -2:
        if material not in rawRecipe:
          rawRecipe[material] = tempRec[material]
        numDone += 1
      else:
        #print(temp)
        for mat in temp:
          #print(mat, f"in {temp}")
          if mat not in rawRecipe:
            rawRecipe[mat] = int(math.ceil(tempRec[material] * temp[mat]))
          else:
            rawRecipe[mat] += int(math.ceil(tempRec[material] * temp[mat]))
      procRecs[material] = temp
    if numDone == recSize:
      break
    else:
      #print(f"raw recipe so far {rawRecipe}")
      recipelst.append(rawRecipe)
      tempRec = rawRecipe
      recSize = len(rawRecipe)
      rawRecipe = {}
      numDone = 0
  end = time.time()
  print(f"get_raw_recipe time {end - start} seconds")
  return recipelst


# gets items bazaar cost
# can assume id is valid
def findCost(itemID):
  #print(f"item id being checked: {item_ID}")
  start = time.time()
  itemName = sbIDDict[itemID]
  SB_ITEM_DATA[itemID]["in_bz"]
  if SB_ITEM_DATA[itemID]["in_bz"] == False:
    if SB_ITEM_DATA[itemID]["soulbound"] != 'N/A':  # if it is soulboumd
      return -3
    elif itemName in NPC_ITEMS:  # if it is sold by npc
      return NPC_ITEMS[itemName]
    elif SB_ITEM_DATA[itemID]['vanilla'] and SB_ITEM_DATA[itemID][
        'in_ah']:  # for items that have to be crafted anyways
      return -4
    else:
      return -1
  else:
    itemSellPrice = asyncio.run(
      globals.req_data("https://api.hypixel.net/skyblock/bazaar")
    )["products"][itemID]['sell_summary']
    end = time.time()
    print(f"findCost time for {itemID} is {end - start}")
    if itemSellPrice == []:  # if no one is selling it bazaar
      return -2
    else:
      return itemSellPrice[0]["pricePerUnit"]


# takes in already valid item names, check ah for lowest bin
# assume all items in itemLst properly capitalized
def lowestBin(itemLst):
  start = time.time()
  pg = 0
  print("auction item list", itemLst)
  tierDict = checkTiers(itemLst)
  print("valid tiers", tierDict)
  while True:
    data = asyncio.run(
      globals.req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      #print("test", pg)
      for auction in data["auctions"]:
        aucName = auction["item_name"]
        if auction["bin"] == True:
          aucTier = auction["tier"]
          if tierDict[aucTier] == True:
            for i in itemLst:
              if (i in aucName or i == aucName):
                #print(aucName, f"on pg {pg}")
                if itemLst[i] == -1 or auction["starting_bid"] < itemLst[i]:
                  itemLst[i] = auction["starting_bid"]
                break
      pg += 1
  print("itemLst", itemLst)
  end = time.time()
  print(f"lowestBin process time {end - start} seconds")
  return itemLst


# trying out a lowest bin for bits
# assume all items in dict are valid and properly spelled
def bitsLowestBin(itmDict):
  start = time.time()
  tierDict = checkTiers(itmDict)
  catDict = {
    "weapon": False,
    "armor": False,
    "accessories": True,
    "consumables": True,
    "blocks": True,
    "tools": True,
    "misc": True
  }
  pg = 0
  print("auction item list", itmDict)
  while True:
    data = asyncio.run(
      globals.req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      #print("test", pg)
      for auction in data["auctions"]:
        if auction["bin"] == True:
          aucItm = auction["item_name"]
          itmCat = auction["category"]
          itmTier = auction["tier"]
          if tierDict[itmTier] == True and catDict[itmCat] == True:
            try:
              aucItm = auction["item_name"]
              itmVal = itmDict[aucItm]
              aucItm
              #print(auction["item_name"], f"on pg {pg}")
              aucPrice = auction["starting_bid"]
              if itmVal == -1 or aucPrice < itmVal:
                itmDict[aucItm] = aucPrice
            except:
              pass
    pg += 1
  print("itemLst", itmDict)
  end = time.time()
  print(f"bitsLowestBin process time {end - start} seconds")
  return itmDict
