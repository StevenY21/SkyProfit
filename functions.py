import re, json, requests
import nbt
import io
import base64
import globals
import math
import aiohttp
import asyncio

skyblockItems = globals.SB_ITEMS_DATA

# for decoding auction house most recent ending bids
#def decode_inventory_data(raw_data):
#data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(raw_data)))
#print(data)

BASE_ITEMS = [
  "lapis lazuli", "coal", "diamond", "redstone", "gold ingot", "iron ingot",
  "wheat", "cobblestone", "oak log", "birch log", "bone", "spruce log",
  "dark oak log", "jungle log", "emerald"
]
# items that have recipe that isn't accurate in repo
SPECIAL_ITEMS1 = {"blaze powder": 0.5}
# for items that have duplicate names
SPECIAL_ITEMS2 = {"hay bale": "HAY_BLOCK"}

#decode_inventory_data(
#"H4sIAAAAAAAAAD2Q3W7TQBCFx0lDExcUwRMMiNvQ1g5J6V0Uwk/VpFwQ4A6N12N7lfVu8K5J80R+jzwYYm0h7lY753xn5oQAIwhkCABBD3oyDcYBDJam1i4Ioe8oH8EZa1H8U/TVbwWDTgkIAVxsdVIx7ShRHPRh9Emm/EFRbr38TwjnqbR7RUcPuTcVD/3vBYxPzbtVlkkhPfiI3+DVqZl/1sJzLFsszAF/1VLs1BGPpq7QGaPgudd0SRYTZcTOvvGs1rjAvTlwldUKvxuTssbFI+OhkKJAQbrTdEYsa+XkXjEqk1uUGgmt1LliOPeaQrqX8OLU3Cx9XGoO+hZPDUXtIf4x94OvhfQ2x2XLxYSx4sxUOaedj06N2m6WD+v1wwYXP1ZDONtQyfDMj+7qNqZdDEIYrx5dRQvnKpnUju2wKzO8224+3q9+emcIT9vGSbuStbN9CPl/W36bAXh0XXvP6+gqeZuxuJpMUyEm0yijCc1oPqEkFhFdxzccx0MYOVmydVTuYTy7vI4voxhnt9MIv6wBevDkPZWUsyfDX/ZF5iEOAgAA"
#)
"""
#test function
def get_item(itemName):
  try:
    item_data = bz_data["products"]["itemName"]
    item_buyPrice = item_data["quick_status"]["sellPrice"]
    item_sellPrice = item_data["quick_status"]["sellPrice"]
  except:
    return "invalid item, please make try again"
  return item_data
"""


# gets an item's item_id
def get_item_id(itemName):
  try:
    if itemName.lower() in SPECIAL_ITEMS2:
      return SPECIAL_ITEMS2[itemName.lower()]
    skyblockItems
    items = skyblockItems["items"]

    for i in items:
      if i['name'].lower() == itemName.lower():
        itemID = i["id"]
        #print(f"item id of {itemName}: {itemID}")
        return itemID
  except:
    return -1


# turns itemId to itemName
def get_item_name(itemId):
  try:
    skyblockItems
    items = skyblockItems["items"]

    for i in items:
      if i['id'] == itemId:
        itemName = i["name"]
        return itemName
  except:
    return "invalid item ID, please try again"


#get item name to item recipe
def get_item_recipe(itemName):
  try:
    if itemName.lower() in BASE_ITEMS:
      return -2
    #get the id from the name

    itemId = get_item_id(itemName)
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
    itemData2 = requests.get(
      f'https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master/items/{newItemId}.json'
    ).json()
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

          itemName2 = get_item_name(fixedID)
        else:
          itemName2 = get_item_name(item[0])
        if properRecipe.get(itemName2) != None:
          properRecipe[itemName2] += int(item[1])
        else:
          properRecipe[itemName2] = int(item[1])
    try:
      factor = SPECIAL_ITEMS1[itemName.lower()]
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
        if material in BASE_ITEMS and rawRecipe.get(material) == None:
          rawRecipe[material] = tempRec[material]
          numDone += 1
          break
      #print(f"getting recipe for {material}")
      temp = get_item_recipe(material)
      #print(material, temp, f"raw rec for {material}")
      #print(temp)
      if temp == -1 or temp == -2:
        if rawRecipe.get(material) == None:
          rawRecipe[material] = tempRec[material]
        numDone += 1
      else:
        #print(temp)
        for mat in temp:
          #print(mat, f"in {temp}")
          if rawRecipe.get(mat) == None:
            rawRecipe[mat] = int(math.ceil(tempRec[material] * temp[mat]))
          else:
            rawRecipe[mat] += int(math.ceil(tempRec[material] * temp[mat]))
    if numDone == recSize:
      break
    else:
      print(f"raw recipe so far {rawRecipe}")
      recipelst.append(rawRecipe)
      tempRec = rawRecipe
      recSize = len(rawRecipe)
      rawRecipe = {}
      numDone = 0
  return recipelst


#test_item = "Enchanted Block of Coal"
#test_recipe = get_item_recipe(test_item)
#print(test_item, "recipe:", test_recipe)
#print("raw recipe:", get_raw_recipe(test_recipe))


# gets items bazaar cost
# can assume id is valid
# returns -1 if its an auction house item
def findCost(item_ID):
  bz_data = requests.get("https://api.hypixel.net/skyblock/bazaar").json()
  if bz_data["products"].get(item_ID) != None:
    item_data = bz_data["products"][item_ID]
    #item_buyPrice = item_data["quick_status"]["buyPrice"]
    item_sellPrice = item_data["quick_status"]["sellPrice"]
    #print(item_sellPrice)
    return item_sellPrice
  else:
    return -1


# takes in already valid item ids, check ah for lowest bin
def lowestBin(itemLst):

  pg = 0
  lowestBins = {}
  print("auction item list", itemLst)
  while True:
    data = requests.get(
      f"https://api.hypixel.net/skyblock/auctions?page={pg}").json()
    if data["success"] == False:
      print("test", pg, "last pg reached")
      break
    else:
      print("test", pg)
      for auction in data["auctions"]:
        for i in itemLst:
          if (i.lower() in auction["item_name"].lower() or i.lower()
              == auction["item_name"].lower()) and auction["bin"] == True:
            print(auction["item_name"], f"on pg {pg}")
            if lowestBins.get(
                i) == None or auction["starting_bid"] < lowestBins[i]:
              lowestBins[i] = auction["starting_bid"]
            break
      pg += 1
  print("itemLst", itemLst)
  print("lowestBins", lowestBins)
  for i in itemLst:
    if i not in lowestBins:
      lowestBins[i] = -1
  print(lowestBins)

  return lowestBins
