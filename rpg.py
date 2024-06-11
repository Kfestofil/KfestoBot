import asyncio
import datetime
import math
import random
import items
import copy
from PIL import Image
from discord import Interaction
from threading import Thread
from threading import Event
from discord import embeds
from items import Item


def new(item: Item):
    return copy.deepcopy(item)


class Player:  # The most important class in the entire game, has all the stuff related to a player in the game
    def __init__(self, discordID: int, interaction: Interaction, position =[160,46]):  # default pos is 256,256
        self.screen = "main"  # main, menu[1,2,...], map
        self.awaitingDeletion = False
        self.ID = discordID
        self.position = [0,0]
        self.position[0] = position[0] + 7  # Those are here because of the border adding by ChatGPT™
        self.position[1] = position[1] + 7
        while dataMatrix[self.position[0]][self.position[1]]["Entity"] is not None:  # Do not spawn on other players
            self.position = [random.randint(253+7,259+7),random.randint(253+7,259+7)]  # This forgets about the set (if set) position... fix at some point
        dataMatrix[self.position[0]][self.position[1]]["Entity"] = self  # Basically tell the game he's there
        self.interaction = interaction  # The discord interaction passes to this class, need to access it later to edit the game message
        self.afkTimer = datetime.datetime.now()
        self.currentHealth = 100
        self.currentMana = 100
        self.level = 1
        self.exp = 0
        self.statPoints = 0
        self.stats = {  # placeholder, we probably doin this next
            "Max Health" : 100,
            "Max Mana" : 100,
            "Int" : 10,
            "Spd" : 10,
            "Str" : 10,
            "Dex" : 10,
        }
        self.statusEffects = {
            "poison" : [0,0], #[duration, damage]
            "bleed" : [0,0] #[duration, %damage]
        }
        self.alive = True
        self.menuSelection = 0
        self.selectedObject = None
        self.fightAction = 0  # 0 - awaiting action, 1 - attack, 2 - run, 3 - fight finished awaiting end, add more if necessary
        self.tookAction = Event()  # Read about python threading Events before doing something with this
        self.inventory: list[Item] = []
        self.inventory.extend([new(items.Consumables.health_potion), new(items.Consumables.mana_potion),new(items.Boots.swift_shoes)])
        self.equipment = {
            "weapon" : new(items.Weapons.rusty_sword),
            "head" : new(items.Helmets.old_hat),
            "chest" : new(items.Chestplates.ragged_tunic),
            "pants" : new(items.Pants.tattered_pants),
            "boots" : new(items.Boots.simple_sandals),
        }

        if interaction.user.id == 490793326476263434:
            self.inventory.append(new(items.Weapons.divine_blade_of_kfestofil))
        if interaction.user.id == 448145391154626575:
            self.inventory.append(new(items.Helmets.fishelm))

class Mob:
    def __init__(self, mob_type: str, zone: str = "map1", position = [0,0]):
        self.level = random.randint(1,10)
        self.levelMultiplier = (self.level*2 + 5)/10
        self.mob_type = mob_type
        self.alive = True
        self.position = position
        self.lastAction = [f"{mob_type.capitalize()} is ready to kick your ass!", ""]  # the first field is text in bold, the second one is under it
        self.expMultiplier = 1

        if self.mob_type == "zombie":
            self.health = random.randint(65, 115)
            self.attack = random.randint(9, 14)
        elif self.mob_type == "vampire":
            self.health = random.randint(80, 150)
            self.attack = random.randint(19, 29)
            self.expMultiplier = 2
        elif self.mob_type == "skeleton":
            self.health = random.randint(50, 80)
            self.attack = random.randint(14, 19)
        elif self.mob_type == "bear":
            self.health = random.randint(80, 150)
            self.attack = random.randint(24, 34)
            self.expMultiplier = 3
        elif self.mob_type == "pumpkin_zombie":
            self.health = random.randint(80, 135)
            self.attack = random.randint(12, 18)
            self.expMultiplier = 1.5
        elif self.mob_type == "rice_snake":
            self.health = random.randint(35, 55)
            self.attack = random.randint(12, 18)
            self.expMultiplier = 0.8
        elif self.mob_type == "jellyfish":
            self.health = random.randint(40, 70)
            self.attack = random.randint(16, 22)
        else:
            self.health = 0
            self.attack = 0
            print(f"Unknown mob type: {self.mob_type}")

        self.health *= self.levelMultiplier
        self.attack *= self.levelMultiplier
        self.health = round(self.health)




