import discord
from discord import app_commands
from discord.app_commands import Choice
import discord.ext
import functions
import functools
import re, json, requests
import os
from keep_alive import keep_alive
import globals
import time
import aiohttp
import asyncio

TOKEN = os.environ['TOKEN']
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

sbProperNames = globals.SB_NAME_FIX


# inv bot: https://discord.com/api/oauth2/authorize?client_id=1117918806224932915&permissions=448824396865&scope=bot
@tree.command(name="help", description="Help for SkyProfit commands")
async def getHelp(interaction: discord.Interaction, name: str):
  await interaction.response.send_message("Need help for commands? :thinking:")
  globals.finalOutput.title = "SkyProfit Commands"
  globals.finalOutput.description += "- craftprofit [item name]" + "\n" + " - gets regular item recipe, raw material recipe, and 2 alt recipes(if applicable)" + "\n" + " - finds cost to craft item with each recipe, and also returns the profit percentage if you sell item." + "\n" + " - NOTE: ONLY for items that can be made with regular crafting table. Currently doesn't work for pets, enchantments, potions, and some random items. Please report to me any items that don't work."

  await interaction.edit_original_response(embed=globals.finalOutput)


@tree.command(name="test", description="testin comamnd")
async def testChoice(interaction: discord.Interaction, chc: str):
  await interaction.response.send_message(f"You chose {chc}")


@testChoice.autocomplete("chc")
async def testChoice_autocomp(interaction: discord.Interaction, current: str):
  data = []
  for itemChoice in globals.SB_BITS_DICT:
    if current.lower() in itemChoice.lower():
      data.append(app_commands.Choice(name=itemChoice, value=itemChoice))
  return data[:5]


