import json
import os
import random
import asyncio
import pprint
import shutil

# Vanilla folder (Obtain from .minecraft/versions/{version})
vanilla_folder = "1.21.11/"

# Replace with the location you want the datapack and resourcepack to output
# You may want to have them in their respective folders for easier testing
datpack_folder = "C:/Users/" + os.getlogin() + "/AppData/Roaming/ModrinthApp/profiles/Main/datapacks/Food"
resourcepack_folder = "C:/Users/" + os.getlogin() + "/AppData/Roaming/ModrinthApp/profiles/Main/resourcepacks/Food"

# Internal name, may cause issues if anyother datapack has the same one
namespace = "food"

"""
Until main(), the following code does not
need to be touched under practical use
"""

# Prepare a list of the Minecraft models that will be changed
models_modded = {}

class Item():
    def __init__(self, id, display_name, components, texture, item_to_replace="minecraft:firework_star"):
        self.id = id
        self.display_name = display_name

        # Append the item's name to the components
        name_components = {"custom_name": {"italic":False,"text":display_name},
                           "custom_model_data":{"strings":[id]}
                           }
        self.components = name_components | components
        self.texture = texture
        self.base_item = item_to_replace

        # Write a function of give command of the item
        write_mcfunction(datpack_folder+"/data/" + namespace + "/function/give_" + id + ".mcfunction", data_to_command(item_to_replace,self.components))

        # Write model
        write_json(resourcepack_folder + "/assets/" + namespace + "/item/" + id + ".json", 
                   {
            "model": {
            "type": "minecraft:model",
            "model": namespace + ":item/" + id
            }
        })

        write_json(resourcepack_folder + "/assets/" + namespace + "/models/item/" + id + ".json", {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": namespace + ":item/" + id
            }
        })

        # If this model has not been touched yet, mark it as modified
        if item_to_replace not in models_modded:
            model = read_json(vanilla_folder + "/assets/minecraft/items/" + item_to_replace[10:] +".json")
            models_modded[item_to_replace] = model

        # If this model has been modified, append changes instead of replacing
        else:
            model = models_modded[item_to_replace]
            pprint.pp(model)
        if model["model"]["type"] == "minecraft:model":
            model = {"model": {
                "type": "select",
                "property": "custom_model_data",
                "fallback": model["model"],
                "cases": [{
                    "when": id,
                    "model": {
                        "type": "model",
                        "model": "food:item/" + id
                    }
                }]
            }}
        else:
            model["model"]["cases"].append({
                    "when": id,
                    "model": {
                        "type": "model",
                        "model": "food:item/" + id
                    }
                })
            
        write_json(resourcepack_folder + "/assets/minecraft/items/" + item_to_replace[10:] + ".json", model)

        # Put the specified item's texture into the resourcepack
        duplicate("assets/"+texture, resourcepack_folder + "/assets/" + namespace + "/textures/item/" + texture)

def duplicate(source_path, destination_path):
    shutil.copy2(source_path, destination_path)

# Get the data of a JSON
def read_json(path):
    with open(path) as f:
        return json.load(f)

# Write to a new JSON
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# Get a dictionary of every json in a specific folder
# Useful for mass-modifying
def load_all_json(folder):
    files = {}
    for root, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(root, name)
            files[path] = read_json(path)
    return files

# Add components to a vanilla recipe's result
def modify_recipes(recipes, item_components):
    for path, data in recipes.items():
        try:
            item_id = data["result"]["id"]
            if item_id in item_components:
                data["result"]["components"] = item_components[item_id]
        except:
            pass

# Write components to a vanilla loot table's drops
def write_loot_data(entry, item_components):
    item_id = entry["name"]
    if item_id in item_components:
            
            try:
                entry["functions"] = entry["functions"] + ([
                {
                    "function": "minecraft:set_components",
                    "components": item_components[item_id],
                }
                 ])
            except:
                entry["functions"] = [
                    {
                        "function": "minecraft:set_components",
                        "components": item_components[item_id],
                    }
                ]
        
# Uhhh I don't remember what I did here
def modify_loot_tables(loot_tables, item_components):
    for path, data in loot_tables.items():
        try:
            pools = 0
            for pool in data["pools"]:
                pools += 1
                try:                    
                    for entry in pool["entries"]:
                        if entry["type"] == "minecraft:item" or entry["type"] == "minecraft:alternatives": 
                            if "children" in entry.keys():
                                for child in entry["children"]:
                                    write_loot_data(child, item_components)
                            else:    
                                write_loot_data(entry, item_components)
                except:
                    pass
        except:
            pass

def write_mcfunction(path, contents):
    with open(path, "w+") as f:
        if type(contents) == list:
            for command in contents:
                f.write(command)
        else:
            f.write(contents)

def data_to_command(item, components):
    result = "give @s " + item + "["
    for key,val in components.items():
        result += key + "=" + str(val) + ","

    return result[:-1] + "]"
            

# Write a new custom recipe
def make_recipe(name: str, type: str, result, result_amount: int, ingredients: list, pattern=[], category:str = "misc", group:str = None):
    recipe = {}
    path = datpack_folder + "/data/" + namespace + "/recipe/" + name + ".json"
    
    # Set the recipe
    if type == "shapeless":
        recipe["type"] = "minecraft:crafting_shapeless"
        recipe["ingredients"] = ingredients
    elif type == "shaped":
        recipe["type"] = "minecraft:crafting_shaped"
        recipe["pattern"] = pattern
        recipe["key"] = ingredients
    

    recipe["category"] = category
    recipe["group"] = group

    recipe["result"] = {
        "count": result_amount,
        "id": result.base_item,
        "components": result.components
    }
    write_json(path, recipe)

# Example code
def main():

    Dough = Item("dough", "Dough", {}, "dough.png")
    make_recipe("craft_dough", "shapeless", Dough, 2, ["minecraft:wheat"], group = "dough")

    Bleh = Item("bleh", "bleh", {}, "bleh.png")
    make_recipe("craft_bleh", "shaped", Bleh, 2, {"x": "minecraft:dirt", "z": "minecraft:copper_door"}, pattern=["xxx","xxx","zxz"], group = "bleh")

if __name__ == "__main__":
    main()