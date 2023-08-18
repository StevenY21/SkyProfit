import re, json, requests
import globals
import math
import asyncio
import aiohttp
import time

# key: item names, value: item id
# due to the fact that some items have same names, the more useless ones got excluded, like decors, cosmetics, and furniture
sbItemDict = globals.SB_NAME_DICT


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
SB_ITEM_DATA = asyncio.run(
  req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/constants/items.json'
  ))


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
    itemID = sbItemDict[item]
    itmTier = SB_ITEM_DATA[itemID]['tier']
    itmCat = SB_ITEM_DATA[itemID]['ah_category']
    if itmCat == 'tools and misc':
      tierCats[itmTier]['tools'] += [item]
      tierCats[itmTier]["misc"] += [item]
    elif itmCat == 'blocks and tools and misc':
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
  propLst = []  # all recipes that will be returned
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
      except:
        temp = get_item_recipe(material)
      if temp == -1 or temp == -2:
        if material not in rawRecipe:
          rawRecipe[material] = tempRec[material]
        else:
          rawRecipe[material] += tempRec[material]
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
  itemName = SB_ITEM_DATA[itemID]['name']
  SB_ITEM_DATA[itemID]["in_bz"]
  if SB_ITEM_DATA[itemID]["in_bz"] == False:
    if SB_ITEM_DATA[itemID]["soulbound"] != 'N/A':  # if it is soulboumd
      return -3
    elif itemName in NPC_ITEMS:  # if it is sold by npc
      return NPC_ITEMS[itemName]
    elif SB_ITEM_DATA[itemID]['vanilla'] and SB_ITEM_DATA[itemID][
        'in_ah']:  # for vanilla items found in auction
      # for vanilla items with no recipe
      # so far only applied to vines
      if itemName == "Vines":
        return 0
      # for vanilla items with recipe
      else:
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


# takes in already valid item names, check ah for lowest bin
# assume all items in itemLst properly capitalized
def lowestBin(itemLst):
  start = time.time()
  pg = 0
  print("auction item list", itemLst)
  tierCats = checkTierCats(itemLst)
  while True:
    data = asyncio.run(
      req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      print("test", pg)
      for auction in data["auctions"]:
        aucName = auction["item_name"]
        if auction["bin"] == True:
          aucTier = auction["tier"]
          aucCat = auction['category']
          tierCat = tierCats[aucTier][aucCat]
          if tierCat != []:
            if aucTier == 'SPECIAL' or aucTier == 'VERY_SPECIAL':
              for i in tierCat:
                if i == aucName:
                  print(aucName, f"on pg {pg}")
                  if itemLst[i] == -1 or auction["starting_bid"] < itemLst[i]:
                    print(f"new lowest price for{i} found")
                    itemLst[i] = auction["starting_bid"]
                  break
            else:
              for i in tierCat:
                if i in aucName:
                  print(aucName, f"on pg {pg}")
                  if itemLst[i] == -1 or auction["starting_bid"] < itemLst[i]:
                    print(f"new lowest price for {i} found")
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
  tierDict = {
    'SUPREME': False,
    'RARE': True,
    'MYTHIC': False,
    'LEGENDARY': True,
    'EPIC': True,
    'UNCOMMON': False,
    'UNTIERED': False,
    'COMMON': False,
    'VERY_SPECIAL': False,
    'SPECIAL': True,
    'UNOBTAINABLE': False
  }
  ahCats = {
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
      req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
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
          if tierDict[itmTier] == True and ahCats[itmCat] == True:
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