Tiles = {  # Dict containing the color mapping to the tile names
    "199a0d" : "grass",
    "37c5ff" : "water_passable",
    "209cce" : "water_impassable",
    "6b6b6b" : "wall_stone",
    "bebebe" : "path_cobblestone",
    "c38812" : "path_dirt",
    "a36d00" : "wall_wood",
    "136418" : "tree_leafy",
    "ffc93a" : "chair",
    "c8af6d" : "table",
    "c7a054" : "floor_wood",
    "0d3d3d" : "grave",
    "ba2a02" : "bed",
    "83807c" : "rock",
    "543801" : "doors_closed",
    "fad783" : "books",
    "92cbe1" : "fountain",
    "ff0e00" : "lava",
    "000000" : "no_vision",
    "ff00de" : "rice_grain",
    "dcd604" : "boat",
    "b10031" : "target",
    "fff135" : "corn",
    "947332" : "horse",
}

Colors = {v: k for k, v in Tiles.items()}  # reversed Colors dict

Tags = {  # Dict containing the tags set for each tile, currently only the walkable/not_walkable tags exist
    "grass" : {"walkable",},
    "water_passable" : {"walkable",},
    "water_impassable" : {"not_walkable",},
    "wall_stone" : {"not_walkable",},
    "path_cobblestone" : {"walkable",},
    "path_dirt" : {"walkable",},
    "wall_wood" : {"not_walkable",},
    "tree_leafy" : {"not_walkable",},
    "chair" : {"walkable",},
    "table" : {"not_walkable",},
    "floor_wood" : {"walkable",},
    "grave" : {"not_walkable",},
    "bed" : {"not_walkable",},
    "rock" : {"not_walkable",},
    "doors_closed" : {"not_walkable",},
    "books" : {"not_walkable",},
    "fountain" : {"not_walkable",},
    "lava" : {"not_walkable",},
    "no_vision" : {"not_walkable",},
    "rice_grain" : {"not_walkable",},
    "boat" : {"not_walkable",},
    "target" : {"not_walkable",},
    "corn" : {"not_walkable",},
    "horse" : {"not_walkable",},
}

MobSpawnZones = {  # Dict that has all the colors for mob zones
    "989898" : {"zombie:5", "skeleton:3", "vampire:1"},
    "8a4b00" : {"bear:5",},
    "92a100" : {"pumpkin_zombie:8",},
    "c100a5" : {"rice_snake:8",},
    "0079c5" : {"jellyfish:8",},
    "000000" : {"none:0"}
}

Emotes = {  # Dict that has all the tiles and their emotes mapped to them
    "grass" : "🟩",
    "water_passable" : "🟦",
    "water_impassable" : "🌊",
    "wall_stone" : ":white_square_button:",
    "path_cobblestone" : "⬜",
    "path_dirt" : "🟫",
    "wall_wood" : "🟧",
    "tree_leafy" : "🌳",
    "chair" : "🪑",
    "table" : "🟤",
    "floor_wood" : "🟨",
    "grave" : "🪦",
    "bed" : "🛏️",
    "rock" : "🪨",
    "doors_closed" : "🚪",
    "books" : "📚",
    "fountain" : "⛲",
    "lava" : "🟥",
    "no_vision" : "◼️",
    "rice_grain" : "🌾",
    "boat" : "🛶",
    "target" : "🎯",
    "corn" : "🌽",
    "horse" : "🐴",
    # Entity tiles:
    "other_player" : ":neutral_face:",
    "player" : ":grinning:",
    "zombie" : "🤢",
    "skeleton" : "💀",
    "vampire" : "🧛",
    "bear" : "🐻",
    "pumpkin_zombie" : "🎃",
    "rice_snake" : "🐍",
    "jellyfish" : "🪼",
}

Directions = {  # the buttons pass w,a,s,d strings instead of inputs cuz im lazy
    'w' : [0, -1],
    's' : [0, 1],
    'a' : [-1,0],
    'd' : [1,0]
}


def add_border_to_matrix(dataMatrix, mobMatrix = False):  # ChatGPT™
    # Determine the original dimensions of the dataMatrix
    original_height = len(dataMatrix[0])      # Number of rows (y-coordinate or height)
    original_width = len(dataMatrix)    # Number of columns (x-coordinate or width)

    # Calculate the new dimensions with the border
    new_height = original_height + 14      # Add 7 rows at the top and 7 rows at the bottom
    new_width = original_width + 14        # Add 7 columns at the left and 7 columns at the right

    # Create a new matrix with the updated dimensions and set all values to the set_value
    if mobMatrix:
        new_matrix = [[{"MobSpawnData": "None"} for _ in range(new_width)] for _ in range(new_height)]
    else:
        new_matrix = [[{"Tile": "no_vision", "Entity": None} for _ in range(new_width)] for _ in range(new_height)]

    # Copy the original dataMatrix into the new_matrix, leaving the border intact
    for i in range(original_height):
        for j in range(original_width):
            new_matrix[i + 7][j + 7] = dataMatrix[i][j]

    return new_matrix


