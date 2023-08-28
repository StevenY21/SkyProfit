import discord
from discord import app_commands
from discord.app_commands import Choice
import discord.ext
import functions
import re, json, requests
import os
from keep_alive import keep_alive
#if I need to update anything
import globals
import time
import aiohttp
import asyncio

TOKEN = os.environ['TOKEN']
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

ITEMS_JSON = asyncio.run(
  functions.req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/constants/items.json'
  ))
SB_ITEM_DATA = ITEMS_JSON["item_data"]
SB_PROPER_NAMES = ITEMS_JSON["fix_item_name"]
SB_NAME_ID = ITEMS_JSON["name_to_id"]
SB_BITS_SHOP = asyncio.run(
  functions.req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/constants/bits_shop.json'
  ))
SB_SKYMART = asyncio.run(
  functions.req_data(
    'https://raw.githubusercontent.com/StevenY21/SkyProfit/main/src/constants/copper_shop.json'
  ))


# inv bot: https://discord.com/api/oauth2/authorize?client_id=1117918806224932915&permissions=448824396865&scope=bot
@tree.command(name="help", description="Help for SkyProfit commands")
async def getHelp(interaction: discord.Interaction, name: str):
  await interaction.response.send_message("Need help for commands? :thinking:")
  res = discord.Embed(title="  ", colour=0x1978E3)
  res.title = "SkyProfit Commands"
  res.description += "- craftprofit [item name]" + "\n" + " - gets regular item recipe, raw material recipe, and 2 alt recipes(if applicable)" + "\n" + " - finds cost to craft item with each recipe, and also returns the profit percentage if you sell item." + "\n" + " - NOTE: ONLY for items that can be made with regular crafting table, and are salable in bazaar or auction house. Currently doesn't work for pets, enchantments, potions, and some random items. Please report to me any items that don't work."

  await interaction.edit_original_response(embed=res)


@tree.command(name="test", description="testin comamnd")
async def testChoice(interaction: discord.Interaction, chc: str):
  await interaction.response.send_message(f"You chose {chc}")


@testChoice.autocomplete("chc")
async def testChoice_autocomp(interaction: discord.Interaction, current: str):
  data = []
  for itemChoice in SB_ITEM_DATA:
    if current.lower() in itemChoice.lower():
      data.append(app_commands.Choice(name=itemChoice, value=itemChoice))
  return data[:5]


