import json
import os
import random
import asyncio
import pprint
import shutil

vanilla_folder = "1.21.11/"
datpack_folder = "C:/Users/" + os.getlogin() + "/AppData/Roaming/ModrinthApp/profiles/Main/datapacks/Food"
resourcepack_folder = "C:/Users/" + os.getlogin() + "/AppData/Roaming/ModrinthApp/profiles/Main/resourcepacks/Food"
namespace = "food"


models_modded = {}

class Item():
    def __init__(self, id, display_name, components, texture, item_to_replace="minecraft:firework_star"):
        self.id = id
        self.display_name = display_name
        name_components = {"custom_name": {"italic":False,"text":display_name},
                           "custom_model_data":{"strings":[id]}
                           }
        self.components = name_components | components
        self.texture = texture
        self.base_item = item_to_replace

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

        if item_to_replace not in models_modded:
            model = read_json(vanilla_folder + "/assets/minecraft/items/" + item_to_replace[10:] +".json")
            
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
        if item_to_replace not in models_modded:
            models_modded[item_to_replace] = model
        else:
            print("new model is:")
            pprint.pp(model)
        write_json(resourcepack_folder + "/assets/minecraft/items/" + item_to_replace[10:] + ".json", model)

        duplicate("assets/"+texture, resourcepack_folder + "/assets/" + namespace + "/textures/item/" + texture)

def duplicate(source_path, destination_path):
    shutil.copy2(source_path, destination_path)

def read_json(path):
    with open(path) as f:
        return json.load(f)

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_all_json(folder):
    files = {}
    for root, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(root, name)
            files[path] = read_json(path)
    return files


def modify_recipes(recipes, item_components):
    for path, data in recipes.items():
        try:
            item_id = data["result"]["id"]
            if item_id in item_components:
                data["result"]["components"] = item_components[item_id]
        except:
            pass

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
def modify_loot_tables(loot_tables, item_components):
    for path, data in loot_tables.items():
        if True: #path[-(len("oak_leaves.json")):] == "oak_leaves.json":
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

def make_recipe(name: str, type: str, result: Item, result_amount: int, ingredients: list, pattern=[], category:str = "misc", group:str = None):
    recipe = {}
    path = datpack_folder + "/data/" + namespace + "/recipe/" + name + ".json"
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


def new_item(id, components, recipes):
    path = datpack_folder + "/data/" + namespace + "/"

    for name, data in recipes:
        write_json(path + "recipe/"+name+".json", data)

def main():

    Dough = Item("dough", "Dough", {}, "dough.png")
    make_recipe("craft_dough", "shapeless", Dough, 2, ["minecraft:wheat"], group = "dough")

    Bleh = Item("bleh", "bleh", {}, "bleh.png")
    make_recipe("craft_bleh", "shapeless", Bleh, 2, ["minecraft:diamond"], group = "bleh")

if __name__ == "__main__":
    main()