def loadMapFile(file: str, realMap: bool):  # Loads a map file into a dataMatrix, realMap only makes it so the border ain't added
    tempImg = Image.open(file)
    dimensions = tempImg.size
    mapImg = tempImg.load()
    def hexPixelValue(x: int, y: int):
        return '%02x%02x%02x' % mapImg[x,y]
    matrix = [[0 for i in range(dimensions[1])] for j in range(dimensions[0])]
    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            if realMap:
                matrix[x][y] = {
                    "Tile" : Tiles[hexPixelValue(x,y)],
                    "Entity" : None,
                }
            else:
                matrix[x][y] = {"Tile": Tiles[hexPixelValue(x, y)]}
    if realMap: matrix = add_border_to_matrix(matrix)
    return matrix


def loadMobZonesFile(file: str):  # Loads a mob zones file into a mobSpawnMatrix
    tempImg = Image.open(file)
    dimensions = tempImg.size
    mapImg = tempImg.load()
    def hexPixelValue(x: int, y: int):
        return '%02x%02x%02x' % mapImg[x,y]
    matrix = [[0 for i in range(dimensions[1])] for j in range(dimensions[0])]
    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
             matrix[x][y] = {
                 "MobSpawnData": MobSpawnZones[hexPixelValue(x, y)],
            }

    matrix = add_border_to_matrix(matrix, True)
    return matrix

dataMatrix = loadMapFile('Map.bmp', True)
miniMatrix = loadMapFile('miniMap.bmp', False)
mobSpawnMatrix = loadMobZonesFile("Map1 mob spawns.bmp")

# with open("rpgDataMatrix.txt", 'w') as file:  # Saving the data if we ever need it
#     for y in range(dimensions[1]):
#         file.write('\n')
#         for x in range(dimensions[0]):
#             file.write(str(str(x) + ', ' + str(y) + ' ' + str(dataMatrix[x][y]) + ' '))

playerList: list[Player] = []


def playerMove(direction: str, player: Player):  # good luck figuring this out
    player.afkTimer = datetime.datetime.now()
    newpos = [player.position[0] + Directions[direction][0], player.position[1] + Directions[direction][1]]
    if "walkable" in Tags[dataMatrix[newpos[0]][newpos[1]]["Tile"]] and dataMatrix[newpos[0]][newpos[1]]["Entity"] is None:
        dataMatrix[player.position[0]][player.position[1]]["Entity"] = None
        player.position = newpos
        dataMatrix[player.position[0]][player.position[1]]["Entity"] = player


def prepareRender(player: Player):  # Prepares render, basically a 13x13 grid of tiles to render
    posX = player.position[0]
    posY = player.position[1]
    startX = posX - 6
    startY = posY - 6
    viewport = [[0 for i in range(13)] for j in range(13)]
    for x in range(13):
        for y in range(13):
            data = dataMatrix[startX + x][startY + y]
            if data["Entity"] is None:
                viewport[x][y] = data["Tile"]
            else:
                if type(data["Entity"]) is Player:
                    if data["Entity"].ID == player.ID:
                        viewport[x][y] = "player"
                    else:
                        viewport[x][y] = "other_player"
                elif type(data["Entity"]) is Mob:
                    mob: Mob = data["Entity"]
                    viewport[x][y] = mob.mob_type
            # print(startX +  x, ', ', startY + y, ' ', str(viewport[x][y]))
    # print(position)
    # viewport[6][6] = "player"
    return viewport


def miniPrepareRender(player: Player):  # Prepares minimap render
    relativeX = round(player.position[0] / (512 + 14) * 12)
    relativeY = round(player.position[1] / (512 + 14) * 12)
    viewport = [[0 for i in range(13)] for j in range(13)]
    for x in range(13):
        for y in range(13):
            tile = miniMatrix[x][y]["Tile"]
            if x == relativeX and y == relativeY: tile = "player"
            viewport[x][y] = tile
    return viewport


def render(viewport = []):  # Renders a prepareRender viewport, basically a string to send as a message on discord
    text = ''
    for y in range(13):
        for x in range(13):
            text += Emotes[viewport[x][y]]
        text += '\n'
    return text


def countPlayerStats(player: Player):
    stats = {}
    stats.update(player.stats)
    stats.update({"Armor" : 0, "Resistance" : 0})
    for i in player.equipment.values():
        i: Item
        for key in stats.keys():
            stats[key] += i.stats[key]
    return stats