@tree.command(
  name="craftprofit",
  description=" Gets many possible recipes for item, provides profit % for each"
)
async def craftprofit(interaction: discord.Interaction, name: str):
  testStart = time.time()
  try:
    name = SB_PROPER_NAMES[name.lower()]
    await interaction.response.send_message("Getting Regular Recipe...")
    regRecipe = await asyncio.to_thread(functions.get_item_recipe, name)
    print(regRecipe, "is reg recipe")
    itemID = SB_NAME_ID[name]
    if SB_ITEM_DATA[itemID]['vanilla'] and SB_ITEM_DATA[itemID]['in_ah']:
      await interaction.edit_original_response(
        content="Do not flip vanilla items (well most of them)")
    elif SB_ITEM_DATA[itemID]['soulbound'] != 'N/A':
      await interaction.edit_original_response(
        content=f"Error: {name} is soulbound and cannot be sold")
    elif regRecipe == None or regRecipe == -1:
      await interaction.edit_original_response(
        content=
        f"Error: {name} not found. Check if the item has a recipe, and that it can be sold on Auction House or Bazaar. REMEMBER: Pets and Enchantment Books are currently not applicable"
      )
    elif regRecipe == -2:
      await interaction.edit_original_response(
        content=f"Error: {name} does not have valid recipe or any recipe at all"
      )
    else:
      res = discord.Embed(title="  ", colour=0x1978E3)
      await interaction.edit_original_response(
        content="Getting Regular Recipe... \nGetting Alt Recipes...")
      recipeLst = await asyncio.to_thread(functions.get_raw_recipe, regRecipe)
      if len(recipeLst) == 0:  # when regular and raw recipe the same
        recipeLst += [regRecipe]
      elif len(recipeLst) > 3:  # when there are too many recipes
        tempRecLst = []
        tempRecLst += [recipeLst[0]]
        tempRecLst += [recipeLst[-2]]
        tempRecLst += [recipeLst[-1]]
        recipeLst = tempRecLst
      #rawRecipe = recipeLst[-1]
      #print(rawRecipe, "is raw recipe")

      # process the cost of the materials into proper sentences
      def processCosts(mat_prices, curr_recipe):
        start = time.time()
        #print(mat_prices, "process_cost debug mat prices")
        totalCost = 0
        for material in mat_prices:
          #print(f"current {material} in loop")
          #print(f"curr recipe: {curr_recipe}")
          res.description += f"\n> {curr_recipe[material]} {material}:"
          #print(mat_prices)
          if mat_prices[material] < 0:
            if mat_prices[material] == -1 or mat_prices[material] == -2:
              res.description += " No one is selling it."
              totalCost = -1
            elif mat_prices[material] == -3:
              res.description += " Soulbound"
              mat_prices[material] = 0
          else:
            mat_prices[material] = round(mat_prices[material])
            res.description += f" {mat_prices[material]} coins."
          #print(curr_recipe[material], material, mat_prices[material])
          if totalCost != -1:
            totalCost += mat_prices[material]
        if totalCost != -1:
          res.description += f"\n`Total Cost: {totalCost} coins.`"
        else:
          res.description += "\n`Total Cost: Incomplete.`"
        end = time.time()
        print(f"processCosts time {end - start} seconds")
        return (totalCost)

      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices..."
      )
      # getting the prices for the amts of materials
      #recipeCosts.append(await asyncio.to_thread(getCosts, None, regRecipe))
      #recipeCosts.append(getCosts(None, regRecipe))
      #prevPrice = recipeCosts[0]
      costStrt = time.time()
      fullLst = [regRecipe] + recipeLst
      recipeCosts = []
      prevRecipe = None
      prevPrice = None
      currRecipe = fullLst[0]
      numRecs = len(fullLst)
      i = 0
      while True:
        material_price = {}
        if prevRecipe != None:
          for material in currRecipe:
            print(f"curr processed: {material}")
            try:
              if prevRecipe[material] == currRecipe[material]:
                material_price[material] = prevPrice[material]
              else:
                if prevPrice[material] < 0:
                  material_price[material] = prevPrice[material]
                else:
                  material_price[material] = (
                    prevPrice[material] /
                    prevRecipe[material]) * currRecipe[material]
            except:
              matID = SB_NAME_ID[material]
              matCost = await asyncio.to_thread(functions.findCost, matID)
              if matCost < 0:
                material_price[material] = matCost
              else:
                material_price[material] = matCost * currRecipe[material]
        else:
          for material in currRecipe:
            matID = SB_NAME_ID[material]
            matCost = await asyncio.to_thread(functions.findCost, matID)
            if matCost < 0:
              material_price[material] = matCost
            else:
              material_price[material] = matCost * currRecipe[material]
        recipeCosts.append(material_price)
        print(f"mat price for curr recipe: {material_price}")
        i += 1
        if i == numRecs:
          break
        else:
          prevRecipe = currRecipe
          currRecipe = fullLst[i]
          prevPrice = recipeCosts[-1]
      costEnd = time.time()
      print(f"getCosts time {costEnd - costStrt} seconds")
      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices... \nGetting Alt Recipe Prices... \nNote that if any items are from the auction house, it will take a little longer :slight_smile:"
      )
      ahItems = {}
      # for efficiency, all items in both raw and regular recipe will be processed together
      mainItemPrice = round(await asyncio.to_thread(functions.findCost,
                                                    SB_NAME_ID[name]))
      if mainItemPrice == -1:  # if in auction house
        ahItems[name] = -1
      j = 0
      costsLen = len(recipeCosts)
      prevPrice = recipeCosts[0]
      while True:
        if j == costsLen:
          break
        else:
          for mat in recipeCosts[j]:
            if recipeCosts[j][mat] == -1:
              ahItems[mat] = -1
          j += 1
      # places the auction house item costs into the recip cost dict
      if len(ahItems) > 0:
        ah_data = requests.get("https://moulberry.codes/lowestbin.json").json()
        #ahItems = await asyncio.to_thread(functions.lowestBin, ahItems)
        for item in ahItems:
          itemID = SB_NAME_ID[item]
          try:
            ahItems[item] = ah_data[itemID]
          except:
            ahItems[item] = -1
        count = 0
        for i in (ahItems):
          for j in range(len(recipeCosts)):
            if i in recipeCosts[j]:
              if count == 0:
                if ahItems[i] == -1:
                  recipeCosts[j][i] = -1
                else:
                  recipeCosts[j][i] = regRecipe[i] * ahItems[i]
              elif count > 0:
                if ahItems[i] == -1:
                  recipeCosts[j][i] = -1
                else:
                  recipeCosts[j][i] = recipeLst[count - 1][i] * ahItems[i]
              if count == len(recipeCosts) - 1:
                count = 0
              else:
                count += 1
            else:
              count += 1
          count = 0
        if name in ahItems:
          mainItemPrice = ahItems[name]

      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices... \nGetting Alt Recipes' Prices... \nGetting Readable Results. Note that the price for bazaar items are based off the highest buy order price, and the price for auction house items are based off of the lowest BIN. Additionally, an item's value is based off its clean version, e.g non-recombombulated."
      )
      res.title = f"{name}'s recipes:"
      # find total cost for each recipe
      recipeTotals = []
      i = 0
      while True:
        if i == 0:
          res.description = "__**Regular Recipe:**__"
          recipeTotals += [
            await asyncio.to_thread(processCosts, recipeCosts[0], regRecipe)
          ]
        else:
          if len(recipeCosts) == 1 or i == len(recipeCosts) - 1:
            res.description += "\n\n__**Raw Recipe:**__"
            recipeTotals += [
              await asyncio.to_thread(processCosts, recipeCosts[-1],
                                      recipeLst[-1])
            ]
            break
          else:
            res.description += f"\n\n__**Alt Recipe {i}:**__"
            if i == 1:
              recipeTotals += [
                await asyncio.to_thread(processCosts, recipeCosts[1],
                                        recipeLst[(0)])
              ]
            elif i == 2:
              recipeTotals += [
                await asyncio.to_thread(processCosts, recipeCosts[2],
                                        recipeLst[(1)])
              ]
        i += 1
      # processes the profit percentages
      res.description += "\n\n__**Profit Margin**__"
      res.description += f"\n> {name}'s price:"
      if mainItemPrice == -1:  # if no one's selling
        res.description += " No one is selling it."
        res.description += "\nPut a price you like :slight_smile:."
        mainItemPrice = 0
      else:
        res.description += f" {mainItemPrice} coins."
        recProfits = {}
        i = 0
        print("check point creating profit % ")
        while True:
          profit = 0
          profitPercent = 0
          if i == len(recipeCosts):
            break
          else:
            if recipeTotals[i] == -1:
              profit = 'N/A'
              profitPercent = 'N/A'
            else:
              profit = (mainItemPrice - recipeTotals[i])
              profitPercent = (round(((profit / recipeTotals[i]) * 100), 2))
            if i == 0:
              res.description += f"\n> Regular Recipe Proft (%): {profit} coins ({profitPercent}%)."
              recProfits["Regular Recipe"] = profitPercent
            elif i == len(recipeCosts) - 1:
              res.description += f"\n> Raw Recipe Proft (%): {profit} coins ({profitPercent}%)."
              recProfits["Raw Recipe"] = profitPercent
            else:
              res.description += f"\n> Alt Recipe {i} Proft (%): {profit} coins ({profitPercent}%)."
              recProfits[f"Alt Recipe {i}"] = profitPercent
          i += 1
        bestProfitRec = ""
        bestProfit = 'N/A'
        # processes the biggest profit percentage
        for rec in recProfits:
          if recProfits[rec] != 'N/A':
            if bestProfit == 'N/A' or recProfits[rec] > bestProfit:
              bestProfit = recProfits[rec]
              bestProfitRec = rec
        res.description += f"\n`Craft it using {bestProfitRec}`"
      print("reached here not bad")
      testEnd = time.time()
      res.set_footer(
        text="Recipe Data By: NotEnoughUpdates" +
        f"\nProcess Time: {round((testEnd-testStart), 2)} seconds")
      await interaction.edit_original_response(embed=res)
  except:
    await interaction.response.send_message(
      f"Error: {name} not found. Check if the item name is spelled correctly. Note that the input is not case-sensitive."
    )


