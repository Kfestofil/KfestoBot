# A FILE CONTAINING ALL THE ITEMS IN THE GAME, ALWAYS TAKE ITEMS FROM HERE, NEVER CREATE ITEMS IN THE RPG.PY FILE
class Item:  # The Item class, use it when adding stuff to player inv
    def __init__(self, item_type: str, name: str, **kwargs):
        self.item_type = item_type
        self.name = name

        # Define attribute mappings based on item type
        attribute_map = {
            "weapon": ["damage", "slot"],
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


# EQUIPEMENT NAMING SCHEME: ALL non-capital LETTERS, USE UNDERSCORES, NO ABBREVIATIONS,
# REMEMBER TO ALWAYS CALL THE new() FUNCTION WHEN GIVING ITEMS TO PLAYERS
class Consumables:
    health_potion = Item("consumable", "Health Potion", effect="heal", duration=5)
    mana_potion = Item("consumable","Mana Potion", effect="mana", duration=5)

class Weapons:
    rusty_sword = Item("weapon", "Rusty sword", damage=10, slot="weapon")
    divine_blade_of_kfestofil = Item("weapon", "The Divine Blade of Kfestofil, "  # Don't.
                                  "The Harbinger of Death, "
                                  "The Destroyer of Worlds, "
                                  "The Ender of Universes", damage=69420, slot="weapon")

class Helmets:
    old_hat = Item("equipment", "Old hat", armor_class=0, slot="head")
    fishelm = Item("equipment", "Fishelm, The protector of the weak, "
                                "The Light in the Dark, "
                                "The Last Hope", armor_class=1337, slot="head")

class Chestplates:
    ragged_tunic = Item("equipment", "Ragged tunic", armor_class=0, slot="chest")

class Pants:
    tattered_pants = Item("equipment", "Tattered pants", armor_class=0, slot="pants")

class Boots:
    simple_sandals = Item("equipment", "Simple sandals", armor_class=0, slot="boots")