def menu1(player: Player):  # Returns a discord embed for the character menu
    stats = ''
    levelStats = ''
    levelStats += f"Level: `{player.level}`\nExperience: `{player.exp}`\nStat Points: `{player.statPoints}`"
    # armor = 0
    # for i in player.equipment.values():
    #     try:
    #         armor += i.Armor
    #     except AttributeError:
    #         continue

    statdict = countPlayerStats(player)

    for stat in statdict.keys():
        stats += f"{stat}: `{statdict[stat]}`\n"
    username = player.interaction.user.display_name
    embed = embeds.Embed(title=username + "'s Character", color=0xe80046)
    embed.add_field(name="Progress", value=levelStats, inline=False)
    embed.add_field(name="Stats", value=stats, inline=False)
    return embed


def menu2(player: Player):  # Returns the embed for interaction menu
    embed = embeds.Embed(title="Interactable entities in your proximity", color=0xe80046)
    sel = player.menuSelection
    text = ""
    entities = getInteractables(player)
    if sel < 0:
        player.menuSelection = len(entities) - 1
        sel = len(entities) - 1
    if sel >= len(entities):
        player.menuSelection = 0
        sel = 0
    for e in range(len(entities)):
        mob: Mob = entities[e]
        if e == sel:
            text += "> "
            player.selectedObject = entities[e]
        text += f"{mob.mob_type.capitalize()} lv.{mob.level}\n"
    embed.add_field(name=text, value="", inline=False)
    return embed


def menuSelect(player: Player):  # Function that handles the action for when object is selected in menu
    if player.screen == "menu2":
        entity = player.selectedObject
        if type(entity) is Mob:
            combatThread = Thread(target=combatInitiated, args=(player,entity))
            combatThread.start()
            player.screen = "fight"
    if player.screen == "menu3":
        item = player.selectedObject
        if type(item) is Item:
            if item.item_type in ("weapon", "equipment"):
                slot = item.slot
                temp = player.equipment[slot]
                player.inventory.append(temp)
                player.equipment[slot] = item
                player.inventory.remove(item)


def menuFight(player: Player, enemy: Mob):
    pHealth = player.currentHealth
    eHealth = enemy.health
    pName = player.interaction.user.display_name
    eName = enemy.mob_type.capitalize()
    embed = embeds.Embed(title=player.interaction.user.display_name + " vs " + enemy.mob_type, color=0xe80046)
    hpsField = f"{pName}'s HP: `{pHealth}`\n{eName}'s HP: `{eHealth}`"
    embed.add_field(name="Battle stats:", value=hpsField, inline=False)
    eAction = enemy.lastAction
    embed.add_field(name=eAction[0], value=eAction[1], inline=False)
    return embed


def menu3(player: Player):  # Returns the embed for Inventory menu
    embed = embeds.Embed(title="Inventory", color=0xe80046)
    stats = f"HP: `{player.currentHealth}`, MP: `{player.currentMana}`"
    sel = player.menuSelection
    text = ""
    texte = ""
    equipmentk = [item for item in player.equipment.keys()]
    for eqi in equipmentk:
        texte += f"{eqi.capitalize()}: `{player.equipment[eqi].name}`\n"

    items = [item for item in player.inventory if item.item_type != "consumable"]
    items.extend([item for item in player.inventory if item.item_type == "consumable"])
    if sel < 0:
        player.menuSelection = len(items) - 1
        sel = len(items) - 1
    if sel >= len(items):
        player.menuSelection = 0
        sel = 0
    for e in range(len(items)):
        it: Item = items[e]
        if e == sel:
            text += "> "
            player.selectedObject = it
        text += f"{it.name}\n"

    embed.add_field(name="stats", value=stats, inline=False)
    embed.add_field(name="Equipment", value=texte, inline=False)
    embed.add_field(name="Inventory", value=text, inline=False)
    return embed


def getInteractables(player: Player):
    entities = []
    pos = player.position
    for x in range(pos[0] - 1, pos[0] + 2):
        for y in range(pos[1] - 1, pos[1] + 2):
            if dataMatrix[x][y]["Entity"] is not None:
                if type(dataMatrix[x][y]["Entity"]) is not Player:
                    entities.append(dataMatrix[x][y]["Entity"])
    return entities