@tree.command(
  name="cookieprofit",
  description="provides a sorted list showing bit shop item profits")
@app_commands.choices(
  filter=[Choice(name=i, value=i) for i in SB_BITS_SHOP['filter']])
@app_commands.choices(
  famerank=[Choice(name=i, value=i) for i in SB_BITS_SHOP['fame_rank']])
async def cookieprofit(interaction: discord.Interaction, famerank: str,
                       filter: str):
  start = time.time()
  cookieBits = 4800 * SB_BITS_SHOP['fame_rank'][famerank]
  cookieCost = await asyncio.to_thread(functions.findCost, "BOOSTER_COOKIE")
  cookieCPB = round(cookieCost / cookieBits, 2)
  filter = SB_BITS_SHOP['filter'][filter]
  shopLst = SB_BITS_SHOP[filter]
  await interaction.response.send_message(
    "Processing filtered Bits Shop items...")
  costDict = {}
  ahLst = {}
  cost = 0
  temp = ""
  for item in shopLst:
    if "Abicase" not in item:
      temp = item
      if temp == "1 Inferno Fuel Block" or item == "64 Inferno Fuel Blocks":
        item = "Inferno Fuel Block"
      itemID = SB_NAME_ID[item]
      if SB_ITEM_DATA[itemID]['in_bz'] == True:
        cost = await asyncio.to_thread(functions.findCost, itemID)
      else:
        cost = -1
    print(f"{itemID}: {cost}")
    if cost == -1:
      ahLst[item] = -1
      costDict[item] = -1
    else:
      if temp == "64 Inferno Fuel Blocks":
        costDict[temp] = cost * 64
      else:
        costDict[temp] = cost
  await interaction.edit_original_response(
    content=
    "Processing filtered Bits Shop items... \nChecking auction house for items..."
  )
  ah_data = requests.get("https://moulberry.codes/lowestbin.json").json()
  #ahDict = await asyncio.to_thread(functions.bitsLowestBin, ahLst)
  for item in ahLst:
    itemID = SB_NAME_ID[item]
    try:
      costDict[item] = ah_data[itemID]
    except:
      costDict[item] = -1
  await interaction.edit_original_response(
    content=
    "Processing filtered Bits Shop items... \nChecking auction house for items... \nFinalizing Results"
  )
  embTitle = ""
  if filter == "no_filter":
    embTitle = "Bits Shop Item Profits:"
  else:
    embTitle = f"Bits Shop Item Profits with {filter}:"
  profitDict = {}
  for item in costDict:
    if costDict[item] == -1:
      profitDict[item] = 0
    else:
      profitDict[item] = costDict[item] / shopLst[item]
  #print(profitDict)
  sortedItms = dict(
    sorted(profitDict.items(), key=lambda x: x[1], reverse=True))
  i = 0
  j = 0
  embList = []
  embed = discord.Embed(title=embTitle, colour=0x1978E3)
  for item in sortedItms:
    itmBits = shopLst[item]
    if i == 12:
      embList.append(embed)
      embed = discord.Embed(title=embTitle, colour=0x1978E3)
      i = 0
    else:
      if costDict[item] == -1:
        sellPrice = "No one is selling"
        embed.add_field(
          name=f"{j+1}. {item}",
          value=
          f"\nBit Cost: {itmBits} bits\nSell Price: {sellPrice} coins\nEstimated Value: {round(shopLst[item] * cookieCPB)}",
          inline=True)
      else:
        itmBits = shopLst[item]
        cPB = round(profitDict[item], 2)  # coins Per Bit
        profit = round((cPB - cookieCPB) * itmBits)
        cost = cookieCPB * itmBits
        profitPercent = round(((profit / cost) * 100), 2)
        embed.add_field(
          name=f"{j+1}. {item}",
          value=
          f"\nBit Cost: {itmBits} bits\nSell Price: {costDict[item]} coins\nCoins Per Bit: {cPB}\nProfit (%): {profit} coins ({profitPercent}%)",
          inline=True)
      i += 1
      j += 1
  if i > 0:
    embList.append(embed)
  numEmbeds = len(embList)
  #print(numEmbeds)
  pg = 0

  class MyView(discord.ui.View):

    def __init__(self, timeout):
      super().__init__(timeout=timeout)
      self.response = None

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def prev_callback(self, interaction: discord.Interaction, button):
      nonlocal pg
      pg -= 1
      await interaction.response.edit_message(embed=embList[pg % numEmbeds])

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next_callback(self, interaction: discord.Interaction, button):
      nonlocal pg
      pg += 1
      await interaction.response.edit_message(embed=embList[pg % numEmbeds])

    async def on_timeout(self):
      self.clear_items()
      await self.response.edit(view=self)

  end = time.time()
  #res.set_footer(text=f"Process Time: {round((end-start),2)} seconds")
  procTime = round((end - start), 2)
  await interaction.edit_original_response(
    content=
    "Processing filtered Bits Shop items... \nChecking auction house for items... \nFinalizing Results \nNote that the table will timeout 60 seconds after last interaction"
  )
  for i in embList:
    i.set_footer(text=f"Process Time: {procTime} seconds")
  my_view = MyView(timeout=60)
  await interaction.edit_original_response(embed=embList[0], view=my_view)
  out = await interaction.edit_original_response(embed=embList[0],
                                                 view=my_view)
  my_view.response = out


