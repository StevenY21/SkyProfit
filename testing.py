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
"""
def decode_inventory_data(raw_data):
  data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(raw_data)))
  print(data)
  decode_inventory_data("H4sIAAAAAAAAAD2Q3W7TQBCFx0lDExcUwRMMiNvQ1g5J6V0Uwk/VpFwQ4A6N12N7lfVu8K5J80R+jzwYYm0h7lY753xn5oQAIwhkCABBD3oyDcYBDJam1i4Ioe8oH8EZa1H8U/TVbwWDTgkIAVxsdVIx7ShRHPRh9Emm/EFRbr38TwjnqbR7RUcPuTcVD/3vBYxPzbtVlkkhPfiI3+DVqZl/1sJzLFsszAF/1VLs1BGPpq7QGaPgudd0SRYTZcTOvvGs1rjAvTlwldUKvxuTssbFI+OhkKJAQbrTdEYsa+XkXjEqk1uUGgmt1LliOPeaQrqX8OLU3Cx9XGoO+hZPDUXtIf4x94OvhfQ2x2XLxYSx4sxUOaedj06N2m6WD+v1wwYXP1ZDONtQyfDMj+7qNqZdDEIYrx5dRQvnKpnUju2wKzO8224+3q9+emcIT9vGSbuStbN9CPl/W36bAXh0XXvP6+gqeZuxuJpMUyEm0yijCc1oPqEkFhFdxzccx0MYOVmydVTuYTy7vI4voxhnt9MIv6wBevDkPZWUsyfDX/ZF5iEOAgAA"
)
"""

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