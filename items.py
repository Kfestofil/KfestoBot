# A FILE CONTAINING ALL THE ITEMS IN THE GAME, ALWAYS TAKE ITEMS FROM HERE, NEVER CREATE ITEMS IN THE RPG.PY FILE
class Item:  # The Item class, use it when adding stuff to player inv
    def __init__(self, item_type: str, name: str, **kwargs):
        self.item_type = item_type
        self.name = name
        self.stats = {  # stat bonuses
            "Max Health": 0,
            "Max Mana": 0,
            "Int": 0,
            "Spd": 0,
            "Str": 0,
            "Dex": 0,
            "Armor" : 0,
            "Resistance" : 0,
        }

        # Define attribute mappings based on item type
        attribute_map = {
            "weapon": ["damage", "slot"],
            "equipment": ["slot"],
            "consumable": ["effect", "duration"]
        }

        # Set attributes based on the item type and provided kwargs
        if item_type in attribute_map:
            for attr in attribute_map[item_type]:
                if attr in kwargs:
                    setattr(self, attr, kwargs[attr])
                else:
                    print("(RPG) AN ITEM WAS CREATED WITHOUT ALL ATTRIBUTES")
                    setattr(self, attr, None)

        if 'stats' in kwargs:  # loading item
            self.stats = kwargs['stats']
        else:  # creating new
            for key in kwargs:  # Set the stat bonuses dictionary
                if key in self.stats.keys():
                    self.stats[key] = kwargs[key]


# EQUIPMENT NAMING SCHEME: ALL non-capital LETTERS, USE UNDERSCORES, NO ABBREVIATIONS,
# REMEMBER TO ALWAYS CALL THE new() FUNCTION WHEN GIVING ITEMS TO PLAYERS
class Consumables:
    health_potion = Item("consumable", "Health Potion", effect="heal", duration=5)
    mana_potion = Item("consumable","Mana Potion", effect="mana", duration=5)

class Weapons:
    rusty_sword = Item("weapon", "Rusty Sword", damage=10, slot="weapon")
    iron_dagger = Item("weapon", "Iron Dagger", damage=8, slot="weapon")
    wooden_club = Item("weapon", "Wooden Club", damage=12, slot="weapon")
    steel_sword = Item("weapon", "Steel Sword", damage=15, slot="weapon")
    old_bow = Item("weapon", "Enchanted Bow", damage=12, slot="weapon")
    divine_blade_of_kfestofil = Item("weapon", "The Divine Blade of Kfestofil, "  # 👌 made you look
                                  "The Harbinger of Death, "                                     # also we should make 1h/2h/offhands now
                                  "The Destroyer of Worlds, "
                                  "The Ender of Universes", damage=69420, slot="weapon")

class Helmets:
    old_hat = Item("equipment", "Old Hat", Armor=0, slot="head")
    leather_cap = Item("equipment", "Leather Cap", Armor=2, slot="head")
    iron_helmet = Item("equipment", "Iron Helmet", Armor=4, slot="head")
    steel_helm = Item("equipment", "Steel Helm", Armor=6, slot="head")
    mystical_hood = Item("equipment", "Mystical Hood", Armor=3, slot="head", Resistance=5) #actually we probably shouldnt add resistance
    fishelm = Item("equipment", "Fishelm, The protector of the weak, "
                                "The Light in the Dark, "
                                "The Last Hope", Armor=1337, slot="head")
class Chestplates:
    ragged_tunic = Item("equipment", "Ragged Tunic", Armor=0, slot="chest")
    leather_armor = Item("equipment", "Leather Armor", Armor=2, slot="chest")
    chainmail_vest = Item("equipment", "Chainmail Vest", Armor=4, slot="chest")
    plate_armor = Item("equipment", "Plate Armor", Armor=6, slot="chest")
class Pants:
    tattered_pants = Item("equipment", "Tattered Pants", Armor=0, slot="pants")
    leather_leggings = Item("equipment", "Leather Leggings", Armor=1, slot="pants")
    chainmail_leggings = Item("equipment", "Chainmail Leggings", Armor=3, slot="pants")
    steel_greaves = Item("equipment", "Steel Greaves", Armor=5, slot="pants")
    mystic_trousers = Item("equipment", "Mystic Trousers", Armor=2, slot="pants", Resistance=5) #ignore for now, might add later
class Boots:
    simple_sandals = Item("equipment", "Simple Sandals", Armor=0, slot="boots")
    leather_boots = Item("equipment", "Leather Boots", Armor=1, slot="boots")
    iron_sabatons = Item("equipment", "Iron Sabatons", Armor=3, slot="boots")
    steel_boots = Item("equipment", "Steel Boots", Armor=4, slot="boots")
    swift_shoes = Item("equipment", "Swift Shoes", Armor=2, slot="boots", Spd=5) #boosts speed stat on player