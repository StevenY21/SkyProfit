import discord
import re, json, requests
# for final output of commands
finalOutput = discord.Embed(title="  ", colour=0x1978E3)

# sb item data for command choices
SB_ITEMS_DATA = requests.get(
  "https://api.hypixel.net/resources/skyblock/items").json()
print(len(SB_ITEMS_DATA['items']), "items")

ALL_SB_ITEMS = [item["name"] for item in SB_ITEMS_DATA['items']]
print(len(ALL_SB_ITEMS), "items")
print(ALL_SB_ITEMS[0:25])