@tree.command(
  name="craftprofit",
  description=" Gets many possible recipes for item, provides profit % for each"
)
async def craftprofit(interaction: discord.Interaction, name: str):
  start = time.time()
  try:
    name = sbProperNames[name.lower()]
    await interaction.response.send_message("Getting Regular Recipe...")
    regRecipe = await asyncio.to_thread(functions.get_item_recipe, name)
    print(regRecipe, "is reg recipe")
    if regRecipe == None or regRecipe == -1:
      await interaction.edit_original_response(
        content=
        f"Error: {name} not found. Check if the item name is spelled correctly, or that it can be sold on Auction House or Bazaar. REMEMBER: Pets and Enchantment Books are currently not applicable"
      )
    elif regRecipe == -2:
      await interaction.edit_original_response(
        content="Error: Does not have valid recipe or any recipe at all")
    else:
      await interaction.edit_original_response(
        content="Getting Regular Recipe... \nGetting Alt Recipes...")
      recipeLst = await asyncio.to_thread(functions.get_raw_recipe, regRecipe)
      print(f"recipeLst {recipeLst}")
      rawRecipe = {}
      if len(recipeLst) == 0:  # when regular and raw recipe the same
        recipeLst += [regRecipe]
      elif len(recipeLst) > 3:  # when there are too many recipes
        tempRecLst = []
        tempRecLst += [recipeLst[0]]
        tempRecLst += [recipeLst[-2]]
        tempRecLst += [recipeLst[-1]]
        recipeLst = tempRecLst
      rawRecipe = recipeLst[-1]

      print(rawRecipe, "is raw recipe")

      # gets the cost of each amt of materials in the current recipe
      def getCosts(prevRecipe, currRecipe):
        print(f"checking {currRecipe} with {prevRecipe}")
        material_price = {}
        for material in currRecipe:
          #print(f"curr processed: {material}")
          if prevRecipe != None:
            if prevRecipe.get(material) != None:
              if prevRecipe[material] == currRecipe[material]:
                material_price[material] = prevPrice[material]
              else:
                material_price[material] = (
                  prevPrice[material] /
                  prevRecipe[material]) * currRecipe[material]
            else:
              matID = globals.SB_ITEMS_DICT[material]
              matCost = functions.findCost(matID)
              if matCost == -1:
                material_price[material] = -1
              else:
                material_price[material] = functions.findCost(
                  matID) * currRecipe[material]
          else:
            matID = globals.SB_ITEMS_DICT[material]
            matCost = functions.findCost(matID)
            if matCost == -1:
              material_price[material] = -1
            else:
              material_price[material] = functions.findCost(
                matID) * currRecipe[material]
        return material_price

      # process the cost of the materials into proper sentences
      def processCosts(mat_prices, curr_recipe):
        #print(mat_prices, "process_cost debug mat prices")
        totalCost = 0
        for material in mat_prices:
          #print(f"current {material} in loop")
          #print(f"curr recipe: {curr_recipe}")
          globals.finalOutput.description += "\n" + f"> {curr_recipe[material]} {material}"
          #print(curr_recipe, "current recipe being processed")
          if curr_recipe[material] > 1:
            globals.finalOutput.description += "s"
          globals.finalOutput.description += ":"
          #print(mat_prices)
          if mat_prices[material] == -1:
            globals.finalOutput.description += " No one is selling it."
          elif mat_prices[material] == "Soulbound":
            globals.finalOutput.description += " Soulbound"
          else:
            mat_prices[material] = round(mat_prices[material])
            globals.finalOutput.description += f" {mat_prices[material]} coins."
          #print(curr_recipe[material], material, mat_prices[material])
          if totalCost != -1 and mat_prices[material] != -1:
            if mat_prices[material] != "Soulbound":
              totalCost += mat_prices[material]
          else:
            totalCost = -1
        if totalCost != -1:
          globals.finalOutput.description += "\n" + f"`Total Cost: {totalCost} coins.`"
        else:
          globals.finalOutput.description += "\n" + "`Total Cost: Incomplete.`"
        return (totalCost)

      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices..."
      )
      # getting the prices for the amts of materials
      recipeCosts = []
      recipeCosts.append(await asyncio.to_thread(getCosts, None, regRecipe))
      #recipeCosts.append(getCosts(None, regRecipe))
      #print(f"rec costs so far{recipeCosts}")
      prevPrice = recipeCosts[0]
      #print(f"rec list {recipeLst}")
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
          #recipeCosts.append(getCosts(recipeLst[-2], rawRecipe))
      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices... \nGetting Alt Recipe Prices... \nNote that if any items are from the auction house, it will take a little longer :slight_smile:"
      )
      #print(f"rec costs: {recipeCosts}")
      ahItems = []
      # for efficiency, all items in both raw and regular recipe will be processed together
      mainItemPrice = round(await
                            asyncio.to_thread(functions.findCost,
                                              globals.SB_ITEMS_DICT[name]))
      #print(f"mainItem Price of {name} in bz: {mainItemPrice}")
      if mainItemPrice == -1:  # if in auction house
        ahItems.append(name)
      j = 0
      costsLen = len(recipeCosts)
      prevPrice = recipeCosts[0]
      #print(recipeCosts, "check for auction items")
      while True:
        if j == costsLen:
          break
        else:
          #print(recipeCosts[j])
          for mat in recipeCosts[j]:
            #print(f"checking {recipeCosts[j]} for auction stuff")
            if recipeCosts[j][mat] == -1 and mat not in ahItems:
              if globals.SB_SOULBOUND_DICT[mat] == True:
                recipeCosts[j][mat] = "Soulbound"
              else:
                ahItems.append(mat)
          j += 1
      # places the auction house item costs into the recip cost dict
      if len(ahItems) > 0:
        ahItems = await asyncio.to_thread(functions.lowestBin, ahItems)
        #print(ahItems)
        count = 0
        #print(f"rec list {recipeLst}")
        for i in (ahItems):
          for j in range(len(recipeCosts)):
            if i in recipeCosts[j]:
              #print(f"{i} is in current rec {recipeCosts[j]}")
              if count == 0:
                #print(f"landed in regular recipe for {i}")
                if ahItems[i] == -1:
                  recipeCosts[j][i] = -1
                else:
                  recipeCosts[j][i] = regRecipe[i] * ahItems[i]
              elif count > 0:
                #print("landed in alt recipes")
                if ahItems[i] == -1:
                  recipeCosts[j][i] = -1
                else:
                  recipeCosts[j][i] = recipeLst[count - 1][i] * ahItems[i]
              if count == len(recipeCosts) - 1:
                count = 0
              else:
                count += 1
              #print(recipeCosts[j], "testin change to the recipe")
            else:
              count += 1
          count = 0
        if name in ahItems:
          mainItemPrice = ahItems[name]

      await interaction.edit_original_response(
        content=
        "Getting Regular Recipe... \nGetting Alt Recipes... \nGetting Regular Recipe Prices... \nGetting Alt Recipes' Prices... \nGetting Readable Results. Note that prices for bazaar items are based off lowest buy order prices, and prices for auction house items are based off of lowest BINs."
      )
      globals.finalOutput.title = f"{name}'s recipes:"
      # find total cost for each recipe
      recipeTotals = []
      i = 0
      #print(f"rec costs {recipeCosts}")
      while True:
        if i == 0:
          globals.finalOutput.description = "__**Regular Recipe:**__"
          recipeTotals += [
            await asyncio.to_thread(processCosts, recipeCosts[0], regRecipe)
          ]
        else:
          if len(recipeCosts) == 1 or i == len(recipeCosts) - 1:
            globals.finalOutput.description += "\n" + "\n" + "__**Raw Recipe:**__"
            recipeTotals += [
              await asyncio.to_thread(processCosts, recipeCosts[-1],
                                      recipeLst[-1])
            ]
            break
          else:
            globals.finalOutput.description += "\n" + "\n" + f"__**Alt Recipe {i}:**__"
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
      globals.finalOutput.description += "\n" + "\n" + "__**Profit Margin**__"
      globals.finalOutput.description += "\n" + f"> {name}'s price:"
      if mainItemPrice == -1:  # if no one's selling
        globals.finalOutput.description += " No one is selling it."
        globals.finalOutput.description += "\n" + "Put a price you like :slight_smile:."
        mainItemPrice = 0
      else:
        globals.finalOutput.description += f" {mainItemPrice} coins."
        recProfits = {}
        i = 0
        print("check point creating profit % ")
        while True:
          #print(i)
          if i == len(recipeCosts):
            break
          else:
            if recipeTotals[i] == -1:
              profit = 'N/A'
            else:
              profit = (round(
                (((mainItemPrice - recipeTotals[i]) / recipeTotals[i]) * 100),
                2))
            if i == 0:
              globals.finalOutput.description += "\n" + f"> Regular Recipe Proft %: {profit}%."
              recProfits["Regular Recipe"] = profit
            elif i == len(recipeCosts) - 1:
              globals.finalOutput.description += "\n" + f"> Raw Recipe Proft %: {profit}%."
              recProfits["Raw Recipe"] = profit
            else:
              globals.finalOutput.description += "\n" + f"> Alt Recipe {i} Proft %: {profit}%."
              recProfits[f"Alt Recipe {i}"] = profit
          i += 1
        bestProfitRec = ""
        bestProfit = 'N/A'
        # processes the biggest profit percentage
        for rec in recProfits:
          if recProfits[rec] != 'N/A':
            if bestProfit == 'N/A' or recProfits[rec] > bestProfit:
              bestProfit = recProfits[rec]
              bestProfitRec = rec
        globals.finalOutput.description += "\n" + f"`Craft it using {bestProfitRec}`"
      print("reached here not bad")
      end = time.time()
      globals.finalOutput.set_footer(
        text="Recipe Data By: NotEnoughUpdates" +
        f"\nProcess Time: {round((end-start), 2)} seconds")
      await interaction.edit_original_response(embed=globals.finalOutput)
  except:
    end = time.time()
    await interaction.response.send_message(
      f"Error: {name} not found. Check if the item name is spelled correctly. Note that the input is not case-sensitive."
    )

@tree.command(name = "cookieprofit", description = "provides a sorted list showing bit shop item profits")
async def cookieprofit(interaction: discord.Interaction, fameRank: str, filter: str):
  bPC = 4800 * globals.SB_BITS_FACTOR[fameRank]
  
  return True
@cookieprofit.autocomplete("fameRank")
async def cookieprofit_fameRank(interaction: discord.interaction, current: str):
  data = []
  for itemChoice in globals.SB_BITS_FACTOR:
    if current.lower() in itemChoice.lower():
      data.append(app_commands.Choice(name=itemChoice, value=itemChoice))
  return data[:5]
@cookieprofit.autocomplete("filter")
async def cookieprofit_filter(interaction: discord.interaction, current: str):
  data = []
  for itemChoice in globals.SB_BITS_FACTOR:
    if current.lower() in itemChoice.lower():
      data.append(app_commands.Choice(name=itemChoice, value=itemChoice))
  return data[:5]

@client.event
async def on_ready():
  await tree.sync()
  print('ITS ALIVE!!')


keep_alive()
client.run(TOKEN)
