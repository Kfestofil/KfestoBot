import datetime
import random
from PIL import Image
from discord import Interaction
from discord import embeds

class Player:
    def __init__(self, discordID: int, interaction: Interaction, position = [256,256]):
        self.screen = "main"  # main, menu[1,2,...], map
        self.awaitingDeletion = False
        self.ID = discordID
        self.position = [0,0]
        self.position[0] = position[0] + 7
        self.position[1] = position[1] + 7
        while dataMatrix[self.position[0]][self.position[1]]["Entity"] is not None:
            self.position = [random.randint(253,259),random.randint(253,259)]
        dataMatrix[self.position[0]][self.position[1]]["Entity"] = self
        self.interaction = interaction
        self.afkTimer = datetime.datetime.now()
        self.stats = {
            "stat1" : 10,
            "stat2" : 14,
            "stat3" : 12,
        }
        self.inventory: list[Item] = []
        # Example usage:
        sword = Item("weapon", "Sword", damage=10, hand_requirement="one-handed")
        helmet = Item("equipment", "Helmet", armor_class=5, slot="head")
        potion = Item("consumable", "Health Potion", effect="heal", duration=5)
        self.inventory.extend([sword, helmet, potion])


class Item:
    def __init__(self, item_type: str, name: str, **kwargs):
        self.item_type = item_type
        self.name = name

        # Define attribute mappings based on item type
        attribute_map = {
            "weapon": ["damage", "hand_requirement"],
            "equipment": ["armor_class", "slot"],
            "consumable": ["effect", "duration"]
        }

        # Set attributes based on the item type and provided kwargs
        if item_type in attribute_map:
            for attr in attribute_map[item_type]:
                if attr in kwargs:
                    setattr(self, attr, kwargs[attr])
                else:
                    print("(RPG) AN ITEM WAS CREATED WITHOUT PROPER ATTRIBUTES")
                    setattr(self, attr, None)


Tiles = {
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

Tags = {
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

Emotes = {
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

    "other_player" : ":neutral_face:",
    "player" : ":grinning:",
}

Directions = {
    'w' : [0, -1],
    's' : [0, 1],
    'a' : [-1,0],
    'd' : [1,0]
}


def add_border_to_matrix(dataMatrix):
    # Determine the original dimensions of the dataMatrix
    original_height = len(dataMatrix[0])      # Number of rows (y-coordinate or height)
    original_width = len(dataMatrix)    # Number of columns (x-coordinate or width)

    # Calculate the new dimensions with the border
    new_height = original_height + 14      # Add 7 rows at the top and 7 rows at the bottom
    new_width = original_width + 14        # Add 7 columns at the left and 7 columns at the right

    # Create a new matrix with the updated dimensions and set all values to the set_value
    new_matrix = [[{"Tile": "no_vision", "Entity": None} for _ in range(new_width)] for _ in range(new_height)]

    # Copy the original dataMatrix into the new_matrix, leaving the border intact
    for i in range(original_height):
        for j in range(original_width):
            new_matrix[i + 7][j + 7] = dataMatrix[i][j]

    return new_matrix

def loadMapFile(file: str, realMap: bool):
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


dataMatrix = loadMapFile('Map.bmp', True)
miniMatrix = loadMapFile('miniMap.bmp', False)

# with open("rpgDataMatrix.txt", 'w') as file:  # Saving the data if we ever need it
#     for y in range(dimensions[1]):
#         file.write('\n')
#         for x in range(dimensions[0]):
#             file.write(str(str(x) + ', ' + str(y) + ' ' + str(dataMatrix[x][y]) + ' '))

playerList: list[Player] = []


def playerMove(direction: str, player: Player):
    player.afkTimer = datetime.datetime.now()
    newpos = [player.position[0] + Directions[direction][0], player.position[1] + Directions[direction][1]]
    if "walkable" in Tags[dataMatrix[newpos[0]][newpos[1]]["Tile"]] and dataMatrix[newpos[0]][newpos[1]]["Entity"] is None:
        dataMatrix[player.position[0]][player.position[1]]["Entity"] = None
        player.position = newpos
        dataMatrix[player.position[0]][player.position[1]]["Entity"] = player


def prepareRender(player: Player):
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
                if type(data["Entity"]) == Player:
                    if data["Entity"].ID == player.ID:
                        viewport[x][y] = "player"
                    else:
                        viewport[x][y] = "other_player"
            # print(startX +  x, ', ', startY + y, ' ', str(viewport[x][y]))
    # print(position)
    # viewport[6][6] = "player"
    return viewport


def miniPrepareRender(player: Player):
    relativeX = round(player.position[0] / (512 + 14) * 12)
    relativeY = round(player.position[1] / (512 + 14) * 12)
    viewport = [[0 for i in range(13)] for j in range(13)]
    for x in range(13):
        for y in range(13):
            tile = miniMatrix[x][y]["Tile"]
            if x == relativeX and y == relativeY: tile = "player"
            viewport[x][y] = tile
    return viewport

def render(viewport = []):
    text = ''
    for y in range(13):
        for x in range(13):
            text += Emotes[viewport[x][y]]
        text += '\n'
    return text


def menu1(player: Player):
    stats = ''
    inventory = ''
    for stat in player.stats.keys():
        stats += f"{stat}: {player.stats[stat]}\n"
    for item in player.inventory:
        inventory += item.name + " | "
        for attr in item.__dict__:
            if attr not in ("item_type", "name"):
                inventory += attr + ": " + str(item.__dict__[attr]) + " | "
        inventory += "\n"
    embed = embeds.Embed(title=player.interaction.user.display_name + "'s Character", color=0xe80046)
    username = player.interaction.user.display_name
    embed.add_field(name="Stats", value=stats, inline=False)
    embed.add_field(name="Inventory", value=inventory, inline=False)
    return embed
