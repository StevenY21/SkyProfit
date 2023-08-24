# SkyProfit
A Hypixel Skyblock Bot that is all about trying to make money in Skyblock \
[STILL IN DEVELOPMENT] \
Currently has:
- craftprofit [item]: finds regular recipe, raw recipe, and 2 alternative recipes for a specified item.
  - provides the material prices for each recipe, and the profit percentage if the user decides to sell the item
  - currently not working with potions, pets, and a few random items
- cookieprofit [famerank] [filter]: finds profitability of items in bits shop
  - provides the bit cost, the lowest sell price in auction house or bazaar, the coins to bits ratio, and the profit in coins and %.
  - profit calculated based on the cost of bits, which depends on your fame rank and booster cookie price
- copperProfit: provides a list, from best to worst value, of all items that can be bought with copper in the Garden
  - item value based on amount of coins made per copper spent, which is based on the items sell price
  
In the works(higher up USUALLY means higher priority, but I'm consistent with that :)):
- enchantsProfit: provides a list of enchants, from best to worst profit, and checks the profit you can make by buying the lower level versions of it and combining into the max level version
- bazaarprofit: provides a list of all bazaar items, and lists them in flipping profitability, from highest to lowest.
- /bz [item]: provides the bazaar data of the item, as well as the profit from flipping
- candyProfit: provides a list, from best to worst value, of all items that can be bought with candy during the Spooky Festival
- petProfit: provides a list of all pets(or makes you input in one pet if I am lazy), and provides profit from converting pets to different rarites
- forgeProft: similar to craftprofit, but with items that are made in Dwarven Mines Forge and based on your HOTM
- /ah [item]: finds all instances of the item in BIN and lists them from highest to lowest, and attempts to calculate ah flip profit of the item


Hypixel Skyblock Bazaar and General Item Data Source: Hypixel Public API 
Hypixel Skyblock Item Recipe Data Source: NotEnoughUpdates Master Repo
Hypixel Skyblock Auction House Data(Lowest BINS of all items on AH): https://moulberry.codes/lowestbin.json