@tree.command(name="copperprofit",
              description="provides a sorted list showing SkyMart item profits"
              )
async def copperprofit(interaction: discord.Interaction):
  start = time.time()
  skymartLst = SB_SKYMART['copper_shop']
  profitDict = {}  # key: item name, value: coins per copper
  itemProfitData = {}  # {copper: ,sellPrice: , cPC (coinsPerCopper): }
  ahLst = {}
  await interaction.response.send_message("Checking Bazaar for items...")
  for item in skymartLst:
    itemID = SB_NAME_ID[item]
    sellPrice = await asyncio.to_thread(functions.findCost, itemID)
    cpc = 0  # coins per copper
    if sellPrice <= -1:
      ahLst[item] = -1
    else:
      cpc = round(sellPrice / skymartLst[item], 2)
    profitDict[item] = cpc
    itemProfitData[item] = {
      "copper": skymartLst[item],
      "sell_price": sellPrice,
      "cpc": cpc
    }
  await interaction.edit_original_response(
    content=
    "Processing filtered Bits Shop items... \nChecking auction house for items..."
  )
  ah_data = requests.get("https://moulberry.codes/lowestbin.json").json()
  #ahLst = await asyncio.to_thread(functions.lowestBin, ahLst)
  for item in ahLst:
    itemID = SB_NAME_ID[item]
    try:
      itemProfitData[item]["sell_price"] = ah_data[itemID]
      profitDict[item] = round(
        itemProfitData[item]["sell_price"] / skymartLst[item], 2)
      itemProfitData[item]["cpc"] = profitDict[item]
    except:
      profitDict[item] = -1
      itemProfitData[item]["sell_price"] = -1
      itemProfitData[item]["cpc"] = 0
  sortedItms = dict(
    sorted(profitDict.items(), key=lambda x: x[1], reverse=True))
  await interaction.edit_original_response(
    content=
    "Processing filtered Bits Shop items... \nChecking auction house for items... \nFinalizing Results"
  )
  embed = discord.Embed(
    title="SkyMart Item Profits",
    description=
    "Sell Price and Coins per Copper based off the lowest bin or highest buy order for item",
    colour=0x1978E3)
  i = 1
  for item in sortedItms:
    copperCost = itemProfitData[item]["copper"]
    sellPrice = itemProfitData[item]["sell_price"]
    finalCPC = itemProfitData[item]["cpc"]
    if sellPrice == -1:
      embed.add_field(
        name=f"{i}. {item}",
        value=f"Copper: {copperCost} copper\nSell Price: No one is selling it")
    else:
      embed.add_field(
        name=f"{i}. {item}",
        value=
        f"Copper: {copperCost} copper\nSell Price: {sellPrice} coins\n Coins Per Copper: {finalCPC} "
      )
    i += 1
  end = time.time()
  embed.set_footer(text=f"Process Time: {round((end-start), 2)} seconds")
  await interaction.edit_original_response(embed=embed)


@client.event
async def on_ready():
  await tree.sync()
  print('ITS ALIVE!!')


keep_alive()
client.run(TOKEN)