def count_mobs_in_area(x, y, area_size=13, mob_limit=10):
    mob_count = 0
    rows = len(dataMatrix[0])  # Number of rows
    cols = len(dataMatrix)  # Number of columns

    # Define the boundaries of the area
    half_area_size = area_size // 2
    start_x = max(0, x - half_area_size)
    end_x = min(rows, x + half_area_size + 1)
    start_y = max(0, y - half_area_size)
    end_y = min(cols, y + half_area_size + 1)

    # Count the mobs in the area
    for i in range(start_x, end_x):
        for j in range(start_y, end_y):
            if dataMatrix[i][j]["Entity"] is not None and type(dataMatrix[i][j]["Entity"]) is not Player:
                mob_count += 1
                if mob_count >= mob_limit:
                    return mob_count  # Early exit if limit is reached
    return mob_count


def weaponAttack(weapon: Item, player: Player, entity: Mob, base=100):
    strModifier = (player.stats["Str"] + 1 ) / ((player.stats["Str"] + 1) + base) + 1
    weaponDmg = strModifier * weapon.damage
    weaponDmg = round(weaponDmg)
    entity.health -= weaponDmg
    if entity.health <= 0:
        entity.alive = False


def takeDamage(player: Player, damage, base=100):
    # if player.stats["Armor"] < 0:
    #     player.stats["Armor"] = 0
    # armor = 0
    # for i in player.equipment.values():
    #     try:
    #         armor += i.Armor
    #     except AttributeError:
    #         continue
    statdict = countPlayerStats(player)
    armor = statdict["Armor"]

    damage_reduction = (armor + 1) / ((armor + 1) + base)
    dmg = damage*(1 - damage_reduction)
    dmg = round(dmg)
    player.currentHealth -= dmg
    return dmg

def checkPlayerStatus(player: Player):
    if player.statusEffects["poison"][0] > 0:
        player.currentHealth -= player.statusEffects["poison"][1]
        player.statusEffects["poison"][0] -= 1
    if player.statusEffects["bleed"][0] > 0:
        player.currentHealth *= player.statusEffects["bleed"][1]/100
        player.statusEffects["bleed"][0] -= 1
    player.currentHealth = round(player.currentHealth)
    if player.currentHealth <= 0:
        player.alive = False


def combatInitiated(player: Player, hostileEntity):
    pTurn = True  # checks if it's player's turn
    pWeapon = player.equipment["weapon"]
    mob: Mob = hostileEntity
    while True:
        if pTurn:
            flag = player.tookAction.wait(300)
            if flag:
                action = player.fightAction
                if action == 1:
                    weaponAttack(pWeapon, player, mob)
                    if not mob.alive: break
                if action == 2:
                    break
            player.tookAction.clear()
            pTurn = False
        else:
            dmg = mob.attack
            dmg = takeDamage(player, dmg)
            mob.lastAction = [f"{mob.mob_type.capitalize()} attacked you!", f" it dealt {dmg} damage!"]
            checkPlayerStatus(player)
            if not player.alive:
                print(f"{player.interaction.user.display_name} just got killed")
                break
            pTurn = True
    player.tookAction.clear()

    if not mob.alive:
        player.exp += math.ceil(mob.level * mob.expMultiplier)
        if player.level * 50 <= player.exp:
            player.exp = 0
            player.level += 1
            player.statPoints += 3
            print(player.ID)
            print(player.statPoints)
        dataMatrix[mob.position[0]][mob.position[1]]["Entity"] = None
        del mob
    if not player.alive:
        player.awaitingDeletion = True

    player.fightAction = 3


def spawnMobs():
    mobAreaLimit = 10
    print("(RPG) Spawning mobs...")
    for x in range(len(mobSpawnMatrix)):
        for y in range(len(mobSpawnMatrix[0])):
            if mobSpawnMatrix[x][y] != "none" and "walkable" in Tags[dataMatrix[x][y]["Tile"]] and dataMatrix[x][y]["Entity"] is None:
                if count_mobs_in_area(x, y, mob_limit=mobAreaLimit) < mobAreaLimit:
                    for mobSpawnData in mobSpawnMatrix[x][y]["MobSpawnData"]:
                        mobType = mobSpawnData.split(':')[0]
                        spawnRate = int(mobSpawnData.split(':')[1])
                        if random.randint(1, 1000) <= spawnRate:
                            dataMatrix[x][y]["Entity"] = Mob(mobType, position=[x,y])
                            break
    print("(RPG) Finished spawning")


async def gameServerLoop():  # the tick value should be the greatest common divisor between all the loops if we make any
    gameTimer = datetime.datetime.now()
    mobSpawnThread = Thread(target=spawnMobs)
    mobSpawnThread.start()
    tick = 60
    while True:
        if len(playerList) > 0:
            mobSpawnThread = Thread(target=spawnMobs)
            mobSpawnThread.start()
        await asyncio.sleep(tick)