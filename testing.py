# all the random test code and old code that I still want to keep around just in case
import re, json, requests
import nbt
import io
import base64
import globals
import math
import aiohttp
import asyncio


# for decoding auction house most recent ending bids

def decode_inventory_data(raw_data):
  data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(raw_data)))
  print(data)
  decode_inventory_data("H4sIAAAAAAAAAGWRzU7CUBCFp4Ba6kJ3RhfahRoJIdoWwbJDQCDhR21Ym2k7LTe0BdvbRJ+I9+DBjBdbI4mbe5M530zOmVEAyiAxBQCkAhSYK91JsNdZphGXFChy9CU4nEV2TLhAOyCpCOUBc+kpQD8RTV8KHLgsWQX4WYbSaBmTLKoKnG3WTYvHFPl83lI3a6dqiNe8qRoVuBBaJ2Zc7cwxciiT61eZXr/aAboYop8DRg4YArgWwOMyShO1zTk6C9VaEbkZp+WcJrhTwQ0Ig8wDVo0/E1uDXfIoSuifdrI1/zsRq1o+sALnQhhGnIKA+ZRbx51ksG3FzTqYTTrT8Xg6UUe9fn846VsylCYY0o/+nMakWu8pE9+IfJ9FYpUKHPU+eIwiUMzslFMigxwuXeYxiqG0SrebFfeBI+tlNnztve1MTlNRv9RMr2nqDbN2rzfNWt2582qma+s1ajS8uufaruk8yFDmLKSEY7iC4+atbt7qhqrpLb2htscABdjPdi6iwDcM0I/3HAIAAA=="
)


# old functions that are kinda pointless
# kept just in case
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
"""

#jamin testing embeds
"""
@tree.command(name="testing_embed")
async def test(interaction: discord.Interaction):
  grid = ""
  count = 0
  for row in range(3):
    for col in range(3):
      count += 1
      grid += str(
        'https://wiki.hypixel.net/images/4/4d/SkyBlock_items_mine_talisman.png'
      )
    grid += "\n"
  globals.finalOutput.description = grid
  await interaction.response.send_message(embed=globals.finalOutput)
"""

# gets the cost of each amt of materials in the current recipe
# originally used in my craftprofit, but found to be kinda pointless after finding better way to process material costs
"""
      def getCosts(prevRecipe, currRecipe):
        print(f"checking {currRecipe} with {prevRecipe}")
        material_price = {}
        for material in currRecipe:
          #print(f"curr processed: {material}")
          if prevRecipe != None:
            if material in prevRecipe:
              if prevRecipe[material] == currRecipe[material]:
                material_price[material] = prevPrice[material]
              else:
                if prevPrice[material] < 0:
                  material_price[material] = prevPrice[material]
                else:
                  material_price[material] = (
                    prevPrice[material] /
                    prevRecipe[material]) * currRecipe[material]
            else:
              matID = sbItemNames[material]
              matCost = functions.findCost(matID)
              if matCost < 0:
                material_price[material] = matCost
              else:
                material_price[material] = functions.findCost(
                  matID) * currRecipe[material]
          else:
            matID = sbItemNames[material]
            matCost = functions.findCost(matID)
            if matCost < 0:
              material_price[material] = matCost
            else:
              material_price[material] = functions.findCost(
                matID) * currRecipe[material]
        print(f"mat price for curr recipe: {material_price}")
        return material_price
"""
# additional code for usin get getCosts that isnt useful anymore
"""
      if len(recipeLst) == 1:
        #print("test for only raw rec")
        recipeCosts.append(await asyncio.to_thread(getCosts, regRecipe,
                                                   rawRecipe))
        #recipeCosts.append(getCosts(regRecipe, rawRecipe))
      else:
        #print("test for 1 alt and one raw")
        recipeCosts.append(await asyncio.to_thread(getCosts, regRecipe,
                                                   recipeLst[0]))
        #recipeCosts.append(getCosts(regRecipe, recipeLst[0]))
        prevPrice = recipeCosts[1]
        if len(recipeLst) == 2:
          #print("test for 1 alt and 1 raw for raw part")
          recipeCosts.append(await asyncio.to_thread(getCosts, recipeLst[0],
                                                     rawRecipe))
          #recipeCosts.append(getCosts(recipeLst[0], rawRecipe))
        if len(recipeLst) == 3:
          #print("test for 2 alts and one raw")
          recipeCosts.append(await asyncio.to_thread(getCosts, recipeLst[0],
                                                     recipeLst[-2]))
          #recipeCosts.append(getCosts(recipeLst[0], recipeLst[-2]))
          prevPrice = recipeCosts[2]
          recipeCosts.append(await asyncio.to_thread(getCosts, recipeLst[-2],
                                                     rawRecipe))
      """

# find a way to get all craftable items that can be sold on ah and bz
"""
for itemName in SB_ITEMS_DICT:
  if SB_NONCRAFTABLES_DICT[itemName] == False and "glass" not in itemName and "leaves" not in itemName and "dye" not in itemName and itemName not in SB_MINIONS_LIST and SB_SOULBOUND_DICT[itemName] == False:
    itemID = SB_ITEMS_DICT[itemName]
    itemMat = SB_MAT_DICT[itemID]
    if itemID != itemMat:
      try:
        test = asyncio.run(req_data( f'https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master/items/{itemID}.json'))["recipe"]
        print(f"checking if item {i}, {itemName} has rec")
        try:
          test2 = test[0]["type"]
          if test2 == "forge":
            SB_FORGE_ITEMS_DATA[itemID] = test[0]
        except:
          SB_CRAFTPROFIT_DATA[itemID] = test
      except:
        SB_NONCRAFTABLES_DICT[itemName] = True
  i += 1
print(f"{i} end")
"""