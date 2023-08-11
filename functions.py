import re, json, requests
import nbt
import io
import base64
import globals
import math
import aiohttp
import asyncio
import testing
import msgspec

skyblockItems = globals.SB_ITEMS_DATA
sbItemDict = globals.SB_ITEMS_DICT
sbIDDict = globals.SB_ID_DICT
sbAHDict = globals.SB_AH_DICT
sbBzDict = globals.SB_BZ_DICT
sbSBDict = globals.SB_SOULBOUND_DICT

BASE_ITEMS = globals.BASE_ITEMS_DICT
# items that have recipe that isn't accurate in repo
ITEM_FACTOR = {"Blaze Powder": 0.5, "Sulphuric Coal": 0.25}
NPC_ITEMS = {"Glass Bottle": 6, "Stick": 0}
# these items can't be bought on bazaar, but are made of items from bz
EXCLUDED_ITEMS = globals.EXCLUDED_ITEMS_DICT


#get item name to item recipe
# assume item name is fixed to proper form
def get_item_recipe(itemName):
  print(f"item being checked {itemName}")
  try:
    if BASE_ITEMS[itemName] == True:
      return -2
    #get the id from the name

    itemId = sbItemDict[itemName]
    if itemId == -1:
      return -1
    newItemId = ''
    if ':' in itemId:
      for j in itemId:
        if j == ':':
          newItemId += '-'
        else:
          newItemId += j
    else:
      newItemId = itemId
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
  tempRec = recipe
  recipelst = []
  rawRecipe = {}
  temp = None
  recSize = len(recipe)
  numDone = 0  # number of items in recipe that have reached its most basic component
  #print(recipe, "recipe to be processed into raw form")
  while True:
    for material in tempRec:
      #print(material, "curr material to process in get_raw_recipe")
      if len(tempRec) == 1:
        if material in BASE_ITEMS and material not in rawRecipe:
          rawRecipe[material] = tempRec[material]
          numDone += 1
          break
      #print(f"getting recipe for {material}")
      temp = get_item_recipe(material)
      #print(material, temp, f"raw rec for {material}")
      #print(temp)
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
    if numDone == recSize:
      break
    else:
      #print(f"raw recipe so far {rawRecipe}")
      recipelst.append(rawRecipe)
      tempRec = rawRecipe
      recSize = len(rawRecipe)
      rawRecipe = {}
      numDone = 0
  return recipelst


# gets items bazaar cost
# can assume id is valid
def findCost(itemID):
  #print(f"item id being checked: {item_ID}")
  itemName = sbIDDict[itemID]
  if sbSBDict[itemName] == True:  # if it is soulboumd
    return -3
  elif itemName in NPC_ITEMS:  # if it is sold by npc
    return NPC_ITEMS[itemName]
  elif EXCLUDED_ITEMS[
      itemName] == True:  # for items that have to be crafted anyways
    return -4
  else:
    try:
      itemSellPrice = asyncio.run(
        globals.req_data("https://api.hypixel.net/skyblock/bazaar")
      )["products"][itemID]['sell_summary']
      if itemSellPrice == []:  # if no one is selling it bazaar
        return -2
      else:
        return itemSellPrice[0]["pricePerUnit"]
    except:  # if it does not exist on bazaar
      return -1


# takes in already valid item names, check ah for lowest bin
# assume all items in itemLst properly capitalized
def lowestBin(itemLst):
  pg = 0
  print("auction item list", itemLst)
  while True:
    data = asyncio.run(
      globals.req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      print("test", pg)
      for auction in data["auctions"]:
        aucName = auction["item_name"]
        if auction["bin"] == True:
          for i in itemLst:
            if (i in aucName or i == aucName):
              print(aucName, f"on pg {pg}")
              if itemLst[i] == -1 or auction["starting_bid"] < itemLst[i]:
                itemLst[i] = auction["starting_bid"]
              break
      pg += 1
  print("itemLst", itemLst)
  return itemLst


# trying out a lowest bin for bits
# assume all items in dict are valid and properly spelled
def bitsLowestBin(itmDict):
  pg = 0
  print("auction item list", itmDict)
  while True:
    data = asyncio.run(
      globals.req_data(f"https://api.hypixel.net/skyblock/auctions?page={pg}"))
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      print("test", pg)
      for auction in data["auctions"]:
        if auction["bin"] == True:
          try:
            test = itmDict[auction["item_name"]]
            print(auction["item_name"], f"on pg {pg}")
            aucItm = auction["item_name"]
            aucPrice = auction["starting_bid"]
            if itmDict[aucItm] == -1 or aucPrice < itmDict[aucItm]:
              itmDict[aucItm] = aucPrice
          except:
            pass
    pg += 1
  print("itemLst", itmDict)
  return itmDict
