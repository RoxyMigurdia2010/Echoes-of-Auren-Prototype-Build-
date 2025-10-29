# =====================================
# Echoes of Auren
# Author: Congchi Lee
# Version: 1.8.0
# Date: 2025-10-28
# =====================================

import os
import random
import time
import sys
import json
import copy

# ==============================================================================
# ## 1. GAME DATA & CONSTANTS ##
# (All game data is centralized here for easy editing)
# ==============================================================================

GAME_TITLE = "Echoes of Auren"
WORLD_NAME = "Auren"

APP_DATA_PATH = os.getenv('APPDATA')
GAME_SAVE_DIRECTORY = os.path.join(APP_DATA_PATH, "EchoesOfAuren")
try:
    if not os.path.exists(GAME_SAVE_DIRECTORY):
        os.makedirs(GAME_SAVE_DIRECTORY)
except Exception as e:
    print(f"CRITICAL ERROR: Could not create save directory: {e}")
    GAME_SAVE_DIRECTORY = "."
# List of save slot filenames
SAVE_SLOTS = ["save_1.json", "save_2.json", "save_3.json"]

MAP_DATA = [
    ["plains", "plains", "plains", "plains", "forest", "mountain", "cave", "ruins"],
    ["forest", "forest", "forest", "forest", "forest", "hills", "mountain", "ruins"],
    ["forest", "fields", "bridge", "plains", "hills", "forest", "hills", "ruins"],
    ["plains", "shop", "town", "mayor", "plains", "hills", "mountain", "ruins"],
    ["plains", "fields", "fields", "plains", "hills", "mountain", "mountain", "ruins"],
    ["swamp", "swamp", "fields", "plains", "hills", "mountain", "mountain", "ruins"]
]

BIOMES = {
    "plains": {"t": "PLAINS", "e": True, "m": ["Slime", "Wolf"]},
    "forest": {"t": "WOODS", "e": True, "m": ["Orc", "Shadow_Stalker", "Goblin", "Goblin Shaman"]},
    # v1.8: Replaced Wolf
    "fields": {"t": "FIELDS", "e": False},
    "bridge": {"t": "BRIDGE", "e": True, "m": ["Slime"]},
    "town": {"t": "TOWN CENTRE", "e": False},
    "shop": {"t": "SHOP", "e": False},
    "mayor": {"t": "MAYOR'S OFFICE", "e": False},
    "cave": {"t": "DRAGON'S CAVE", "e": False},
    "mountain": {"t": "MOUNTAIN", "e": True, "m": ["Golem", "Orc", "Fire Slime"]},
    "hills": {"t": "HILLS", "e": True, "m": ["Goblin", "Slime", "Goblin Shaman"]},
    "swamp": {"t": "MURKY SWAMP", "e": True, "m": ["Slime", "Fire Slime", "Goblin Shaman"]},
    "ruins": {"t": "HAUNTED RUINS", "e": True, "m": ["Skeleton", "Ghost", "Wraith"]}
}

BIOME_ICONS = {
    # --- Biome Icons ---
    "plains": ".",
    "forest": "T",
    "fields": "~",
    "bridge": "=",
    "town": "H",
    "shop": "$",
    "mayor": "H",
    "cave": "∩",
    "mountain": "▲",
    "hills": "n",
    "swamp": "s",
    "ruins": "R",
    # --- Special Icons ---
    "PLAYER": "@",  # Your icon
    "FOG": " ",  # Unexplored
    "UNKNOWN": "?"  # Error
}

MOBS = {
    "Goblin": {"hp": 18, "atk": 3, "gold": 6, "xp": 10,
               "loot_table": {"EQ_W_001": 0.1},
               "effects": []},
    "Slime": {"hp": 30, "atk": 2, "gold": 9, "xp": 12,
              "loot_table": {"EQ_C_001": 0.05},
              "effects": []},
    "Wolf": {"hp": 25, "atk": 4, "gold": 8, "xp": 15,
             "loot_table": {"EQ_A_001": 0.05},
             "effects": [{"id": "STUN", "chance": 0.15, "turns": 1}]},
    "Orc": {"hp": 45, "atk": 6, "gold": 22, "xp": 30,
            "loot_table": {"EQ_W_002": 0.05},
            "effects": []},
    "Golem": {"hp": 65, "atk": 5, "gold": 28, "xp": 40,
              "loot_table": {},
              "effects": []},
    "Dragon": {"hp": 180, "atk": 14, "gold": 200, "xp": 0,
               "loot_table": {},
               "effects": [{"id": "BURN", "chance": 0.3, "turns": 3}]},
    "Dragon_WorldBoss": {"hp": 250, "atk": 18, "gold": 500, "xp": 0,
                         "loot_table": {},
                         "effects": [{"id": "BURN", "chance": 0.5, "turns": 3}]},
    "Fire Slime": {"hp": 28, "atk": 4, "gold": 12, "xp": 15,
                   "loot_table": {"EQ_C_002": 0.05},
                   "effects": [{"id": "BURN", "chance": 0.2, "turns": 2}]},
    "Goblin Shaman": {"hp": 35, "atk": 3, "gold": 15, "xp": 20,
                      "loot_table": {"EQ_C_003": 0.02},
                      "effects": []},
    "Skeleton": {"hp": 50, "atk": 7, "gold": 25, "xp": 35,
                 "loot_table": {"EQ_W_004": 0.05, "EQ_A_003": 0.03},
                 "effects": []},
    "Ghost": {"hp": 40, "atk": 6, "gold": 30, "xp": 40,
              "loot_table": {"EQ_C_004": 0.05},
              "effects": []},
    "Wraith": {"hp": 70, "atk": 9, "gold": 50, "xp": 60,
               "loot_table": {"EQ_W_005": 0.05},
               "effects": [{"id": "STUN", "chance": 0.1, "turns": 1}]},
    "Tutorial_Dummy": {"hp": 25, "atk": 1, "gold": 0, "xp": 0, "loot_table": {}, "effects": []},
    # --- ADDITIONS v1.8 ---
    "Shadow_Stalker": {"hp": 20, "atk": 5, "gold": 10, "xp": 18,
                       "loot_table": {"EQ_W_003": 0.05},
                       "effects": [{"id": "BLEED", "chance": 0.2, "turns": 3}]},
    "Corrupted_Wolf": {"hp": 35, "atk": 6, "gold": 15, "xp": 25,
                       "loot_table": {"EQ_A_001": 0.1},
                       "effects": [{"id": "STUN", "chance": 0.15, "turns": 1},
                                   {"id": "BLEED", "chance": 0.2, "turns": 2}]},
    "Auren_Sentinel": {"hp": 80, "atk": 7, "gold": 40, "xp": 50,
                       "loot_table": {},
                       "effects": []}  # Skill is handled in handle_enemy_turn
}

EQUIPMENT_DB = {
    # Weapons
    "EQ_W_001": {"name": "Rusted Sword", "type": "weapon", "stats": {"atk": 2},
                 "desc": "A sword that remembers too many battles, and lost its last one."},  # v1.8: Desc updated
    "EQ_W_002": {"name": "Orcish Cleaver", "type": "weapon", "stats": {"atk": 4}, "desc": "A heavy, crude blade."},
    "EQ_W_003": {"name": "Poison Dagger", "type": "weapon", "stats": {"atk": 1},
                 "effect_on_hit": {"id": "POISON", "chance": 0.3, "turns": 3},
                 "desc": "A weak dagger coated in grime."},
    "EQ_W_004": {"name": "Ancient Sword", "type": "weapon", "stats": {"atk": 6},
                 "desc": "A well-balanced blade from the ruins."},
    "EQ_W_005": {"name": "Shadow Dagger", "type": "weapon", "stats": {"atk": 3},
                 "effect_on_hit": {"id": "MANA_DRAIN", "chance": 0.15, "turns": 2},
                 "desc": "A dagger that seems to cut at the soul."},
    # Armors
    "EQ_A_001": {"name": "Leather Tunic", "type": "armor", "stats": {"def": 1, "hp_max": 5},
                 "desc": "Simple leather protection."},
    "EQ_A_002": {"name": "Chainmail Vest", "type": "armor", "stats": {"def": 3}, "desc": "Heavy, but effective."},
    "EQ_A_003": {"name": "Runic Mail", "type": "armor", "stats": {"def": 4, "hp_max": 10},
                 "desc": "Runes of protection, faded because the world forgot what they protect."},
    # v1.8: Desc updated
    "EQ_A_004": {"name": "Acolyte's Robe", "type": "armor", "stats": {"def": 2},
                 "special": "resist_burn_50",
                 "desc": "Robes worn by fire worshippers."},
    # Charms
    "EQ_C_001": {"name": "Slime Core", "type": "charm", "stats": {"hp_max": 10},
                 "desc": "A simple, jellied memory. It only remembers how to hold together."},  # v1.8: Desc updated
    "EQ_C_002": {"name": "Ember Shard", "type": "charm", "stats": {},
                 "effect_on_hit": {"id": "BURN", "chance": 0.1, "turns": 2},
                 "desc": "Warm to the touch."},
    "EQ_C_003": {"name": "Lucky Coin", "type": "charm", "stats": {"gold_bonus": 0.1}, "desc": "A faint glint of luck."},
    "EQ_C_004": {"name": "Ghostly Pendant", "type": "charm", "stats": {},
                 "special": "evade_phys_10",
                 "desc": "It feels cold and slightly transparent."}
}

EFFECTS_DB = {
    "POISON": {
        "name": "Poisoned",
        "type": "dot",
        "value": 2,
        "msg_inflict": "is POISONED!",
        "msg_tick": "takes 2 poison damage."
    },
    "BURN": {
        "name": "Burning",
        "type": "dot",
        "value": 3,
        "msg_inflict": "is BURNING!",
        "msg_tick": "takes 3 burn damage."
    },
    "STUN": {
        "name": "Stunned",
        "type": "control",
        "msg_inflict": "is STUNNED!",
        "msg_tick": "is stunned and cannot move!"
    },
    "REGEN": {
        "name": "Regen",
        "type": "hot",
        "value": 2,
        "msg_inflict": "is REGENERATING!",
        "msg_tick": "heals for 2 HP."
    },
    "MANA_DRAIN": {
        "name": "Mana Drain",
        "type": "control",
        "msg_inflict": "is drained of energy!",
        "msg_tick": "'s skills are put on cooldown!"
    },
    # --- ADDITIONS v1.8 ---
    "BLEED": {
        "name": "Bleeding",
        "type": "dot",
        "value": 2,
        "msg_inflict": "is BLEEDING!",
        "msg_tick": "takes 2 bleed damage."
    },
    "SLEEP": {
        "name": "Sleeping",
        "type": "control",
        "msg_inflict": "falls ASLEEP!",
        "msg_tick": "is asleep and cannot move!"
    }
}

MAIN_QUESTS = {
    "MQ_01": {
        "title": "Auren's Call",
        "desc": "You awaken to a faint echo. Find out what's happening at the Town Centre.",
        "type": "VISIT",
        "target": "town"
    },
    "MQ_02": {
        "title": "The Mayor's Plea",
        "desc": "The Mayor is worried. He asks you to speak with Lira at the Echo Guild.",
        "type": "TALK",
        "target": "LIRA"
    },
    "MQ_03": {
        "title": "Proving Your Echo",
        "desc": "Lira needs you to grow stronger. Prove your worth by clearing 5 Goblins from the hills.",
        "type": "KILL", "target_mob": "Goblin", "needed": 5,
        "reward_gold": 100, "reward_xp": 150
    },
    "MQ_04": {
        "title": "The First True Echo",
        "desc": "Lira senses a 'Fallen Knight's' echo, lost somewhere in the forests. Find it.",
        "type": "COLLECT_ECHO", "target_codex": "fallen_knight",
        "reward_gold": 50, "reward_xp": 100
    },
    "MQ_04_COMPLETE": {
        "title": "The Knight's Vow",
        "desc": "You found the Knight's echo. You feel stronger. Return to the Mayor.",
        "type": "TALK", "target": "MAYOR"
    },
    # --- v1.8: Hero Path Rework ---
    "MQ_05_HERO_A": {
        "title": "The Hero's Path: Patience",
        "desc": "Lira states strength is not just muscle, but resolve. Find the 'Shrine of Moss' in the wilds.",
        "type": "COLLECT_ECHO", "target_codex": "shrine_memory"
    },
    "MQ_05_HERO_B": {
        "title": "The Hero's Path: Understanding",
        "desc": "To win, you must understand why the seal was made. Find the 'Cultist's Diary' at the dragon's cave.",
        "type": "COLLECT_ECHO", "target_codex": "dragon_cultist_diary"
    },
    "MQ_05_HERO_C": {
        "title": "The Hero's Path: The Final Test",
        "desc": "Lira is ready to test your strength and wisdom. Defeat the 'Auren Sentinel' she has summoned in the hills.",
        "type": "KILL", "target_mob": "Auren_Sentinel", "needed": 1
    },
    "MQ_05_RECKLESS": {
        "title": "The Reckless Path",
        "desc": "The seal was forced. The dragon has escaped. Find and slay it.",
        "type": "KILL", "target_mob": "Dragon_WorldBoss", "needed": 1
    },
    "MQ_06_HERO": {
        "title": "Confront the Flame",
        "desc": "The seal is safely broken. Confront the dragon in its lair.",
        "type": "KILL", "target_mob": "Dragon", "needed": 1
    }
}

SIDE_QUEST_POOL = {
    # --- Tier 1 (Level 1-4) ---
    "SQ_SLIME_01": {
        "title": "A Sticky Situation", "desc": "Clear out 6 Slimes from the plains.",
        "type": "KILL", "target_mob": "Slime", "needed": 6,
        "reward_gold": 50, "reward_xp": 70, "min_level": 1
    },
    "SQ_GOBLIN_01": {
        "title": "Hilltop Pests", "desc": "Defeat 4 Goblins in the hills.",
        "type": "KILL", "target_mob": "Goblin", "needed": 4,
        "reward_gold": 60, "reward_xp": 80, "min_level": 2
    },
    # v1.8: Farmer Quest (Interactable)
    "SQ_FARMER_01": {
        "title": "The Lost Lullaby",
        "desc": "A farmer in the fields (1,2) seeks an old tune. Find a 'Merchant Spirit' who might remember it.",
        "type": "COLLECT_ECHO", "target_codex": "merchant_spirit",
        "reward_gold": 100, "reward_xp": 150, "min_level": 4, "is_board_quest": False
    },
    # --- Tier 2 (Level 5-9) ---
    "SQ_WOLF_02": {
        "title": "The Wolf Pack", "desc": "A pack of 3 Wolves is menacing the forest path.",
        "type": "KILL", "target_mob": "Wolf", "needed": 3,
        "reward_gold": 90, "reward_xp": 110, "min_level": 6
    },
    "SQ_ORC_01": {
        "title": "Orc Sighting", "desc": "An Orc scout was seen in the mountains. Defeat 1 Orc.",
        "type": "KILL", "target_mob": "Orc", "needed": 1,
        "reward_gold": 100, "reward_xp": 130, "min_level": 7
    },
    # v1.8: Swamp Quest
    "SQ_GUARD_01": {
        "title": "Swamp Menace",
        "desc": "A Shaman in the swamp is corrupting the water, spawning Fire Slimes. Slay the Goblin Shaman.",
        "type": "KILL", "target_mob": "Goblin Shaman", "needed": 1,
        "reward_gold": 150, "reward_xp": 200, "min_level": 8
    },
    # --- Tier 3 (Level 10+) ---
    "SQ_GOLEM_01": {
        "title": "Stone Sentinels", "desc": "The Golems in the mountains are awakening. Take one down.",
        "type": "KILL", "target_mob": "Golem", "needed": 1,
        "reward_gold": 150, "reward_xp": 200, "min_level": 10
    },
    # v1.8: Reckless Path Quest
    "SQ_R_01": {
        "title": "(RECKLESS) Chaos Cleanup",
        "desc": "The broken seal has driven the plains wolves mad! Slay 5 'Corrupted Wolves' before they reach town.",
        "type": "KILL", "target_mob": "Corrupted_Wolf", "needed": 5,
        "reward_gold": 250, "reward_xp": 350, "min_level": 10, "exclusive_path": "RECKLESS"
    },
    "SQ_RUINS_01": {
        "title": "Cleansing the Ruins", "desc": "The skeletons in the Haunted Ruins are a threat. Clear 5 of them.",
        "type": "KILL", "target_mob": "Skeleton", "needed": 5,
        "reward_gold": 180, "reward_xp": 250, "min_level": 12
    },
    "SQ_RUINS_02": {
        "title": "Silent Spirits", "desc": "The Ghosts of the ruins seem tormented. Defeat 3 Ghosts.",
        "type": "KILL", "target_mob": "Ghost", "needed": 3,
        "reward_gold": 200, "reward_xp": 280, "min_level": 13
    }
}

BIOME_FLAVORS = {
    "plains": {
        "lines": [
            "Tall grass brushes at your knees. Once, someone laughed here and the sound lingered.",
            "The plain smells faintly of baked earth and distant smoke; a memory disguised as weather."
        ], "prob": 0.25
    },
    "forest": {
        "lines": [
            "Pine resin hangs in the air. A song once rose among these trees, quiet as a hidden thing.",
            "Moss clings to stone and bone; prayers have long since softened into green."
        ], "prob": 0.25
    },
    "hills": {
        "lines": ["The wind rolls over the slope carrying an old, half-remembered chorus."],
        "prob": 0.25
    },
    "cave": {
        "lines": ["Warm breath from the depths brushes your face; something sealed still breathes."],
        "prob": 0.40
    },
    "town": {
        "lines": ["Hammers ring; children shout. Normality is a careful thing here."],
        "prob": 0.20
    },
    "bridge": {
        "lines": ["The bridge creaks like an old chest; voices cross the water like paper boats."],
        "prob": 0.25
    },
    "fields": {
        "lines": ["Fields smell of seed and late sun. A furrow holds a whisper of some long promise."],
        "prob": 0.25
    },
    "shop": {
        "lines": ["Shelves are orderly and yet some things look as if they were placed by memory rather than need."],
        "prob": 0.15
    },
    "mayor": {
        "lines": ["The mayor's steps echo in a room full of decisions that no one remembers making."],
        "prob": 0.15
    },
    "mountain": {
        "lines": ["Stone climbs skyward here; the mountain keeps its secrets under a calm face."],
        "prob": 0.30
    },
    "swamp": {
        "lines": ["The air is thick and smells of rot. Something bubbles beneath the murky water.",
                  "Gnarled trees reach out like skeletal claws. You hear a distant croak."],
        "prob": 0.35
    },
    "ruins": {
        "lines": ["Broken columns stand like teeth against the sky. A cold wind whispers forgotten names.",
                  "You step on a cracked tile bearing a royal crest. This place held importance once."],
        "prob": 0.40
    }
}

CODEX_ENTRIES = {
    "ECHO_GIFT_01": {
        "title": "The First Echo",
        "text": "A faint whisper, the very first memory that answered your call. It feels like a promise.",
        "buff": {"atk": 1}
    },
    "shrine_memory": {
        "title": "Shrine of Moss",
        "text": "Someone once knelt at this shrine and sang. The song remained like dew on the stone.",
        "buff": {"def": 2, "hp_max": 5},
        "combat_effect": {"id": "REGEN", "turns": 99}
    },
    "fallen_knight": {
        "title": "The Knight's Promise",
        "text": "He fought for a vow. He asked not for glory, but for someone to finish what he began.",
        "buff": {"atk": 2, "def": -1}
    },
    "crimson_flower": {
        "title": "Crimson Bloom",
        "text": "Beauty that stings; it remembers both seed and wound.",
        "buff": {},
        "effect_on_hit": {"id": "POISON", "chance": 0.3, "turns": 3}
    },
    "merchant_spirit": {
        "title": "Merchant Spirit",
        "text": "A small lantern-eyed thing that trades memories like trinkets. It smiles without lips.",
        "buff": {"gold_bonus": 0.25}
    },
    "mirror_echo": {
        "title": "Reflected Soul",
        "text": "You looked into fractured glass and found what the land refused to keep.",
        "buff": {"atk": 1, "def": 1}
    },
    "town_rumor": {
        "title": "Town's Whisper",
        "text": "Villagers speak of an old path behind the inn, where echoes gather at dusk.",
        "buff": {}
    },
    "ruined_king_memory": {
        "title": "Fallen King's Crown",
        "text": "A memory of a crown, heavy with regret. It remembers ruling over dust and shadows.",
        "buff": {"atk": 1, "def": 1}
    },
    # --- ADDITIONS v1.8 ---
    "farmer_memory": {
        "title": "Farmer's Memory",
        "text": "The earth is cold. The fire... the fire that warmed us, where did it go? The children know only the cold now.",
        "buff": {"hp_max": 10}
    },
    "dragon_cultist_diary": {
        "title": "Cultist's Diary Scrap",
        "text": "The weak sealed the flame. We worship it. The fire of forgetting will cleanse Auren... The fools in town do not understand the power of forgetting.",
        "buff": {},
        "special": "resist_burn_25"
    },
    "ancient_lullaby": {
        "title": "Ancient Lullaby",
        "text": "An old tune, it tells of a world where the night was safe and warm. It feels... peaceful.",
        "buff": {"def": 1},
        "effect_on_hit": {"id": "SLEEP", "chance": 0.05, "turns": 1}
    }
}


# ==============================================================================
# ## 2. HELPER & UTILITY FUNCTIONS ##
# (Basic utility functions)
# ==============================================================================

def clear_screen():
    # Clears the terminal screen.
    os.system("cls" if os.name == "nt" else "clear")


def draw_line():
    # Prints a separator line.
    print("xX--------------------xX")


def typewriter_effect(text, delay=0.03):
    # Prints text with a typewriter effect.
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


## NEW (v1.6.4): Safe input wrapper ##
def safe_input(prompt):
    # Handles EOFError (Ctrl+D) during input.
    try:
        return input(prompt)
    except EOFError:
        print("\n(Input cancelled.)")
        return ""


def draw_minimap(player):
    # Draws the game map with fog of war.
    print("--- MAP ---")
    px, py = player['x'], player['y']
    visited = player.get('visited_tiles') or [[px, py]]
    VISION_RANGE = 1

    # Update visited tiles
    for y_vision in range(py - VISION_RANGE, py + VISION_RANGE + 1):
        for x_vision in range(px - VISION_RANGE, px + VISION_RANGE + 1):
            if 0 <= y_vision < len(MAP_DATA) and 0 <= x_vision < len(MAP_DATA[0]):
                if [x_vision, y_vision] not in visited:
                    visited.append([x_vision, y_vision])
    player['visited_tiles'] = visited

    # Draw the map grid
    for y, row in enumerate(MAP_DATA):
        line = ""
        for x, tile_code in enumerate(row):
            is_player_pos = (x == px and y == py)
            is_visited = [x, y] in visited

            if is_player_pos:
                icon_to_draw = BIOME_ICONS.get("PLAYER", "@")
                line += f"[{icon_to_draw}] "
            elif is_visited:
                icon_to_draw = BIOME_ICONS.get(tile_code, "?")
                line += f" {icon_to_draw}  "
            else:
                icon_to_draw = BIOME_ICONS.get("FOG", " ")
                line += f" {icon_to_draw}  "
        print(line)

    print("-----------")


def show_biome_flavor(player):
    # Displays descriptive text for the current biome.
    tile = MAP_DATA[player['y']][player['x']]
    flavor = BIOME_FLAVORS.get(tile)
    if not flavor or random.random() >= flavor['prob']: return
    line = random.choice(flavor['lines'])
    typewriter_effect(line, delay=0.02)
    time.sleep(0.6)


def get_save_slot_info(slot_file):
    # Reads basic info from a save file for display.
    try:
        with open(slot_file, "r") as f:
            player_data = json.load(f)

        x, y = player_data.get('x', 0), player_data.get('y', 0)

        # Failsafe for loading saves before map expansion
        if y >= len(MAP_DATA) or x >= len(MAP_DATA[0]):
            x, y = 2, 3  # Default to town

        tile_code = MAP_DATA[y][x]
        location_name = BIOMES[tile_code]['t']

        # Calculate approximate ATK for display
        atk_stat = player_data.get('total_atk', player_data.get('base_atk', player_data.get('atk', 3)))

        return {
            "name": player_data.get('name', 'Unknown'),
            "level": player_data.get('level', 1),
            "atk": atk_stat,
            "location": location_name
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return None  # Empty or corrupted slot


# ==============================================================================
# ## 3. CORE DATA HANDLERS ##
# (Functions for managing player data)
# ==============================================================================

def create_new_player(name, slot_file):
    # Initializes a new player dictionary.
    start_pos = [1, 3]
    player_data = {
        "name": name,
        "hp": 50, "hp_max": 50,
        "base_atk": 3, "base_def": 0,
        "bonus_atk": 0, "bonus_def": 0,
        "total_atk": 3, "total_def": 0, "gold_bonus": 0.0,

        "pot": 1, "elix": 0, "gold": 0,
        "x": start_pos[0], "y": start_pos[1],
        "seal": True,
        "key": False,
        "level": 1, "xp": 0, "xp_to_next_level": 40,
        "dev_mode": False,
        "rage_potions": 0,
        "stone_potions": 0,
        "active_buff": None,
        "codex": [],
        "skills_cd": {},
        "skip_next": False,
        "guard": False,
        "respawned": False,
        "visited_tiles": [start_pos],
        "main_quest_id": "MQ_01",
        "quest_progress": {},
        "active_side_quests": [],
        "completed_side_quests": [],  # v1.8: Added
        "save_slot": slot_file,
        "active_effects": [],
        "equipment": {"weapon": None, "armor": None, "charm": None},
        "inventory": ["EQ_W_001"],
        "equipped_echo": None
    }

    # Calculate initial stats and fully heal
    player_data = recalculate_player_stats(player_data)
    player_data['hp'] = player_data['hp_max']
    return player_data


def save_game(player):
    # Saves the player data to their assigned slot file.
    slot_file = player.get('save_slot')
    if not slot_file:
        print("Error: No save slot associated with player.")
        time.sleep(1.5)
        return

    try:
        with open(slot_file, "w") as f:
            json.dump(player, f, indent=4)
        print("Game saved!")
    except Exception as e:
        print("Failed to save:", e)
    time.sleep(1)


def load_game(slot_file):
    try:
        with open(slot_file, "r") as f:
            player = json.load(f)

        # Apply defaults for fields added in later versions
        player.setdefault('codex', [])
        player.setdefault('skills_cd', {})
        player.setdefault('skip_next', False)
        player.setdefault('guard', False)
        player.setdefault('respawned', False)
        player.setdefault('key', False)
        player.setdefault('visited_tiles', [[player.get('x', 0), player.get('y', 0)]])
        player.setdefault('main_quest_id', 'MQ_01')
        player.setdefault('quest_progress', {})
        player.setdefault('active_side_quests', [])
        player.setdefault('save_slot', slot_file)
        player.setdefault('equipment', {"weapon": None, "armor": None, "charm": None})
        player.setdefault('inventory', [])
        player.setdefault('equipped_echo', None)
        player.setdefault('base_atk', player.get('atk', 3))
        player.setdefault('base_def', 0)
        player.setdefault('bonus_atk', 0)
        player.setdefault('bonus_def', 0)
        player.setdefault('active_effects', [])
        player.setdefault('completed_side_quests', [])  # v1.8: Added

        # Failsafe for loading saves before map expansion
        if player['y'] >= len(MAP_DATA) or player['x'] >= len(MAP_DATA[0]):
            player['x'], player['y'] = 2, 3
            print("Detected old save location. Warping to Town Centre.")

        # Clean up stale quest progress entries
        active_quests = player.get('active_side_quests', [])
        main_quest = player.get('main_quest_id', '')
        new_quest_progress = {}
        for q_id in player.get('quest_progress', {}):
            if q_id in active_quests or q_id == main_quest or main_quest.startswith(q_id):  # v1.8: Fix for quest chains
                new_quest_progress[q_id] = player['quest_progress'][q_id]
        player['quest_progress'] = new_quest_progress

        # Always recalculate stats on load
        player = recalculate_player_stats(player)

        # Ensure HP isn't higher than max after potential stat changes
        if player['hp'] > player['hp_max']:
            player['hp'] = player['hp_max']

        print(f"Welcome back, {player['name']}!")
        safe_input("> ")
        return player
    except (FileNotFoundError, json.JSONDecodeError):
        print("No valid save file found.")
        time.sleep(1.2)
        return None


def recalculate_player_stats(player):
    current_hp_percent = player.get('hp', 1) / max(1, player.get('hp_max', 1))

    # Start with base stats from level and permanent bonuses
    total_atk = player['base_atk'] + player.get('bonus_atk', 0)
    total_def = player['base_def'] + player.get('bonus_def', 0)
    total_hp_max = 50 + ((player['level'] - 1) * 10)
    total_gold_bonus = 0.0

    # Add stats from Equipment
    for slot, item_id in player['equipment'].items():
        if item_id:
            item_data = EQUIPMENT_DB.get(item_id)
            if item_data:
                for stat, value in item_data.get('stats', {}).items():
                    if stat == 'atk': total_atk += value
                    if stat == 'def': total_def += value
                    if stat == 'hp_max': total_hp_max += value
                    if stat == 'gold_bonus': total_gold_bonus += value

    # Add buffs from the single Focused Echo
    echo_id = player['equipped_echo']
    if echo_id:
        echo_data = CODEX_ENTRIES.get(echo_id)
        if echo_data:
            for stat, value in echo_data.get('buff', {}).items():
                if stat == 'atk': total_atk += value
                if stat == 'def': total_def += value
                if stat == 'hp_max': total_hp_max += value
                if stat == 'gold_bonus': total_gold_bonus += value

    # Update player object with calculated totals
    player['total_atk'] = total_atk
    player['total_def'] = total_def
    player['hp_max'] = total_hp_max
    player['gold_bonus'] = total_gold_bonus

    # Restore HP based on percentage, clamped to 1 minimum
    new_hp = max(1, int(player['hp_max'] * current_hp_percent))

    # Ensure HP doesn't exceed new max
    player['hp'] = min(new_hp, player['hp_max'])

    return player


def handle_level_up(player):
    # Handles player leveling up.
    leveled_up = False
    max_level = 50  # Set a maximum level cap

    while player['xp'] >= player['xp_to_next_level'] and player['level'] < max_level:
        leveled_up = True
        overflow = player['xp'] - player['xp_to_next_level']
        player['level'] += 1
        player['base_atk'] += 1  # Increase BASE ATK
        player['xp'] = overflow
        player['xp_to_next_level'] = int(player['xp_to_next_level'] * 1.6)

        # If max level is reached, set XP requirements high
        if player['level'] == max_level:
            player['xp'] = 0
            player['xp_to_next_level'] = 9999999  # Effectively infinite

    if leveled_up:
        draw_line()
        print(f"LEVEL UP! You are now level {player['level']}!")
        # Recalculate stats BEFORE fully healing
        player = recalculate_player_stats(player)
        player['hp'] = player['hp_max']  # Full heal to new max HP

        print(f"HP MAX increased to {player['hp_max']}!")
        print(f"Base ATK increased to {player['base_atk']}!")
        print(f"(Total ATK is now {player['total_atk']})")
        if player['level'] == max_level:
            print("You have reached the maximum level!")
        else:
            print(f"Next level at {player['xp_to_next_level']} XP.")
        draw_line()
    return player


def codex_add(player, entry_id):
    if entry_id not in CODEX_ENTRIES: return player
    if entry_id not in player.get('codex', []):
        player.setdefault('codex', []).append(entry_id)
        print(f"(New Echo added to Codex: {CODEX_ENTRIES[entry_id]['title']})")
        player = check_quest_completion(player, "COLLECT_ECHO", entry_id)
    return player


def show_codex(player):
    clear_screen()
    draw_line()
    print("ECHO CODEX (Collected Memories)")
    draw_line()
    if not player.get('codex'):
        print("You have not collected any echoes yet.")
        print("\n(Visit the Echo Guild in Town to Focus on a memory)")
    else:
        codex_list = sorted(player.get('codex', []))
        for i, eid in enumerate(codex_list, 1):
            entry = CODEX_ENTRIES.get(eid, {})
            print(f"[{i}] {entry.get('title', 'Unknown')}")
    draw_line()
    print("\nEnter number to read, or press Enter to return.")
    choice = safe_input("# ")

    codex_list = sorted(player.get('codex', []))

    if choice.strip().isdigit():
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(codex_list):
            eid_to_read = codex_list[idx]
            entry = CODEX_ENTRIES.get(eid_to_read, {})

            # Sub-menu for displaying echo details
            clear_screen()
            draw_line()
            print(f"{entry.get('title', 'Unknown')}")
            draw_line()
            typewriter_effect(entry.get('text', ''), delay=0.03)
            draw_line()

            # Show potential buffs and effects
            if entry.get('buff'):
                print(f"Focus Buff: {entry['buff']}")
            if entry.get('effect_on_hit'):
                eff = entry['effect_on_hit']
                print(f"Focus Effect (On Hit): {eff.get('chance', 0) * 100}% chance to inflict {eff.get('id', '?')}")
            if entry.get('combat_effect'):
                eff = entry['combat_effect']
                print(f"Focus Effect (Combat Start): Applies {eff.get('id', '?')}")

            draw_line()
            print("(To Focus this memory, visit the Echo Guild in Town)")
            safe_input("\n> Press Enter to return to Codex...")
            show_codex(player)  # Return to the codex list
    # Return if user pressed Enter or invalid input
    return


## MODIFIED (v1.7): Added skill upgrades and new skills ##
def skill_available(player, skill_name):
    # Checks if a skill is available based on level or codex.
    lv = player.get('level', 1)
    codex = player.get('codex', [])

    if skill_name == "Focus Strike": return lv >= 3
    if skill_name == "Guard": return lv >= 4
    if skill_name == "Meditate": return lv >= 6
    if skill_name == "Limit Break": return lv >= 10

    ## NEW SKILLS & UPGRADES (v1.7) ##
    if skill_name == "Purify": return lv >= 12
    if skill_name == "Focus Strike II": return lv >= 15
    if skill_name == "Guard II": return lv >= 18
    if skill_name == "Meditate II": return lv >= 20

    if skill_name == "Reflected Strike": return "mirror_echo" in codex

    return False


def skill_on_cooldown(player, skill_name):
    # Checks if a skill is currently on cooldown.
    base_skill_name = skill_name.replace(" II", "")
    return player.get('skills_cd', {}).get(base_skill_name, 0) > 0


def set_skill_cd(player, skill_name, turns):
    # Sets the cooldown for a skill.
    base_skill_name = skill_name.replace(" II", "")
    player.setdefault('skills_cd', {})[base_skill_name] = turns


def decrement_skill_cooldowns(player):
    # Reduces cooldown turns for all active cooldowns.
    for k in list(player.get('skills_cd', {}).keys()):
        if player['skills_cd'][k] > 0:
            player['skills_cd'][k] -= 1


# ==============================================================================
# ## 4. GAME STATE HANDLERS ##
# (Functions handling each game screen/state)
# ==============================================================================

def handle_main_menu():
    # Displays the main game menu.
    clear_screen()
    draw_line()
    # Simple ASCII Art for the title
    print(r"""
█▀▀░█▀▀░█░█░█▀█░█▀▀░█▀▀░░█▀█░█▀▀░░█▀█░█░█░█▀▄░█▀▀░█▀█
█▀▀░█░░░█▀█░█░█░█▀▀░▀▀█░░█░█░█▀▀░░█▀█░█░█░█▀▄░█▀▀░█░█
▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░░▀▀▀░▀░░░░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀
    """)
    draw_line()
    print("1. NEW GAME")
    print("2. LOAD GAME")
    print("3. QUIT GAME")
    choice = safe_input("# ")
    if choice == "1":
        return "new_game_menu"
    if choice == "2":
        return "load_game_menu"
    if choice == "3":
        return "exit"
    return "main_menu"  # Default: reload main menu


def handle_new_game_menu():
    # Handles the new game slot selection screen.
    clear_screen()
    draw_line()
    print("SELECT A SLOT FOR YOUR NEW GAME")
    draw_line()

    slot_info = []
    for i, slot_file in enumerate(SAVE_SLOTS, 1):
        info = get_save_slot_info(slot_file)
        slot_info.append(info)
        if info:
            print(f"{i}. [Lvl {info['level']}] {info['name']} (ATK: {info['atk']})")
            print(f"   Location: {info['location']}")
        else:
            print(f"{i}. [Empty Slot]")

    print("0. Back to Main Menu")
    draw_line()
    choice = safe_input("# ")

    if choice.strip().isdigit():
        slot_index = int(choice) - 1

        if choice == "0":
            return "main_menu", None  # Return state and player (None)

        if 0 <= slot_index < len(SAVE_SLOTS):
            selected_file = SAVE_SLOTS[slot_index]

            # Confirm overwrite if slot is not empty
            if slot_info[slot_index]:
                print(
                    f"\nWARNING: This will overwrite [Lvl {slot_info[slot_index]['level']}] {slot_info[slot_index]['name']}.")
                confirm = safe_input("Are you sure? (y/n): ").lower()
                if confirm != 'y':
                    return "new_game_menu", None  # Return to slot selection

            # Get player name and create new player
            clear_screen()
            name = safe_input("# What's your name, hero? ")
            if not name: name = "Wanderer"  # Default name

            player = create_new_player(name, selected_file)

            # Activate dev mode for specific names
            if name in ["Congchi Lee", "admin"]:
                player['dev_mode'] = True;
                print("\n*** Dev Mode Activated ***");
                time.sleep(1.2)

            show_lore()  # Show intro lore
            return "playing", player  # Start the game

    return "new_game_menu", None  # Invalid input, reload menu


def handle_load_game_menu():
    # Handles the load game slot selection screen.
    clear_screen()
    draw_line()
    print("SELECT A SLOT TO LOAD")
    draw_line()

    valid_slots = {}  # Maps display index (1, 2, 3) to filename
    slot_display_index = 1
    for slot_file in SAVE_SLOTS:
        info = get_save_slot_info(slot_file)
        if info:  # Only display non-empty slots
            print(f"{slot_display_index}. [Lvl {info['level']}] {info['name']} (ATK: {info['atk']})")
            print(f"   Location: {info['location']}")
            valid_slots[str(slot_display_index)] = slot_file
            slot_display_index += 1

    if not valid_slots:
        print("No saved games found.")

    print("0. Back to Main Menu")
    draw_line()
    choice = safe_input("# ")

    if choice == "0":
        return "main_menu", None  # Return state and player (None)

    if choice in valid_slots:
        selected_file = valid_slots[choice]
        player = load_game(selected_file)  # Attempt to load
        if player:
            return "playing", player  # Load successful, start game
        else:
            # load_game() prints error message
            time.sleep(1)
            return "load_game_menu", None  # Return to load menu on failure

    return "load_game_menu", None  # Invalid input, reload menu


def show_lore():
    # Displays the introductory lore sequence.
    clear_screen()
    draw_line()
    typewriter_effect(f"Echoes of {WORLD_NAME}", delay=0.04)
    draw_line()
    time.sleep(0.5)

    paragraphs = [
        f"There was once a land named {WORLD_NAME}...",
        "They lived with a flame the elders called the Breath of Dawn...",
        "It was not a fire that burned, but one that *remembered*.",
        "It held the shape of their songs, the weight of their promises, and the quiet joy of their long afternoons.",
        "But a shadow fell. A great, silent beast whose roar was not sound, but *forgetting*.",
        f"To save {WORLD_NAME}, the ancestors forged a Seal, sacrificing their own memories to bind the creature... and the Breath of Dawn with it.",
        "Now, the land is quiet. The fire is gone.",
        "All that remains... are echoes.",
        "Faint whispers of what was lost, clinging to stone and wind.",
        "The Seal is weakening. The echoes are growing restless, calling for someone to remember what the world forgot.",
        "You awaken to that call."
    ]

    for line in paragraphs:
        typewriter_effect(line, delay=0.03)
        time.sleep(0.6)
    draw_line()
    print()
    print("1 - Answer the call and begin your journey.")
    print("2 - Stay in the village (decline).")
    choice = safe_input("# ")
    if choice.strip() != "1":
        clear_screen()
        typewriter_effect("You turn away. The echo fades... but not forever.")
        safe_input("> Press Enter to change your mind.")
        show_lore()  # Recursive call to retry choice
    else:
        typewriter_effect("The wind carries your name. Auren remembers.")
        safe_input("\n> Press Enter to begin your quest.")


## MODIFIED (v1.7): Added new event ##
def handle_random_event(player):
    # Handles random encounters/events on the map.
    clear_screen()
    draw_line()
    title = f"An echo stirs across {WORLD_NAME}..."
    typewriter_effect(title)
    draw_line()
    events = ["shrine_prayer", "fallen_knight", "crimson_flower", "merchant_spirit", "mirror_echo"]

    # NEW (v1.7): Add event by region
    current_tile = MAP_DATA[player['y']][player['x']]
    if current_tile == "ruins":
        events.append("ruined_king")

    event = random.choice(events)

    if event == "shrine_prayer":
        typewriter_effect("You find a small, forgotten shrine, thick with moss.")
        typewriter_effect("A quiet melody seems to hang in the air.")
        print("1 - Kneel and listen")
        print("2 - Leave it be")
        choice = safe_input("# ")
        if choice.strip() == "1":
            typewriter_effect("You close your eyes. The song is of safety and stone.")
            player['hp'] = min(player['hp_max'], player['hp'] + 10)  # Heal
            print("(You healed 10 HP.)")
            player = codex_add(player, "shrine_memory")  # Add echo
    elif event == "fallen_knight":
        typewriter_effect("Beneath a withered tree lies a fallen knight...")
        typewriter_effect("Their armor is old, but their vow feels... new.")
        print("1 - Search their belongings")
        if player['pot'] > 0:
            print("2 - Leave a healing potion (1)")
        print("3 - Pay respects and leave")
        choice = safe_input("# ")
        if choice.strip() == "1":
            typewriter_effect("You find 15 Gold, but feel a pang of... something.")
            player['gold'] += 15
            player = codex_add(player, "fallen_knight")
        elif choice.strip() == "2" and player['pot'] > 0:
            typewriter_effect("You leave the potion. The air feels lighter.")
            player['pot'] -= 1
            player = codex_add(player, "fallen_knight")  # Still add echo for interaction
    elif event == "crimson_flower":
        typewriter_effect("A single, impossibly crimson flower grows on a rock.")
        print("1 - Pluck it")
        print("2 - Touch it")
        choice = safe_input("# ")
        if choice.strip() == "1":
            typewriter_effect("You pluck it. It turns to dust in your hand.")
            player['hp'] = max(1, player['hp'] - 5)  # Take minor damage
            print("(You lost 5 HP.)")
        elif choice.strip() == "2":
            typewriter_effect("You touch a petal. It feels like a fresh wound, but also a seed.")
            player = codex_add(player, "crimson_flower")
    elif event == "merchant_spirit":
        typewriter_effect("A small, lantern-eyed spirit appears on the path.")
        typewriter_effect("It holds out a single Elixir.")
        print("1 - 'I'll take it.' (50 Gold)")
        print("2 - 'No thank you.'")
        choice = safe_input("# ")
        if choice.strip() == "1" and player['gold'] >= 50:
            typewriter_effect("It smiles without lips and vanishes.")
            player['gold'] -= 50
            player['elix'] += 1
            player = codex_add(player, "merchant_spirit")
        elif choice.strip() == "1" and player['gold'] < 50:
            typewriter_effect("You can't afford it. It vanishes.")
        else:  # Chose 2 or invalid
            typewriter_effect("It vanishes.")
    elif event == "mirror_echo":
        typewriter_effect("You find a shard of a mirror.")
        typewriter_effect("Your reflection is... different. Stronger.")
        print("1 - Reach into the reflection")
        print("2 - Shatter the shard")
        choice = safe_input("# ")
        if choice.strip() == "1":
            typewriter_effect("Your hand meets... yourself. You feel a jolt of power.")
            player['bonus_atk'] = player.get('bonus_atk', 0) + 1  # Increase permanent bonus ATK
            player = recalculate_player_stats(player)  # Recalculate totals
            print(f"(You gained +1 Bonus ATK! Total ATK is now {player['total_atk']}!)")
            player = codex_add(player, "mirror_echo")
        else:  # Chose 2 or invalid
            typewriter_effect("You shatter the shard. The echo is gone.")

    elif event == "ruined_king":
        typewriter_effect("You find a tarnished, broken crown resting on a pile of rubble.")
        typewriter_effect("As you touch it, you feel a wave of immense sadness and authority.")
        print("1 - Take the memory")
        print("2 - Leave it in peace")
        choice = safe_input("# ")
        if choice.strip() == "1":
            typewriter_effect("You absorb the echo of the Fallen King.")
            player = codex_add(player, "ruined_king_memory")
        else:
            typewriter_effect("You back away slowly, leaving the crown to its rest.")

    safe_input("\n> Press Enter to continue...")
    return "playing", player  # Always return to playing state, updated player


# v1.8: REFACTORED to handle quest chains
def check_quest_completion(player, quest_type, target):
    # Checks if collecting an echo completes the current main quest objective.
    main_q_id = player.get('main_quest_id', '')
    main_q_data = MAIN_QUESTS.get(main_q_id, {})

    if not main_q_data: return player

    # Check if the quest type is COLLECT_ECHO, matches the target, and isn't already marked complete
    is_main_quest_objective = (main_q_data.get('type') == quest_type and
                               main_q_data.get('target_codex') == target and
                               main_q_id not in player['quest_progress'])

    if is_main_quest_objective:
        print(f"\nMain Quest Completed: {main_q_data.get('title')}")
        player['quest_progress'][main_q_id] = 1  # Mark as complete

        # Grant rewards (if any)
        reward_g = main_q_data.get('reward_gold', 0)
        reward_x = main_q_data.get('reward_xp', 0)
        if reward_g > 0 or reward_x > 0:
            player['gold'] += reward_g
            player['xp'] += reward_x
            print(f"Reward: {reward_g} Gold, {reward_x} XP!")
            player = handle_level_up(player)  # Check for level up

        # --- v1.8: Quest Chain Logic ---
        next_quest_id = None
        if main_q_id == "MQ_04":
            next_quest_id = "MQ_04_COMPLETE"
        elif main_q_id == "MQ_05_HERO_A":
            next_quest_id = "MQ_05_HERO_B"
        elif main_q_id == "MQ_05_HERO_B":
            next_quest_id = "MQ_05_HERO_C"
            player['quest_progress']["MQ_05_HERO_C"] = 0  # Initialize kill quest

        if next_quest_id:
            player['main_quest_id'] = next_quest_id
            print(f"Main Quest Updated! (Check Quest Log for details)")
        # --- End v1.8 Logic ---

        safe_input("> ")

    # Check side quests (v1.8: Farmer Quest)
    for q_id in player.get('active_side_quests', [])[:]:
        quest = SIDE_QUEST_POOL.get(q_id, {})
        if (quest.get('type') == quest_type and
                quest.get('target_codex') == target and
                player['quest_progress'].get(q_id, 0) == 0):  # Check if not already complete

            player['quest_progress'][q_id] = 1  # Mark as complete
            print(f"Side Quest: '{quest.get('title', 'Unknown')}' objective complete! Turn in.")
            safe_input("> ")

    return player


## MODIFIED (v1.6.4): Added Echo Focus menu, safe_input ##
def handle_town(player):
    # Handles interactions within the Town Centre.
    while True:
        clear_screen()
        draw_line()
        print("TOWN CENTRE - Auren")
        draw_line()
        print("You step into the town square. People move with practiced care.")
        draw_line()
        print("1 - Rest at the Inn (Full HP) - 15 Gold")
        print("2 - Visit the Quest Board")
        print("3 - Visit the Echo Guild")
        print("4 - Talk to the Locals")
        print("5 - Leave Town")
        draw_line()
        print(f"HP: {player['hp']}/{player['hp_max']} | GOLD: {player['gold']}")
        draw_line()
        choice = safe_input("# ")

        if choice.strip() == "1":  # Rest at Inn
            if player['gold'] >= 15:
                player['gold'] -= 15;
                player['hp'] = player['hp_max']  # Full heal
                # Clear negative status effects (dot, control)
                player['active_effects'] = [e for e in player.get('active_effects', []) if
                                            EFFECTS_DB.get(e['id'], {}).get('type') == 'hot']
                typewriter_effect("You sleep in a creaking bed. The world feels gentle.")
                print("(Negative status effects have been cleared.)")
                safe_input("> ")
            else:
                typewriter_effect("You lack the coin for the inn.")
                safe_input("> ")
        elif choice.strip() == "2":  # Quest Board
            player = handle_quest_board(player)
            # handle_quest_board now returns player, loop continues
        elif choice.strip() == "3":  # Echo Guild
            clear_screen()
            draw_line()
            print("ECHO GUILD - Archivist Lira")
            draw_line()
            typewriter_effect("'The echoes you gather... they mend what memory forgot,' Lira says softly.")
            draw_line()
            print("1 - Browse Echo Codex (Read Only)")
            print("2 - Ask Lira about the land (Quest)")
            print("3 - Focus on a Memory (Change Echo)")  # Option to change equipped echo
            print("4 - Return to Town Square")
            sub = safe_input("# ")

            if sub.strip() == "1":  # Read Codex
                show_codex(player)
                # show_codex returns None, loop continues


            elif sub.strip() == "2":  # Talk to Lira (Quests)
                main_q_id = player.get('main_quest_id')
                main_q_data = MAIN_QUESTS.get(main_q_id, {})
                # --- TUTORIAL (v1.7.1): Integrated Tutorial Logic ---
                if main_q_id == "MQ_02" and main_q_data.get('target') == "LIRA":
                    # --- TUTORIAL (PART 1: Give Echo) ---
                    if "ECHO_GIFT_01" not in player.get('codex', []):
                        typewriter_effect("'The Mayor sent you? Good. The echoes are restless.'")
                        typewriter_effect("'But you are not yet strong enough to hear them fully.'")
                        typewriter_effect("'To fight the echoes, you must use their own memories.'")
                        typewriter_effect(
                            "'Take this. It is 'The First Echo' that answered your call.'")
                        player = codex_add(player, "ECHO_GIFT_01")
                        print("\n(Lira gives you your first Echo!)")

                    # --- TUTORIAL (PART 2: Check Focus & Start Battle) ---
                    if player['equipped_echo'] == "ECHO_GIFT_01":
                        typewriter_effect(
                            "'Excellent. You feel the memory's power, yes? A faint boost to your strength?'")
                        typewriter_effect("'Now, you must prove your strength. A true test.'")
                        player['main_quest_id'] = "MQ_03"  # Advance quest
                        player['quest_progress']['MQ_03'] = 0  # Initialize progress
                        print("\n(Main Quest Updated!)")
                        safe_input("> ")
                        print("\n(Lira leads you to the training yard...)")
                        safe_input("> ")
                        # Trigger the tutorial battle
                        player = handle_tutorial_battle(player)
                        # After battle, Lira gives final words
                        clear_screen()
                        draw_line()
                        print("ECHO GUILD - Archivist Lira")
                        draw_line()
                        typewriter_effect("'Well done,' Lira says, nodding.")
                        typewriter_effect("'You have learned the basics. Now, go. Fulfill the quest.'")
                        typewriter_effect("'The Goblins are in the hills. Good luck.'")
                    else:  # Player hasn't focused the echo yet
                        typewriter_effect("'You have the memory, but you must *focus* it.'")
                        typewriter_effect("'Select option 3, 'Focus on a Memory', and choose the 'The First Echo'.'")
                        typewriter_effect("'Return to me once you have focused it.'")
                # --- END TUTORIAL LOGIC ---
                elif main_q_id == "MQ_03":
                    typewriter_effect("'You must prove your strength. The Goblins in the hills...'")
                elif main_q_id == "MQ_04":
                    typewriter_effect("'Find the Knight's Echo in the forest. It calls to you.'")
                # --- v1.8: Hero Path Quest Dialogue ---
                elif main_q_id == "MQ_05_HERO_A":
                    typewriter_effect(
                        "'You chose wisely. To master the seal, you must first master patience. Find the Shrine of Moss.'")
                elif main_q_id == "MQ_05_HERO_B":
                    typewriter_effect(
                        "'Good. Now, you must understand *why* the seal was made. Find the Cultist's Diary at the cave entrance.'")
                elif main_q_id == "MQ_05_HERO_C":
                    typewriter_effect(
                        "'You are ready. I have summoned a Sentinel in the hills. Prove your strength and wisdom.'")
                # --- End v1.8 ---
                else:  # Generic dialogue
                    typewriter_effect("Lira speaks: 'Collect enough, and Auren will remember.'")
                safe_input("> ")
            elif sub.strip() == "3":  # Focus Echo
                player = handle_echo_focus_menu(player)
                # handle_echo_focus_menu returns updated player, loop continues

            elif sub.strip() == "4":  # Return
                continue  # Go back to outer loop (Town Centre menu)
            # Implicit else: Invalid input, loop continues in Echo Guild menu

        elif choice.strip() == "4":  # Talk to Locals
            # v1.8: Dialogue changes based on world state
            lines = []
            if player['main_quest_id'] == "MQ_05_RECKLESS":
                lines = [
                    "'The sky... it feels wrong! What did you do at the cave?'",
                    "'Monsters are everywhere! The guards are overwhelmed! This is a nightmare...'",
                    "'The Mayor locked himself in his office. He looks terrified...'"
                ]
            elif player['main_quest_id'].startswith("MQ_05_HERO"):
                lines = [
                    "'We are all counting on you. Lira says you are taking the wise path.'",
                    "'The air feels tense, but stable. Thank you for your caution, traveler.'",
                ]
            else:
                lines = [
                    "An old woman whispers about a path behind the inn that glows at dusk.",
                    "Children play near the fountain, singing words that sound like an old hymn.",
                    "A blacksmith hums a tune that used to call warriors home."
                ]

            line = random.choice(lines)
            typewriter_effect(line)
            # Chance to gain the Town Rumor echo
            if random.random() < 0.30 and not player['main_quest_id'] == "MQ_05_RECKLESS":
                player = codex_add(player, "town_rumor")
            safe_input("> ")
        elif choice.strip() == "5":  # Leave Town
            return "playing", player, None  # Return state, player, and None (no enemy)
        # Implicit else: Invalid input, loop continues in Town Centre menu


## NEW (v1.6.4): Menu to change focused Echo, uses safe_input ##
def handle_echo_focus_menu(player):
    # Handles the menu for selecting the single focused Echo.
    while True:
        clear_screen()
        draw_line()
        print("FOCUS ON A MEMORY")
        draw_line()
        typewriter_effect("'Which memory... which part of Auren... do you wish to become?'", delay=0.02)
        draw_line()

        # Display currently focused echo
        print("--- CURRENTLY FOCUSED ---")
        current_echo_id = player.get('equipped_echo')
        if not current_echo_id:
            print("None. (Your mind is clear)")
        else:
            echo_name = CODEX_ENTRIES.get(current_echo_id, {}).get('title', 'Unknown')
            print(f"- {echo_name}")
        draw_line()

        # Display list of collected echoes to choose from
        print("--- CHOOSE A MEMORY TO FOCUS ON ---")
        collected_echoes = sorted(player.get('codex', []))  # Sort for consistent list order
        if not collected_echoes:
            print("You have not collected any memories to focus on.")
        else:
            for i, eid in enumerate(collected_echoes, 1):
                entry = CODEX_ENTRIES.get(eid, {})
                # Show buff summary for easier selection
                buff_text = ""
                if entry.get('buff'):
                    buff_text = f" (Buff: {entry['buff']})"
                # Add check for other effect types if needed in future
                print(f"[{i}] {entry.get('title', 'Unknown')}{buff_text}")

        draw_line()
        print("Enter number to Focus, '99' to Unfocus, or '0' to return.")
        choice = safe_input("# ")

        if choice == '0':
            return player  # Return updated player to caller (handle_town)

        elif choice == '99':  # Unfocus current echo
            if player['equipped_echo'] is None:
                print("You are already unfocused.")
            else:
                player['equipped_echo'] = None
                print("Memory unfocused. Your mind is clear.")
                player = recalculate_player_stats(player)  # Recalculate stats
            safe_input("> ")

        elif choice.strip().isdigit():  # Focus a new echo
            idx = int(choice.strip()) - 1
            if 0 <= idx < len(collected_echoes):
                eid_to_focus = collected_echoes[idx]

                if eid_to_focus == player['equipped_echo']:
                    print(f"You are already focusing on '{CODEX_ENTRIES[eid_to_focus]['title']}'.")
                else:
                    player['equipped_echo'] = eid_to_focus
                    print(f"You focus your mind on '{CODEX_ENTRIES[eid_to_focus]['title']}'.")
                    player = recalculate_player_stats(player)  # Recalculate stats
                safe_input("> ")
            else:
                print("Invalid number.")
                safe_input("> ")
        else:
            print("Invalid input.")
            safe_input("> ")
        # Loop continues to refresh the menu


def handle_quest_board(player):
    # Handles interactions with the Quest Board in town.
    while True:
        clear_screen()
        draw_line()
        print("QUEST BOARD")
        draw_line()
        player_level = player['level']

        # Check for completed quests
        completed_quests = []
        active_quests = player.get('active_side_quests', [])

        if active_quests:
            print("--- Active Bounties ---")
            for q_id in active_quests:
                quest = SIDE_QUEST_POOL.get(q_id)
                if not quest: continue
                progress = player['quest_progress'].get(q_id, 0)

                # Handle different quest types
                if quest.get('type') == 'KILL':
                    needed = quest.get('needed', 0)
                    print(f"> {quest.get('title', 'Unknown Quest')} ({progress}/{needed})")
                    if progress >= needed:
                        completed_quests.append(q_id)
                elif quest.get('type') == 'COLLECT_ECHO':  # v1.8: Handle Farmer Quest
                    needed = 1
                    print(f"> {quest.get('title', 'Unknown Quest')} ({progress}/{needed})")
                    if progress >= needed:
                        completed_quests.append(q_id)
        else:
            print("You have no active side quests.")

        draw_line()
        # Turn in completed quests
        if completed_quests:
            print("You have completed bounties to turn in!")
            for q_id in completed_quests:
                quest = SIDE_QUEST_POOL[q_id]
                typewriter_effect(f"Turning in: {quest.get('title', 'Unknown Quest')}...")
                reward_g = quest.get('reward_gold', 0)
                reward_x = quest.get('reward_xp', 0)
                player['gold'] += reward_g
                player['xp'] += reward_x
                print(f"Reward: {reward_g} Gold, {reward_x} XP!")

                player['active_side_quests'].remove(q_id)  # Remove from active list
                if q_id not in player.get('completed_side_quests', []):  # v1.8: Add to history
                    player.setdefault('completed_side_quests', []).append(q_id)
                if q_id in player['quest_progress']:
                    del player['quest_progress'][q_id]  # Clean up progress entry

            player = handle_level_up(player)  # Check level up after XP gain
            safe_input("\n> Press Enter to continue...")
            continue  # Refresh the board

        # Generate and display available quests
        print("--- Available Bounties ---")
        available_pool = []
        # v1.8: REFACTORED to filter quests
        for q_id, quest in SIDE_QUEST_POOL.items():
            if q_id in active_quests: continue  # Skip already active quests

            # --- v1.8: Quest Filtering Logic ---
            # 1. Skip non-board quests
            if quest.get("is_board_quest", True) == False:
                continue

            # 2. Check Exclusive Path
            quest_path = quest.get("exclusive_path")
            main_q = player['main_quest_id']

            if quest_path == "RECKLESS" and main_q != "MQ_05_RECKLESS":
                continue  # Skip if not on Reckless Path
            if quest_path == "HERO" and not main_q.startswith("MQ_05_HERO"):
                continue  # Skip if not on Hero Path
            # --- End v1.8 Logic ---

            quest_min_level = quest.get('min_level', 1)
            # Show quests appropriate for player level (within a range)
            if (player_level >= quest_min_level) and (player_level <= quest_min_level + 5):
                available_pool.append(q_id)

        # Handle cases where no quests are available or player has max quests
        if not available_pool or len(active_quests) >= 3:
            if len(active_quests) >= 3:
                print("Your hands are full. (Max 3 bounties)")
            else:
                print("No new bounties appropriate for your level right now.")
            print("\n0 - Back to Town")
            choice = safe_input("# ")
            if choice == "0": return player  # Return player to caller (handle_town)
            # Otherwise loop continues
        else:
            # Display available quests (up to 2)
            choices = random.sample(available_pool, k=min(len(available_pool), 2))
            for i, q_id in enumerate(choices, 1):
                quest = SIDE_QUEST_POOL[q_id]
                print(f"{i} - Accept: {quest.get('title', 'Unknown Quest')} (Lv. {quest.get('min_level', 1)})")
                print(f"    Reward: {quest.get('reward_gold', 0)} Gold, {quest.get('reward_xp', 0)} XP")
            print("0 - Back to Town")

            choice = safe_input("# ")
            if choice == "0": return player  # Return player to caller (handle_town)
            if choice.strip().isdigit() and 0 < int(choice) <= len(choices):
                q_id_to_accept = choices[int(choice) - 1]
                player['active_side_quests'].append(q_id_to_accept)
                player['quest_progress'][q_id_to_accept] = 0  # Initialize progress
                print(f"Accepted bounty: {SIDE_QUEST_POOL[q_id_to_accept]['title']}")
                safe_input("> ")
                continue  # Refresh the board after accepting
            # Invalid input, loop continues
        # Fallback return in case of unexpected flow
        return player


def handle_quest_log(player):
    # Displays the current main and side quests.
    clear_screen()
    draw_line()
    print("QUEST LOG")
    draw_line()

    # Display Main Quest
    print("--- Main Quest ---")
    main_q_id = player.get('main_quest_id', 'MQ_01')
    main_q_data = MAIN_QUESTS.get(main_q_id, {})
    if main_q_data:
        print(f"[{main_q_data.get('title', 'Unknown Quest')}]")
        print(f"> {main_q_data.get('desc', '...')}")

        q_type = main_q_data.get('type')
        if q_type == 'KILL':
            progress = player['quest_progress'].get(main_q_id, 0)
            needed = main_q_data.get('needed', 0)
            print(f"  Progress: ({progress}/{needed})")
        elif q_type == 'STAT_CHECK':
            print(f"  Level: {player['level']}/{main_q_data.get('target_level', 0)}")
            print(f"  ATK:   {player['total_atk']}/{main_q_data.get('target_atk', 0)}")
        elif q_type == 'COLLECT_ECHO':  # v1.8: Added
            progress = 1 if main_q_id in player['quest_progress'] else 0
            print(f"  Progress: ({progress}/1)")
    else:
        print("No active main quest.")

    draw_line()

    # Display Side Quests
    print("--- Side Quests (Bounties) ---")
    active_side_quests = player.get('active_side_quests', [])
    if not active_side_quests:
        print("No active side quests.")
        print("(Visit the Quest Board in Town or explore the world)")
    else:
        for q_id in active_side_quests:
            quest = SIDE_QUEST_POOL.get(q_id, {})
            progress = player['quest_progress'].get(q_id, 0)

            if quest.get('type') == 'KILL':
                needed = quest.get('needed', 0)
                print(f"> {quest.get('title', 'Unknown')} ({progress}/{needed})")
            elif quest.get('type') == 'COLLECT_ECHO':
                needed = 1
                print(f"> {quest.get('title', 'Unknown')} ({progress}/{needed})")
            else:
                print(f"> {quest.get('title', 'Unknown')} (In Progress)")

    draw_line()
    safe_input("> Press Enter to return...")
    return  # Return None, caller handles state


def handle_map_legend():
    # Displays the map legend.
    clear_screen()
    draw_line()
    print("MAP LEGEND")
    draw_line()
    print(f" {BIOME_ICONS.get('PLAYER', '@')} : You (Your Location)")
    print(f" {BIOME_ICONS.get('FOG', ' ')} : Fog (Unexplored)")
    print("\n--- Locations ---")
    print(f" {BIOME_ICONS.get('town', 'H')} : Town Centre / Mayor's Office")
    print(f" {BIOME_ICONS.get('shop', '$')} : Shop")
    print(f" {BIOME_ICONS.get('cave', '∩')} : Dragon's Cave")
    print("\n--- Terrain ---")
    print(f" {BIOME_ICONS.get('plains', '.')} : Plains")
    print(f" {BIOME_ICONS.get('fields', '~')} : Fields")
    print(f" {BIOME_ICONS.get('forest', 'T')} : Forest")
    print(f" {BIOME_ICONS.get('hills', 'n')} : Hills")
    print(f" {BIOME_ICONS.get('mountain', '▲')} : Mountain")
    print(f" {BIOME_ICONS.get('bridge', '=')} : Bridge")
    print(f" {BIOME_ICONS.get('swamp', 's')} : Murky Swamp")
    print(f" {BIOME_ICONS.get('ruins', 'R')} : Haunted Ruins")
    draw_line()
    safe_input("> Press Enter to return...")
    return  # Return None, caller handles state


def handle_help_menu():
    # Displays the How to Play / Help screen.
    clear_screen()
    draw_line()
    print("HOW TO PLAY / HELP")
    draw_line()
    print("\n--- 1. COMBAT BASICS ---")
    print("  ATK: Your Attack stat. Increases damage dealt.")
    print("  DEF: Your Defense stat. Reduces damage taken from regular attacks.")
    print("  GUARD (Skill): Reduces all damage taken for 1 turn by 50%.")
    print("  SKILL II: Upgraded skills (e.g., Focus Strike II) automatically replace")
    print("              the basic version when you reach the required level.")

    print("\n--- 2. STATUS EFFECTS (v1.8) ---")
    print("  POISON: Take damage every turn. Cured by Potion or Elixir.")
    print("  BURN  : Take damage every turn. Cured by Purify skill or Elixir.")
    print("  BLEED : Take damage every turn. Cured by Potion or Elixir.")
    print("  STUN  : Lose your next turn.")
    print("  SLEEP : Lose your next turn. Wakes up when hit.")
    print("  REGEN : Heal HP every turn.")
    print("  HARDENED: (Enemy) Reduces damage from the next hit by 50%.")
    print("  MANA DRAIN: (Player) Puts a random skill on cooldown.")

    print("\n--- 3. ECHOES & CODEX ---")
    print("  The Codex stores all 'Echoes' (memories) you find.")
    print("  Visit Lira at the Echo Guild to 'Focus on a Memory'.")
    print("  You can only Focus ONE Echo at a time.")
    print("  The Focused Echo provides powerful passive buffs (stats, effects).")

    print("\n--- 4. EXPLORATION ---")
    print("  Some locations on the map hide secrets. If you see an option like")
    print("  '7 - Examine...' try it to find new quests, echoes, or lore.")

    draw_line()
    safe_input("> Press Enter to return...")
    return


## MODIFIED (v1.6.4): Improved HP clamping for mobs ##
## MODIFIED (v1.8): Added BURN resistance logic ##
def process_status_effects(target, target_name):
    # Processes status effects (DOTs, HOTs, Control) for player or enemy.
    # Returns the updated target and a boolean indicating if stunned.
    if 'active_effects' not in target:
        target['active_effects'] = []
        return target, False  # Not stunned

    is_stunned = False

    # Iterate over a copy of the list to allow safe removal during iteration
    for effect in target.get('active_effects', [])[:]:
        effect_data = EFFECTS_DB.get(effect['id'])
        if not effect_data: continue  # Skip unknown effects

        effect_type = effect_data.get('type')

        if effect_type == "dot":  # Damage Over Time
            dmg = effect_data.get('value', 0)

            # --- v1.8: Refactored Burn Resistance ---
            if effect['id'] == 'BURN' and target_name == "You":
                resist_percent = 0.0
                if target.get('equipment', {}).get('armor') == 'EQ_A_004':
                    resist_percent = 0.5
                    print("(Your Acolyte's Robe resists some of the burn damage!)")
                elif target.get('equipped_echo') == 'dragon_cultist_diary':
                    resist_percent = 0.25
                    print("(Your echo of the Cultist's Diary dampens the flame!)")

                if resist_percent > 0.0:
                    dmg = int(dmg * (1.0 - resist_percent))
                    if dmg < 1: dmg = 1
            # --- End v1.8 ---

            target['hp'] -= dmg
            print(f"{target_name} {effect_data.get('msg_tick', 'takes damage.')}")

        elif effect_type == "hot":  # Heal Over Time
            heal = effect_data.get('value', 0)
            max_hp = target.get('hp_max', target['hp'] + heal)
            target['hp'] = min(max_hp, target['hp'] + heal)
            print(f"{target_name} {effect_data.get('msg_tick', 'heals.')}")

        elif effect['id'] == "MANA_DRAIN" and target_name == "You":
            print(f"Your energy is drained!")

        # Decrement turn counter
        effect['turns'] -= 1
        # Remove effect if duration runs out
        if effect['turns'] <= 0:
            target['active_effects'].remove(effect)
            print(f"{target_name} is no longer {effect_data.get('name', 'affected')}.")

    # Check for Stun/Sleep *after* processing other effects
    for effect in target.get('active_effects', []):
        if effect['id'] == "STUN" and EFFECTS_DB.get(effect['id'], {}).get('type') == 'control':
            print(f"{target_name} {EFFECTS_DB[effect['id']].get('msg_tick', 'is stunned!')}")
            is_stunned = True
            break
        if effect['id'] == "SLEEP" and EFFECTS_DB.get(effect['id'], {}).get('type') == 'control':  # v1.8
            print(f"{target_name} {EFFECTS_DB[effect['id']].get('msg_tick', 'is asleep!')}")
            is_stunned = True
            break

    return target, is_stunned


## MODIFIED (v1.6.4): Prevents duplicate effect stacking ##
## MODIFIED (v1.8): Added SLEEP echo logic ##
def apply_hit_effects(attacker, defender, attacker_name, defender_name):
    # Applies status effects from attacker (player or enemy) to defender.
    effects_to_try = []

    # Gather potential effects from Player (Weapon, Charm, Echo)
    if attacker_name == "You":
        wp_id = attacker['equipment'].get('weapon')
        if wp_id and 'effect_on_hit' in EQUIPMENT_DB.get(wp_id, {}):
            effects_to_try.append(EQUIPMENT_DB[wp_id]['effect_on_hit'])

        ch_id = attacker['equipment'].get('charm')
        if ch_id and 'effect_on_hit' in EQUIPMENT_DB.get(ch_id, {}):
            effects_to_try.append(EQUIPMENT_DB[ch_id]['effect_on_hit'])

        echo_id = attacker.get('equipped_echo')
        if echo_id and 'effect_on_hit' in CODEX_ENTRIES.get(echo_id, {}):
            effects_to_try.append(CODEX_ENTRIES[echo_id]['effect_on_hit'])

    # Gather potential effects from Enemy
    elif attacker_name != "You":
        for effect in attacker.get('effects', []):
            effects_to_try.append(effect)

    defender.setdefault('active_effects', [])
    applied_effect_ids = set()

    for eff in effects_to_try:
        effect_id = eff.get('id')
        if not effect_id: continue

        if random.random() < eff.get('chance', 0):

            if effect_id == "MANA_DRAIN" and defender_name == "You":
                print(f"The {attacker_name}'s attack drains your energy!")
                skills_to_drain = [s for s in defender.get('skills_cd', {}).keys() if
                                   s not in ["Focus Strike", "Guard"]]
                if not skills_to_drain: skills_to_drain = ["Meditate", "Limit Break"]
                skill_drained = random.choice(skills_to_drain)
                set_skill_cd(defender, skill_drained, eff.get('turns', 2))
                print(f"Your {skill_drained} skill is now on cooldown!")
                continue

            is_already_affected = False
            for active_eff in defender['active_effects']:
                if active_eff['id'] == effect_id:
                    active_eff['turns'] = max(active_eff.get('turns', 0), eff.get('turns', 0))
                    is_already_affected = True
                    break

            if not is_already_affected:
                defender['active_effects'].append({"id": effect_id, "turns": eff.get('turns', 1)})
                print(f"{defender_name} {EFFECTS_DB.get(effect_id, {}).get('msg_inflict', 'is affected!')}")

    return defender


## MODIFIED (v1.7): Added new mob skills ##
## MODIFIED (v1.8): Added Auren_Sentinel logic ##
def handle_enemy_turn(enemy, player, player_def):
    # Handles the enemy's turn in combat.
    enemy_name = enemy['name']

    # Process enemy's status effects (poison, stun etc.)
    enemy, is_stunned = process_status_effects(enemy, enemy_name)
    if enemy['hp'] <= 0:
        return enemy, player
    if is_stunned:
        time.sleep(1.2)
        return enemy, player

    if enemy.get('is_exhausted'):
        print(f"The {enemy_name} is exhausted and does nothing!")
        enemy['is_exhausted'] = False
        time.sleep(1.2)
        return enemy, player

    used_special = False

    ## NEW MOB SKILLS (v1.7) ##
    if enemy_name == "Skeleton" and not enemy.get('is_hardened') and random.randint(1, 100) <= 30:
        enemy['is_hardened'] = True;
        used_special = True
        print(
            f"The {enemy_name} assembles a Bone Shield! Its defense hardened! (Next physical hit is halved!)")  # v1.8: text

    elif enemy_name == "Ghost" and random.randint(1, 100) <= 25:
        used_special = True
        print(f"The {enemy_name} lets out a chilling wail, draining your spirit!")
        skills_to_drain = [s for s in player.get('skills_cd', {}).keys() if s not in ["Focus Strike", "Guard"]]
        if not skills_to_drain: skills_to_drain = ["Meditate", "Limit Break"]
        skill_drained = random.choice(skills_to_drain)
        set_skill_cd(player, skill_drained, 3)
        print(f"Your {skill_drained} skill is now on cooldown!")

    elif enemy_name == "Wraith" and random.randint(1, 100) <= 35:
        damage = max(1, int(enemy['atk'] * 1.2) - player_def)
        if player.get('guard'): damage = int(damage * 0.5)
        player['hp'] -= damage
        heal_amt = int(damage * 0.5)
        enemy['hp'] = min(enemy['hp_max'], enemy['hp'] + heal_amt)
        used_special = True
        print(f"The {enemy_name} uses Life Siphon! It dealt {damage} damage and healed {heal_amt} HP!")

    # --- v1.8: Auren_Sentinel Skill ---
    elif enemy_name == "Auren_Sentinel" and not enemy.get('is_hardened') and random.randint(1, 100) <= 35:
        enemy['is_hardened'] = True;
        used_special = True
        print(f"The {enemy_name} raises its shield! Its defense hardened! (Next physical hit is halved!)")
    # --- End v1.8 ---

    elif enemy_name == "Goblin Shaman" and enemy["hp"] <= (enemy["hp_max"] * 0.4) and random.randint(1, 100) <= 50:
        heal_amt = 15
        enemy["hp"] = min(enemy['hp_max'], enemy['hp'] + heal_amt)
        used_special = True
        print(f"The {enemy_name} chants wildly and heals for {heal_amt} HP!")

    elif enemy_name == "Slime" and enemy["hp"] <= 12 and random.randint(1, 100) <= 50:
        enemy["hp"] = min(enemy['hp_max'], enemy['hp'] + 5)
        used_special = True
        print(f"The {enemy_name} wobbles and regenerates for 5 HP!")
    elif enemy_name == "Goblin" and enemy["hp"] <= 5 and not enemy.get('has_raged'):
        enemy["atk"] += 2;
        enemy['has_raged'] = True;
        used_special = True
        print(f"The {enemy_name} flies into a rage! Its ATK increases by 2!")
    elif enemy_name == "Wolf" and random.randint(1, 100) <= 30:
        print(f"The {enemy_name} lunges forward with a swift strike!")
        used_special = True
        for _ in range(2):
            damage = max(1, int(enemy['atk'] * 0.75) - player_def)
            if player.get('guard'): damage = int(damage * 0.5)
            player['hp'] -= damage
            print(f"It hits you for {damage} damage!");
            time.sleep(0.6)
            if player['hp'] <= 0: break
    elif enemy_name == "Orc" and random.randint(1, 100) <= 40:
        damage = max(1, int(enemy['atk'] * 1.8) - player_def)
        if player.get('guard'): damage = int(damage * 0.5)
        player['hp'] -= damage
        enemy['is_exhausted'] = True;
        used_special = True
        print(f"The {enemy_name} delivers a brutal slam for {damage} damage!")
        print("It seems exhausted after that massive attack...")
    elif enemy_name == "Golem" and random.randint(1, 100) <= 30 and not enemy.get('is_hardened'):
        enemy['is_hardened'] = True;
        used_special = True
        print(
            f"The {enemy_name}'s stone body glows. It has hardened its defense! (Next physical hit is halved!)")  # v1.8: text
    elif enemy_name in ["Dragon", "Dragon_WorldBoss", "Fire Slime"] and random.randint(1, 100) <= 35:
        dmg_base = 15 if "Dragon" in enemy_name else 5
        if player.get('guard'): dmg_base = int(dmg_base * 0.5)
        damage = max(1, dmg_base - player_def)

        # v1.8: Refactored burn resist check
        resist_percent = 0.0
        if player.get('equipment', {}).get('armor') == 'EQ_A_004':
            resist_percent = 0.5
            print("(Your Acolyte's Robe resists some of the fire damage!)")
        elif player.get('equipped_echo') == 'dragon_cultist_diary':
            resist_percent = 0.25
            print("(Your echo of the Cultist's Diary dampens the flame!)")
        if resist_percent > 0.0:
            damage = int(damage * (1.0 - resist_percent))
            if damage < 1: damage = 1

        player['hp'] -= damage;
        used_special = True
        print(f"The {enemy_name} breathes FIRE! You take {damage} damage!")
    # --- End Special Attack Logic ---

    # Regular Attack
    if not used_special:
        if player.get('equipment', {}).get('charm') == 'EQ_C_004' and random.random() < 0.10:
            print(f"You evaded the {enemy_name}'s attack thanks to your Ghostly Pendant!")
        else:
            damage_dealt = max(1, enemy['atk'] - player_def)
            if player.get('guard'):
                damage_dealt = int(damage_dealt * 0.5)
            player['hp'] -= damage_dealt
            print(f"The {enemy_name} dealt {damage_dealt} damage to {player['name']}.")

            # v1.8: Wake up on hit
            for eff in player['active_effects'][:]:
                if eff['id'] == 'SLEEP':
                    player['active_effects'].remove(eff)
                    print("You were woken up by the attack!")

    # Apply on-hit effects
    player = apply_hit_effects(enemy, player, enemy_name, "You")

    player['guard'] = False
    time.sleep(1.2)
    player['hp'] = max(0, player['hp'])
    enemy['hp'] = max(0, enemy['hp'])
    return enemy, player


def game_over(player):
    # Handles the game over sequence. Returns updated player if respawning, None otherwise.
    print("\n────────────────────────────")
    time.sleep(1)
    print(" You fall to your knees...")
    time.sleep(1.5)
    print(" The light fades from your eyes.")
    time.sleep(1.5)
    print("\n Auren watches in silence.")
    time.sleep(2)

    codex_entries = len(player.get("codex", []))
    if codex_entries == 0:
        print("\n > 'The world barely remembers you.'")
    elif codex_entries < 3:
        print("\n > 'The world still remembers what you couldn’t finish.'")
    else:
        print("\n > 'Even in silence, your story will be remembered.'")

    print("\n────────────────────────────")
    time.sleep(2)
    print(" GAME OVER")
    print("────────────────────────────\n")
    time.sleep(2)

    if player.get("respawned", False):
        print(" The echoes fall silent. No light answers you this time.\n")
        time.sleep(2)
        print(" Your name fades forever into Auren.\n")
        time.sleep(2)
        return None

    while True:
        choice = safe_input("Do you wish to let the world forget you? (y/n): ").strip().lower()
        if choice == "y":
            print("\n The echo fades... completely.")
            time.sleep(2)
            return None
        elif choice == "n":
            print("\n A faint light remains...")
            time.sleep(2)
            player["hp"] = max(20, player["hp_max"] // 2)
            player["gold"] = player["gold"] // 2
            player["x"], player["y"] = 2, 3
            player["respawned"] = True
            player["active_effects"] = []
            print(" HP and Gold reduced by half.")
            print(" Returned to Town Centre.")
            print(" The world will not remember you again.\n")
            time.sleep(2)
            return player
        else:
            print(" Please choose y or n.")


## NEW (v1.7.1): Scripted tutorial battle function ##
def handle_tutorial_battle(player):
    """
    A scripted, step-by-step tutorial battle guided by Lira.
    """
    enemy = copy.deepcopy(MOBS["Tutorial_Dummy"])
    enemy['hp_max'] = enemy['hp']
    enemy['name'] = "Training Dummy"
    enemy.update({'active_effects': []})

    player['pot'] = max(1, player['pot'])

    temp_level_up = False
    if not skill_available(player, "Focus Strike"):
        player['level'] = 3
        temp_level_up = True
        print("(Lira temporarily grants you the memory of 'Focus Strike'!)")
        time.sleep(1.2)

    player = recalculate_player_stats(player)
    battle_atk, battle_def = player['total_atk'], player['total_def']
    player['hp'] = player['hp_max']

    tutorial_step = 1
    is_stunned = False

    while True:
        clear_screen();
        draw_line()
        print(f"TRAINING YARD - Defeat the {enemy['name']}");
        draw_line()
        print(f"{enemy['name']}'s HP: {enemy['hp']}/{enemy['hp_max']}")
        print(f"{player['name']}'s HP: {player['hp']}/{player['hp_max']}");
        draw_line()

        if tutorial_step == 1:
            typewriter_effect("Lira: 'This is a Training Dummy. First, let's practice a basic ATTACK.'", 0.02)
        elif tutorial_step == 2:
            typewriter_effect("Lira: 'Good. Now, let's try a SKILL. Skills are powerful but have cooldowns.'", 0.02)
        elif tutorial_step == 3:
            typewriter_effect("Lira: 'Well done. The dummy will hit back, but it's weak.'", 0.02)
            typewriter_effect("Lira: 'If you get low on HP, use a POTION. Try it now.'", 0.02)
        elif tutorial_step == 4:
            typewriter_effect("Lira: 'Excellent. You have learned the basics. Now, defeat the dummy.'", 0.02)

        draw_line()

        choice = ""
        if not is_stunned:
            if tutorial_step == 1:
                print("1 - ATTACK")
            elif tutorial_step == 2:
                print("S - USE SKILL (Focus Strike)")
            elif tutorial_step == 3:
                print(f"2 - USE POTION ({player['pot']} left)")
            elif tutorial_step >= 4:
                if skill_available(player, "Focus Strike"): print("S - USE SKILL")
                print("1 - ATTACK")
                if player['pot'] > 0: print(f"2 - USE POTION ({player['pot']} left)")

            draw_line();
            choice = safe_input("# ")

        action_taken = False
        if not is_stunned:
            if choice == "1" and tutorial_step in [1, 4]:  # Attack
                damage = battle_atk
                enemy['hp'] -= damage
                print(f"You dealt {damage} damage.")
                action_taken = True
                if tutorial_step == 1: tutorial_step = 2

            elif choice.upper() == "S" and tutorial_step in [2, 4]:  # Skill
                if skill_available(player, "Focus Strike"):
                    if skill_on_cooldown(player, "Focus Strike"):
                        print("Lira: 'That skill is on cooldown. Wait for it to recover.'")
                        time.sleep(1)
                    else:
                        damage = int(battle_atk * 1.8)
                        enemy['hp'] -= damage
                        set_skill_cd(player, "Focus Strike", 2)
                        print(f"You used Focus Strike for {damage} damage!")
                        action_taken = True
                        if tutorial_step == 2: tutorial_step = 3
                else:
                    print("Lira: 'You don't have that skill ready.'")
                    time.sleep(1)

            elif choice == "2" and player['pot'] > 0 and tutorial_step in [3, 4]:  # Use Potion
                player['pot'] -= 1;
                player['hp'] = min(player['hp_max'], player['hp'] + 25)
                print("HP refilled.")
                action_taken = True
                if tutorial_step == 3: tutorial_step = 4

            elif not choice:
                pass
            else:
                print("Lira: 'That's not the right action right now. Follow the instructions.'");
                time.sleep(1.2);
                continue

        if not action_taken and not is_stunned:
            continue

        time.sleep(1)

        if enemy['hp'] <= 0:
            print(f"You defeated the {enemy['name']}!")
            safe_input("> ")
            if temp_level_up:
                player['level'] = 1
                player = recalculate_player_stats(player)
            return player

        if tutorial_step > 2:
            damage_dealt = max(0, enemy['atk'] - battle_def)
            player['hp'] -= damage_dealt
            print(f"The {enemy['name']} hits you for {damage_dealt} damage.")
            time.sleep(1.2)

        if player['hp'] <= 0:
            print("Lira: 'Don't worry, this is just training.'")
            player['hp'] = player['hp_max']
            print("(You are fully healed.)")
            time.sleep(1)

        decrement_skill_cooldowns(player)


## MODIFIED (v1.7): Handles skill upgrades and new skills ##
## MODIFIED (v1.8): Handles Main Quest chain KILL quests ##
def handle_battle(player, enemy_name):
    # Main combat loop handler.
    enemy = copy.deepcopy(MOBS[enemy_name])
    enemy['hp_max'] = enemy['hp']
    enemy['name'] = enemy_name
    enemy.update({'is_hardened': False, 'is_exhausted': False, 'has_raged': False, 'active_effects': []})

    player = recalculate_player_stats(player)

    echo_id = player.get('equipped_echo')
    if echo_id:
        echo_data = CODEX_ENTRIES.get(echo_id, {})
        if 'combat_effect' in echo_data:
            eff = echo_data['combat_effect']
            is_already_affected = False
            for active_eff in player.get('active_effects', []):
                if active_eff['id'] == eff['id']:
                    is_already_affected = True
                    break
            if not is_already_affected:
                player.setdefault('active_effects', []).append(
                    {"id": eff['id'], "turns": eff.get('turns', 99)})
                print(f"Your focused memory ({echo_data.get('title', 'Unknown')}) activates {eff.get('id', '?')}!")
                time.sleep(1)

    battle_atk, battle_def = player['total_atk'], player['total_def']

    if player['active_buff']:
        clear_screen();
        draw_line()
        if player['active_buff'] == "rage":
            battle_atk += 5;
            print("The Rage Potion takes effect! ATK boosted!")
        elif player['active_buff'] == "stone":
            battle_def += 2;
            print("The Stone Skin Potion takes effect! DEF boosted!")
        player['active_buff'] = None
        draw_line();
        safe_input("> Press Enter to start...")

    # Main Battle Loop
    while True:
        clear_screen();
        draw_line()
        print(f"Defeat the {enemy_name}!");
        draw_line()

        # Display Enemy HP and Status Effects
        enemy_status = ""
        if enemy.get('active_effects'):
            enemy_status_list = [e['id'] for e in enemy['active_effects']]
            if enemy.get('is_hardened'): enemy_status_list.append("HARDENED")
            enemy_status = f" ({', '.join(enemy_status_list)})"
        elif enemy.get('is_hardened'):
            enemy_status = " (HARDENED)"
        print(f"{enemy_name}'s HP: {enemy['hp']}/{enemy['hp_max']}{enemy_status}")

        # Display Player HP and Status Effects
        player_status = ""
        if player.get('active_effects'):
            player_status = f" ({', '.join([e['id'] for e in player['active_effects']])})"
        print(f"{player['name']}'s HP: {player['hp']}/{player['hp_max']}{player_status}");
        draw_line()

        # --- PLAYER'S TURN ---
        player, is_stunned = process_status_effects(player, "You")
        if player['hp'] <= 0:
            player = game_over(player)
            if player is None: return "game_over", None
            return "playing", player

        choice = ""
        is_skipping = False
        if player.get('skip_next'):
            print("(You are focused — you will skip this turn to gather strength.)")
            player['skip_next'] = False
            is_skipping = True
        if is_stunned:
            print("You are stunned and cannot act!")
            time.sleep(1)
        elif is_skipping:
            print("(You are focused — you will skip this turn to gather strength.)")
            time.sleep(1)
        else:
            # Display Action Menu
            available_skills = []
            if skill_available(player, "Focus Strike II"):
                available_skills.append("Focus Strike II")
            elif skill_available(player, "Focus Strike"):
                available_skills.append("Focus Strike")

            if skill_available(player, "Guard II"):
                available_skills.append("Guard II")
            elif skill_available(player, "Guard"):
                available_skills.append("Guard")

            if skill_available(player, "Meditate II"):
                available_skills.append("Meditate II")
            elif skill_available(player, "Meditate"):
                available_skills.append("Meditate")

            if skill_available(player, "Limit Break"): available_skills.append("Limit Break")
            if skill_available(player, "Purify"): available_skills.append("Purify")
            if skill_available(player, "Reflected Strike"): available_skills.append("Reflected Strike")

            if available_skills: print("S - USE SKILL")
            print("1 - ATTACK")
            if player['pot'] > 0: print(f"2 - USE POTION ({player['pot']} left)")
            if player['elix'] > 0: print(f"3 - USE ELIXIR ({player['elix']} left)")
            draw_line();
            choice = safe_input("# ")

        # Execute Player Action
        if not is_stunned and not is_skipping:

            # v1.8: Remove SLEEP on hit
            is_woken_up = False
            for eff in enemy['active_effects'][:]:
                if eff['id'] == 'SLEEP':
                    enemy['active_effects'].remove(eff)
                    is_woken_up = True

            if choice == "1":  # Attack
                damage = battle_atk
                if enemy.get('is_hardened'):
                    print("Your attack clangs against the hardened body!")
                    damage = max(1, int(damage / 2));
                    enemy['is_hardened'] = False
                enemy['hp'] -= damage
                print(f"You dealt {damage} damage.")
                if is_woken_up: print(f"The {enemy_name} was woken up!")
                enemy = apply_hit_effects(player, enemy, "You", enemy_name)

            elif choice.upper() == "S":  # Use Skill
                clear_screen();
                draw_line();
                print("CHOOSE A SKILL");
                draw_line()
                skill_map = {}
                skill_idx = 1

                for skill_name in available_skills:
                    base_skill_name = skill_name.replace(" II", "")
                    cd = player.get('skills_cd', {}).get(base_skill_name, 0)

                    if cd > 0:
                        print(f"[X] {skill_name} (CD: {cd})")
                    elif skill_name == "Limit Break" and player['hp'] > (player['hp_max'] * 0.25):
                        print(f"[ ] Limit Break (Requires HP < 25%)")
                    else:
                        details = ""
                        if skill_name == "Focus Strike":
                            details = "(1.8x ATK, 2 Turn CD)"
                        elif skill_name == "Focus Strike II":
                            details = "(2.2x ATK, 2 Turn CD)"
                        elif skill_name == "Guard":
                            details = "(50% DMG Reduction, 3 Turn CD)"
                        elif skill_name == "Guard II":
                            details = "(50% DMG Reduction, 2 Turn CD)"
                        elif skill_name == "Meditate":
                            details = "(Heal 15% Max HP, 5 Turn CD)"
                        elif skill_name == "Meditate II":
                            details = "(Heal 25% Max HP, 4 Turn CD)"
                        elif skill_name == "Limit Break":
                            details = "(3.0x ATK, 6 Turn CD, HP < 25%)"
                        elif skill_name == "Reflected Strike":
                            details = "(1.2x ATK, Skip next, 3 Turn CD)"
                        elif skill_name == "Purify":
                            details = "(Cure POISON/BURN, 4 Turn CD)"

                        print(f"{skill_idx} - {skill_name} {details}")
                        skill_map[str(skill_idx)] = skill_name;
                        skill_idx += 1

                print("0 - Cancel")
                draw_line()
                skill_choice = safe_input("# ")

                if skill_choice == "0":
                    continue

                if skill_choice in skill_map:
                    skill_to_use = skill_map[skill_choice]
                    base_skill_name = skill_to_use.replace(" II", "")

                    if skill_to_use == "Focus Strike" or skill_to_use == "Focus Strike II":
                        multiplier = 2.2 if skill_to_use == "Focus Strike II" else 1.8
                        damage = int(battle_atk * multiplier)
                        if enemy.get('is_hardened'):
                            damage = max(1, int(damage / 2));
                            enemy['is_hardened'] = False
                        enemy['hp'] -= damage
                        set_skill_cd(player, base_skill_name, 2)
                        print(f"You used {skill_to_use} for {damage} damage!")
                        if is_woken_up: print(f"The {enemy_name} was woken up!")
                        enemy = apply_hit_effects(player, enemy, "You", enemy_name)

                    elif skill_to_use == "Guard" or skill_to_use == "Guard II":
                        cooldown = 2 if skill_to_use == "Guard II" else 3
                        player['guard'] = True
                        set_skill_cd(player, base_skill_name, cooldown)
                        print(f"You take a defensive stance.")

                    elif skill_to_use == "Meditate" or skill_to_use == "Meditate II":
                        percent = 0.25 if skill_to_use == "Meditate II" else 0.15
                        cooldown = 4 if skill_to_use == "Meditate II" else 5
                        heal_amt = int(player['hp_max'] * percent)
                        player['hp'] = min(player['hp_max'], player['hp'] + heal_amt)
                        set_skill_cd(player, base_skill_name, cooldown)
                        print(f"You focus your spirit and heal for {heal_amt} HP.")

                    elif skill_to_use == "Limit Break":
                        if player['hp'] > (player['hp_max'] * 0.25):
                            print("Your HP is too high to use Limit Break!")
                            print("(Requires HP < 25%)")
                            time.sleep(1.2)
                            continue
                        damage = int(battle_atk * 3.0)
                        if enemy.get('is_hardened'):
                            damage = max(1, int(damage / 2));
                            enemy['is_hardened'] = False
                        enemy['hp'] -= damage
                        set_skill_cd(player, base_skill_name, 6)
                        print(f"With desperate strength, you use Limit Break for {damage} damage!")
                        if is_woken_up: print(f"The {enemy_name} was woken up!")
                        enemy = apply_hit_effects(player, enemy, "You", enemy_name)

                    elif skill_to_use == "Reflected Strike":
                        damage = int(battle_atk * 1.2)
                        if enemy.get('is_hardened'):
                            damage = max(1, int(damage / 2));
                            enemy['is_hardened'] = False
                        enemy['hp'] -= damage
                        player['skip_next'] = True
                        set_skill_cd(player, base_skill_name, 3)
                        print(f"You used Reflected Strike for {damage} damage!")
                        print("You will skip your next turn to focus.")
                        if is_woken_up: print(f"The {enemy_name} was woken up!")
                        enemy = apply_hit_effects(player, enemy, "You", enemy_name)

                    elif skill_to_use == "Purify":
                        cured_effect_name = "None"
                        for eff in player['active_effects'][:]:
                            if eff['id'] == 'POISON' or eff['id'] == 'BURN':
                                player['active_effects'].remove(eff)
                                cured_effect_name = EFFECTS_DB.get(eff['id'], {}).get('name', eff['id'])
                                break
                        if cured_effect_name != "None":
                            print(f"You used Purify and cured {cured_effect_name}!")
                        else:
                            print("You used Purify, but had no Poison or Burn to cure.")
                        set_skill_cd(player, base_skill_name, 4)

                else:
                    print("Invalid skill choice.");
                    time.sleep(0.8);
                    continue

            elif choice == "2" and player['pot'] > 0:  # Use Potion
                player['pot'] -= 1;
                player['hp'] = min(player['hp_max'], player['hp'] + 25)
                cured_effects = []
                for eff in player['active_effects'][:]:
                    if eff['id'] == 'POISON' or eff['id'] == 'BLEED':  # v1.8: Cures bleed
                        player['active_effects'].remove(eff)
                        cured_effects.append(eff['id'])
                print("HP refilled.")
                if cured_effects: print(f"The potion cured your {', '.join(cured_effects)}!")
            elif choice == "3" and player['elix'] > 0:  # Use Elixir
                player['elix'] -= 1;
                player['hp'] = min(player['hp_max'], player['hp'] + 50)
                player['active_effects'] = [e for e in player['active_effects'] if
                                            EFFECTS_DB.get(e['id'], {}).get('type') == 'hot']
                print("HP refilled. All negative effects cured!")
            elif choice != "":
                print("Invalid input.");
                time.sleep(0.8);
                continue

        time.sleep(1)

        # Check for Enemy Defeat
        if enemy['hp'] <= 0:
            xp_gain = enemy.get('xp', 0)
            gold_bonus = player.get('gold_bonus', 0.0)
            base_gold = enemy.get('gold', 0)
            bonus_gold = int(base_gold * gold_bonus)
            gold_gain = base_gold + bonus_gold

            if player['level'] < 50:
                player['xp'] += xp_gain
                print(f"Gained {base_gold} gold (+{bonus_gold} bonus) and {xp_gain} XP!")
            else:
                print(f"Gained {base_gold} gold (+{bonus_gold} bonus) (Max level, no XP)")

            player['gold'] += gold_gain
            print(f"You defeated the {enemy_name}!")

            # Check for Loot Drops
            for item_id, chance in enemy.get('loot_table', {}).items():
                if random.random() < chance:
                    item_name = EQUIPMENT_DB.get(item_id, {}).get('name', 'Unknown Item')
                    player['inventory'].append(item_id)
                    print(f"The enemy dropped: {item_name}!")

            # Update Quest Progress
            # Main Quest
            main_q_id = player['main_quest_id']
            main_q_data = MAIN_QUESTS.get(main_q_id, {})
            if (main_q_data.get('type') == 'KILL' and
                    main_q_data.get('target_mob') == enemy_name):

                progress_key = main_q_id
                # v1.8: Handle chain quest progress
                if main_q_id.startswith("MQ_05_HERO"):
                    progress_key = "MQ_05_HERO_C"  # All hero kills track under C

                progress = player['quest_progress'].get(progress_key, 0) + 1
                player['quest_progress'][progress_key] = progress
                print(f"Main Quest: {progress}/{main_q_data.get('needed', 1)} {enemy_name} defeated.")

                if progress >= main_q_data.get('needed', 1):
                    if main_q_id == "MQ_03":
                        player['main_quest_id'] = "MQ_04"
                        print("Main Quest Updated! Return to Lira.")
                    # --- v1.8: Hero Quest Chain ---
                    elif main_q_id == "MQ_05_HERO_C":
                        player['seal'] = False  # BREAK THE SEAL
                        player['main_quest_id'] = "MQ_06_HERO"
                        print("You feel a great shift. The seal has been safely undone!")
                        print("Main Quest Updated! Confront the Dragon!")
                    # --- End v1.S ---

            # Side Quests
            for q_id in player.get('active_side_quests', [])[:]:
                quest = SIDE_QUEST_POOL.get(q_id, {})
                if (quest.get('type') == 'KILL' and
                        quest.get('target_mob') == enemy_name and
                        player['quest_progress'].get(q_id, 0) < quest.get('needed', 0)):
                    progress = player['quest_progress'].get(q_id, 0) + 1
                    player['quest_progress'][q_id] = progress
                    print(f"Side Quest: {progress}/{quest.get('needed', 1)} {enemy_name} defeated.")
                    if progress >= quest.get('needed', 1):
                        print(f"Side Quest '{quest.get('title', 'Unknown')}' complete! Turn in at the Quest Board.")

            player = handle_level_up(player)

            if random.randint(1, 100) <= 30:
                player['pot'] += 1;
                print("You found a potion!")

            safe_input("> ")

            if enemy_name == "Dragon" or enemy_name == "Dragon_WorldBoss":
                return "game_won", player

            return "playing", player

        # --- ENEMY'S TURN ---
        enemy, player = handle_enemy_turn(enemy, player, battle_def)
        if player['hp'] <= 0:
            player = game_over(player)
            if player is None: return "game_over", None
            return "playing", player

        decrement_skill_cooldowns(player)


## MODIFIED (v1.6.4): Uses safe_input, clearer feedback ##
def handle_shop(player):
    # Handles interactions within the shop.
    while True:
        clear_screen()
        draw_line();
        print("Welcome to the shop!");
        draw_line()
        print(f"GOLD: {player['gold']} | ATK: {player['total_atk']} | DEF: {player['total_def']}");
        draw_line()
        print("--- Consumables ---")
        print(f"1 - BUY POTION (25HP, Cures Poison/Bleed) - 15 GOLD ({player['pot']} owned)")  # v1.8: Desc
        print(f"2 - BUY ELIXIR (50HP, Cures All)      - 25 GOLD ({player['elix']} owned)")
        print(f"3 - BUY RAGE POTION (+5 ATK next battle) - 40 GOLD ({player['rage_potions']} owned)")
        print(f"4 - BUY STONE SKIN POTION (+2 DEF next battle) - 35 GOLD ({player['stone_potions']} owned)")
        draw_line()
        print("--- Equipment ---")
        print(f"5 - BUY Poison Dagger (+1 ATK, 30% Poison) - 75 GOLD")
        print(f"6 - BUY Chainmail Vest (+3 DEF) - 100 GOLD")
        print(f"7 - BUY Lucky Coin (+10% Gold Bonus) - 120 GOLD")

        # Calculate scaling upgrade cost
        upgrade_level = (player['base_atk'] - 3)
        upgrade_cost = 50 + (upgrade_level * 25)
        print(f"8 - UPGRADE WEAPON (+1 Base ATK) - {upgrade_cost} GOLD")
        print("9 - LEAVE")
        draw_line();
        choice = safe_input("# ")

        action_taken = False
        if choice == "1" and player['gold'] >= 15:
            player['gold'] -= 15;
            player['pot'] += 1;
            action_taken = True
            print("Bought 1 Potion.")
        elif choice == "2" and player['gold'] >= 25:
            player['gold'] -= 25;
            player['elix'] += 1;
            action_taken = True
            print("Bought 1 Elixir.")
        elif choice == "3" and player['gold'] >= 40:
            player['gold'] -= 40;
            player['rage_potions'] += 1;
            action_taken = True
            print("Bought 1 Rage Potion.")
        elif choice == "4" and player['gold'] >= 35:
            player['gold'] -= 35;
            player['stone_potions'] += 1;
            action_taken = True
            print("Bought 1 Stone Skin Potion.")

        elif choice == "5" and player['gold'] >= 75:
            player['gold'] -= 75;
            player['inventory'].append("EQ_W_003");
            action_taken = True
            print("Bought Poison Dagger!")
        elif choice == "6" and player['gold'] >= 100:
            player['gold'] -= 100;
            player['inventory'].append("EQ_A_002");
            action_taken = True
            print("Bought Chainmail Vest!")
        elif choice == "7" and player['gold'] >= 120:
            player['gold'] -= 120;
            player['inventory'].append("EQ_C_003");
            action_taken = True
            print("Bought Lucky Coin!")

        elif choice == "8" and player['gold'] >= upgrade_cost:
            player['gold'] -= upgrade_cost;
            player['base_atk'] += 1
            player = recalculate_player_stats(player)
            print(f"Base ATK permanently increased to {player['base_atk']}!")
            action_taken = True
        elif choice == "9":
            return "playing", player, None

        if not action_taken and choice != '9':
            print("Not enough gold or invalid choice!");

        if action_taken or choice != '9':
            safe_input("> ")


def handle_mayor(player):
    # Handles interactions with the Mayor.
    main_q_id = player.get('main_quest_id')
    main_q_data = MAIN_QUESTS.get(main_q_id, {})

    while True:
        clear_screen()
        draw_line()
        print(f"Hello there, {player['name']}!")
        draw_line()

        # Check for the "Fateful Choice" quest state
        if main_q_id == "MQ_04_COMPLETE" and player['seal']:
            if player['total_atk'] >= 10:
                typewriter_effect("'You are stronger,' the Mayor says, 'But... still not enough.'")
                typewriter_effect("'The seal is weakening. We have two choices:'")
                draw_line()
                print(
                    "1 - 'Wait. Train as Lira advised (Lvl 10 / ATK 20 Total) to break the seal safely.' (The Hero's Path)")
                print(
                    "2 - 'Or, I have an ancient key... We can force the seal NOW! The risk is... unknown.' (The Reckless Path)")
                draw_line()
                choice = safe_input("# ")

                if choice == "1":
                    player['main_quest_id'] = "MQ_05_HERO_A"  # v1.8: Start Hero Chain
                    player['quest_progress']['MQ_05_HERO_A'] = 0  # Init progress
                    typewriter_effect("'A wise choice. Speak to Lira. She will guide your training.'")
                    safe_input("> ")
                    return "playing", player, None
                elif choice == "2":
                    player['key'] = True
                    player['seal'] = False
                    player['main_quest_id'] = "MQ_05_RECKLESS"
                    player['quest_progress']['MQ_05_RECKLESS'] = 0  # Init progress
                    typewriter_effect("'May Auren forgive us... The seal is forced!'")
                    typewriter_effect("You hear an enraged roar echo across the world...")
                    safe_input("> ")
                    return "playing", player, None
                else:
                    continue
            else:
                typewriter_effect("'You have returned... but your echo is still weak,' the Mayor says.")
                typewriter_effect(
                    f"'I cannot offer you this choice until you are stronger (Current ATK: {player['total_atk']}/10).'")
                typewriter_effect("'Continue your training.'")

        elif main_q_id == "MQ_01" and main_q_data.get('target') == "town":
            typewriter_effect("'Thank goodness you're here,' the Mayor says, his face grim.")
            typewriter_effect("'The echoes... they're growing stronger. The seal is weakening.'")
            player['main_quest_id'] = "MQ_02"
            print("\n(Main Quest Updated!)")
            safe_input("> ")
            continue

        elif not player['seal']:
            if player['key']:
                typewriter_effect("'The seal is broken... The dragon has escaped! You must find it!'")
            else:
                typewriter_effect("'The seal is safely broken. Go to the cave! Auren is counting on you!'")

        # v1.8: Hero Path dialogue
        elif main_q_id.startswith("MQ_05_HERO"):
            typewriter_effect("'Speak to Lira at the Guild. She is guiding your path now. Be safe.'")

        else:
            typewriter_effect("'Continue your training, adventurer. Talk to Lira at the Guild.'")

        draw_line()
        print("1 - LEAVE")
        draw_line()
        choice = safe_input("# ")
        if choice == "1": return "playing", player, None


def handle_cave(player):
    # Handles interactions at the Dragon's Cave entrance.
    while True:
        clear_screen()
        draw_line()

        if player['seal']:
            typewriter_effect("A massive, glowing seal bars the cave entrance.")
            typewriter_effect("It hums with ancient power. You are not yet strong enough.")
            draw_line()
            print("1 - TURN BACK")
            # v1.8: Check for interactable
            if "dragon_cultist_diary" not in player.get('codex', []):
                print("7 - Examine the strange markings")
            draw_line()
            choice = safe_input("# ")
            if choice == "1":
                return "playing", player, None
            # v1.8: Handle interactable
            elif choice == "7" and "dragon_cultist_diary" not in player.get('codex', []):
                typewriter_effect("You find a charred piece of parchment tucked into the rock...")
                player = codex_add(player, "dragon_cultist_diary")
                safe_input("> ")
                continue  # Refresh cave menu

        else:
            if player['key']:
                typewriter_effect("The seal is shattered... but the cave is empty.")
                typewriter_effect("A cold wind blows from the darkness. The dragon has escaped.")
                draw_line()
                print("1 - TURN BACK")
                draw_line()
                choice = safe_input("# ")
                if choice == "1": return "playing", player, None

            else:
                typewriter_effect("The seal has vanished. The path is open.")
                typewriter_effect("You hear a hateful roar from within the darkness.")
                draw_line()
                print("1 - ENTER THE LAIR (Fight Dragon)")
                print("2 - TURN BACK")
                draw_line()
                choice = safe_input("# ")
                if choice == "1":
                    return "battle", player, "Dragon"
                elif choice == "2":
                    return "playing", player, None


def handle_debug_console(player):
    # Provides a debug menu for testing (if dev_mode is enabled).
    while True:
        clear_screen()
        draw_line();
        print("    DEVELOPER CONSOLE (v1.8)");
        draw_line()
        print(
            f"HP:{player['hp']}/{player['hp_max']} | ATK:{player['total_atk']} (Base:{player['base_atk']}+B{player.get('bonus_atk', 0)}) | DEF:{player['total_def']} (Base:{player['base_def']}+B{player.get('bonus_def', 0)})")
        print(f"LVL:{player['level']} | XP:{player['xp']}/{player['xp_to_next_level']}")
        print(
            f"POS: ({player['x']}, {player['y']}) | Seal: {'Intact' if player['seal'] else 'Broken'} | Key: {player['key']}")
        print(f"Main Quest: {player['main_quest_id']} | Gold: {player['gold']}")
        print(f"Focused Echo: {player['equipped_echo']}")
        print(f"Completed SQs: {player.get('completed_side_quests', [])}")
        draw_line()
        print(
            "1. Add 1000 Gold\n2. Add 500 XP\n3. Add 1 Bonus ATK\n4. Heal to Full HP\n5. Get All Items & Echoes\n6. Toggle Dragon Seal\n7. Teleport (TOWN)\n0. Exit Console")
        draw_line();
        choice = safe_input("# ")

        action_taken = True
        if choice == "1":
            player['gold'] += 1000
        elif choice == "2":
            player['xp'] += 500;
            player = handle_level_up(player)
        elif choice == "3":
            player['bonus_atk'] = player.get('bonus_atk', 0) + 1
            player = recalculate_player_stats(player)
        elif choice == "4":
            player['hp'] = player['hp_max']
        elif choice == "5":
            player['pot'] += 10
            for item_id in EQUIPMENT_DB.keys():
                if item_id not in player['inventory']:
                    player['inventory'].append(item_id)
            for echo_id in CODEX_ENTRIES.keys():
                player = codex_add(player, echo_id)
        elif choice == "6":
            player['seal'] = not player['seal']
        elif choice == "7":
            player['x'], player['y'] = 2, 3
        elif choice == "0":
            return "playing", player, None
        else:
            action_taken = False
            print("Invalid command.")

        if action_taken:
            print("Debug command executed.")
        safe_input("\n> Press Enter to continue...")


def handle_game_over():
    # Final screen after player chooses not to respawn or dies permanently.
    clear_screen()
    draw_line()
    print("GAME OVER")
    draw_line()
    safe_input("> Press Enter to return to the Main Menu...")
    return "main_menu"


def handle_game_won(player):
    # Screen displayed after defeating the final boss.
    clear_screen()
    draw_line()
    typewriter_effect("With a final, earth-shattering roar, the mighty Dragon falls.")
    time.sleep(1)
    typewriter_effect("Silence descends upon the land...")
    time.sleep(1.5)

    if player.get('key'):
        typewriter_effect("The roar of *forgetting* is gone, but the world remains... quiet.")
        typewriter_effect("You have saved Auren from the beast, but the echoes remain scattered.")
        typewriter_effect("The Breath of Dawn... is still lost.")
    else:
        typewriter_effect("A faint warmth returns to the air. The Breath of Dawn stirs.")
        typewriter_effect("The echoes begin to sing, their memories mended by your strength.")
        typewriter_effect(f"{WORLD_NAME} remembers.")

    print()
    typewriter_effect(f"Your name, {player['name']}, will be sung by bards for generations.")
    typewriter_effect("Congratulations, hero. You have won.")
    draw_line()
    safe_input("> Press Enter to return to the Main Menu...")
    return "main_menu"


## MODIFIED (v1.6.4): Uses safe_input, clearer options ##
def handle_equipment_menu(player):
    # Handles the equipment management screen.
    while True:
        clear_screen()
        draw_line()
        print("EQUIPMENT & INVENTORY")
        draw_line()
        print(f"ATK: {player['total_atk']} | DEF: {player['total_def']} | HP: {player['hp']}/{player['hp_max']}")
        draw_line()

        # Display equipped items
        print("--- EQUIPPED ---")
        wp_id = player['equipment']['weapon']
        ar_id = player['equipment']['armor']
        ch_id = player['equipment']['charm']

        wp_name = EQUIPMENT_DB.get(wp_id, {}).get('name', 'None')
        ar_name = EQUIPMENT_DB.get(ar_id, {}).get('name', 'None')
        ch_name = EQUIPMENT_DB.get(ch_id, {}).get('name', 'None')

        print(f"a. Weapon: {wp_name}")
        print(f"b. Armor : {ar_name}")
        print(f"c. Charm : {ch_name}")
        draw_line()

        # Display inventory items with numbers
        print("--- INVENTORY ---")
        if not player['inventory']:
            print("Your inventory is empty.")
        else:
            # Sort inventory by type, then name
            sorted_inventory = sorted(player['inventory'], key=lambda item_id: (
                EQUIPMENT_DB.get(item_id, {}).get('type', 'z'),
                EQUIPMENT_DB.get(item_id, {}).get('name', 'Unknown')
            ))
            player['inventory'] = sorted_inventory

            for i, item_id in enumerate(player['inventory'], 1):
                item = EQUIPMENT_DB.get(item_id, {})
                stats = item.get('stats', {})
                print(f"{i}. {item.get('name', 'Unknown')} [{item.get('type', '?')}] (Stats: {stats})")

        draw_line()
        print("Enter number to Equip, letter (a,b,c) to Unequip, or '0' to return.")
        choice = safe_input("# ").lower()

        if choice == '0':
            return player

        # Handle Unequip action
        elif choice in ['a', 'b', 'c']:
            slot_to_unequip = None
            if choice == 'a':
                slot_to_unequip = 'weapon'
            elif choice == 'b':
                slot_to_unequip = 'armor'
            elif choice == 'c':
                slot_to_unequip = 'charm'

            item_id_to_unequip = player['equipment'].get(slot_to_unequip)
            if item_id_to_unequip:
                item_name = EQUIPMENT_DB.get(item_id_to_unequip, {}).get('name', 'Item')
                player['equipment'][slot_to_unequip] = None
                player['inventory'].append(item_id_to_unequip)
                player = recalculate_player_stats(player)
                print(f"Unequipped {item_name}.")
                safe_input("> ")
            else:
                print("That slot is already empty.")
                safe_input("> ")

        # Handle Equip action
        elif choice.strip().isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(player['inventory']):
                item_id_to_equip = player['inventory'][idx]
                item_data = EQUIPMENT_DB[item_id_to_equip]
                item_type = item_data['type']

                current_equipped_id = player['equipment'].get(item_type)
                if current_equipped_id:
                    player['inventory'].append(current_equipped_id)

                player['equipment'][item_type] = item_id_to_equip
                player['inventory'].pop(idx)

                print(f"Equipped {item_data.get('name', 'Item')}.")
                player = recalculate_player_stats(player)
                safe_input("> ")
            else:
                print("Invalid item number.")
                safe_input("> ")
        else:
            print("Invalid input.")
            safe_input("> ")


## MODIFIED (v1.6.4): Displays more stats, handles safe_input, returns tuple ##
## MODIFIED (v1.8): Handles interactables and world-changing spawns ##
def handle_playing(player):
    # Main game screen handler (map view).
    y_len, x_len = len(MAP_DATA) - 1, len(MAP_DATA[0]) - 1

    if player['y'] > y_len or player['x'] > x_len:
        player['x'], player['y'] = 2, 3

    current_tile = MAP_DATA[player['y']][player['x']]
    standing = True

    if player['main_quest_id'] == "MQ_01" and player['x'] == 2 and player['y'] == 3:
        player['main_quest_id'] = "MQ_02"

    clear_screen()

    player, _ = process_status_effects(player, "You")
    if player['hp'] <= 0:
        player = game_over(player)
        if player is None: return "game_over", None, None
        return "playing", player, None

    draw_line()
    draw_minimap(player)
    show_biome_flavor(player)
    draw_line()
    print("LOCATION: " + BIOMES[current_tile].get("t", "Unknown"))
    draw_line()
    print(f"NAME: {player['name']} | Lv: {player['level']}")
    print(f"HP: {player['hp']}/{player['hp_max']} | ATK: {player['total_atk']} | DEF: {player['total_def']}")

    player_status = ""
    if player.get('active_effects'):
        player_status = f" ({', '.join([e['id'] for e in player['active_effects']])})"
    print(f"XP: {player['xp']}/{player['xp_to_next_level']}{player_status}")

    focused_echo_name = "None"
    if player.get('equipped_echo'):
        focused_echo_name = CODEX_ENTRIES.get(player['equipped_echo'], {}).get('title', 'Unknown')
    print(f"FOCUSED ECHO: {focused_echo_name}")

    print(f"GOLD: {player['gold']}")
    draw_line()

    # Display Action Menu
    print("0 - SAVE AND QUIT")
    if player['y'] > 0: print("1 - NORTH (↑)")
    if player['x'] < x_len: print("2 - EAST (→)")
    if player['y'] < y_len: print("3 - SOUTH (↓)")
    if player['x'] > 0: print("4 - WEST (←)")
    if player['pot'] > 0: print(f"5 - USE HEAL POTION ({player['pot']} left)")
    if player['elix'] > 0: print(f"6 - USE ELIXIR ({player['elix']} left)")

    # --- v1.8: Interactable Logic (Display) ---
    interact_text = None
    px, py = player['x'], player['y']
    codex = player.get('codex', [])

    if current_tile in ["shop", "mayor", "cave", "town"]:
        interact_text = "7 - ENTER"
    elif px == 1 and py == 2:  # Fields (1,2)
        if "farmer_memory" not in codex:
            interact_text = "7 - Examine the abandoned plow"
        elif "SQ_FARMER_01" not in player.get('active_side_quests', []) and "SQ_FARMER_01" not in player.get(
                'completed_side_quests', []):
            interact_text = "7 - Talk to the farmer"
        else:
            interact_text = "7 - Greet the farmer"

    elif px == 6 and py == 0 and "dragon_cultist_diary" not in codex and player['seal']:  # Cave Entrance (6,0)
        interact_text = "7 - Examine the strange markings"

    if interact_text:
        print(interact_text)
    # --- End v1.8 Logic ---

    if player['rage_potions'] > 0: print(f"8 - USE RAGE POTION ({player['rage_potions']} left)")
    if player['stone_potions'] > 0: print(f"9 - USE STONE SKIN POTION ({player['stone_potions']} left)")
    print("10 - READ ECHO CODEX (Read Only)")
    print("11 - VIEW QUEST LOG")
    print("12 - MAP LEGEND")
    print("13 - VIEW EQUIPMENT")
    print("14 - HOW TO PLAY/HELP")
    if player.get('dev_mode'): print("dev - DEV CONSOLE")
    draw_line()

    if player['active_buff']:
        print(f"Active Buff for next battle: {player['active_buff'].upper()}!")
        draw_line()

    # v1.8: REMOVED auto-complete logic, handled by KILL quest now
    main_q_id = player.get('main_quest_id')
    # if (main_q_id == "MQ_05_HERO" and player['total_atk'] >= 20 and ...

    dest = safe_input("# ")

    next_state = "playing"
    enemy_to_fight = None

    if dest == "0":
        save_game(player);
        next_state = "main_menu"
    elif dest in ["1", "2", "3", "4"]:
        moved = False
        if dest == "1" and player['y'] > 0:
            player['y'] -= 1;
            moved = True
        elif dest == "2" and player['x'] < x_len:
            player['x'] += 1;
            moved = True
        elif dest == "3" and player['y'] < y_len:
            player['y'] += 1;
            moved = True
        elif dest == "4" and player['x'] > 0:
            player['x'] -= 1;
            moved = True
        else:
            print("You cannot move that way.")
            time.sleep(1)
            standing = True

        if moved:
            standing = False
            current_tile = MAP_DATA[player['y']][player['x']]

    elif dest == "5" and player['pot'] > 0:
        player['pot'] -= 1;
        player['hp'] = min(player['hp_max'], player['hp'] + 25)
        cured_effects = []
        for eff in player['active_effects'][:]:
            if eff['id'] == 'POISON' or eff['id'] == 'BLEED':  # v1.8: Cures bleed
                player['active_effects'].remove(eff)
                cured_effects.append(eff['id'])
        print("HP refilled!");
        if cured_effects: print(f"The potion cured your {', '.join(cured_effects)}!")
        safe_input("> ")
    elif dest == "6" and player['elix'] > 0:
        player['elix'] -= 1;
        player['hp'] = min(player['hp_max'], player['hp'] + 50)
        player['active_effects'] = [e for e in player['active_effects'] if
        EFFECTS_DB.get(e.get('id'), {}).get('type') == 'hot']
        print("HP refilled. All negative effects cured!");
        safe_input("> ")
    elif dest == "7":
        px, py = player['x'], player['y']
        codex = player.get('codex', [])

        # Original Enter Logic
        if current_tile == "shop":
            next_state = "shop"
        elif current_tile == "mayor":
            next_state = "mayor"
        elif current_tile == "cave":
            next_state = "cave"
        elif current_tile == "town":
            next_state = "town"

        # --- v1.8: Interactable Logic (Action) ---
        elif px == 1 and py == 2:  # Fields (1,2)
            if "farmer_memory" not in codex:
                typewriter_effect("You touch an old plow. A memory of cold earth and hunger surfaces...")
                player = codex_add(player, "farmer_memory")
                safe_input("> ")
            elif "SQ_FARMER_01" not in player.get('active_side_quests', []) and "SQ_FARMER_01" not in player.get(
                    'completed_side_quests', []):
                typewriter_effect("An old farmer approaches you, his eyes weary.")
                typewriter_effect(
                    "'You... you can feel the echoes, can't you? Please... my grandchildren, they can't sleep. They need the 'Ancient Lullaby'.'")
                typewriter_effect(
                    "'I heard a Merchant Spirit... one of those echo-traders... was humming it in the woods.'")
                print("\n(New Side Quest accepted: The Lost Lullaby!)")
                player.setdefault('active_side_quests', []).append("SQ_FARMER_01")
                player['quest_progress']['SQ_FARMER_01'] = 0  # Initialize progress
                safe_input("> ")
            else:
                typewriter_effect("The farmer nods at you, hopeful. 'Still searching for that tune?'")
                safe_input("> ")

        elif px == 6 and py == 0 and "dragon_cultist_diary" not in codex and player['seal']:  # Cave Entrance (6,0)
            typewriter_effect("You find a charred piece of parchment tucked into the rock...")
            player = codex_add(player, "dragon_cultist_diary")
            safe_input("> ")

        elif interact_text:  # Player pressed 7, but it wasn't a standard building or known interactable
            # Default message if '7' was shown but no specific action defined (like "Greet farmer")
            typewriter_effect("You take a closer look around.")
            time.sleep(1)
        else:  # Player pressed 7 where it wasn't an option
            print("Nothing happens.")
            time.sleep(1)
        # --- End v1.8 Logic ---
    elif dest == "8" and player['rage_potions'] > 0:
        player['rage_potions'] -= 1;
        player['active_buff'] = "rage"
        print("Your ATK will be boosted in the next battle.");
        safe_input("> ")
    elif dest == "9" and player['stone_potions'] > 0:
        player['stone_potions'] -= 1;
        player['active_buff'] = "stone"
        print("You will take less damage in the next battle.");
        safe_input("> ")
    elif dest == "10":
        show_codex(player);
    elif dest == "11":
        handle_quest_log(player)
    elif dest == "12":
        handle_map_legend()
    elif dest == "13":
        player = handle_equipment_menu(player)
    elif dest == "14":
        handle_help_menu()
    elif dest == "dev" and player.get('dev_mode'):
        next_state = "debug_console"
    elif dest != "" and dest not in ["1", "2", "3", "4"]:  # Ignore empty input, allow movement
        print("Invalid command.")
        time.sleep(1)

        # Check for encounters AFTER movement or action
    if not standing and BIOMES[current_tile].get("e", False):
        roll = random.randint(1, 100)

        # Check for World Boss encounter (Reckless Path only)
        if not player['seal'] and player['key']:
            if roll <= 10:
                typewriter_effect("The sky darkens... a colossal shadow sweeps over you!")
                typewriter_effect(f"THE DRAGON HAS FOUND YOU!")
                safe_input("> ")
                next_state = "battle"
                enemy_to_fight = "Dragon_WorldBoss"

        # Check for Random Event (if not fighting World Boss)
        elif roll <= 18:  # 8% chance (11-18)
            next_state, player = handle_random_event(player)

        # Check for Regular Mob Encounter (if not fighting World Boss or having event)
        # v1.8: REFACTORED to handle world changes
        elif roll <= 48:  # 30% chance (19-48)
            base_possible_mobs = BIOMES[current_tile].get("m", [])
            if base_possible_mobs:
                # --- v1.8: World Change & Path Logic ---
                # Make a copy to modify
                current_possible_mobs = list(base_possible_mobs)
                main_q = player['main_quest_id']

                # 1. Swamp Cleanup - Check completed quests
                if "SQ_GUARD_01" in player.get('completed_side_quests', []):
                    if current_tile == "swamp" and "Fire Slime" in current_possible_mobs:
                        current_possible_mobs.remove("Fire Slime")

                # 2. Reckless Path Mobs
                if main_q == "MQ_05_RECKLESS":
                    if current_tile == "plains" and "Wolf" in current_possible_mobs:  # Check in Plains
                        current_possible_mobs.remove("Wolf")
                        if "Corrupted_Wolf" not in current_possible_mobs:
                            current_possible_mobs.append("Corrupted_Wolf")

                # 3. Hero Path Quest Mob - Spawn only if on this specific quest step
                elif main_q == "MQ_05_HERO_C":
                    if current_tile == "hills":
                        # Force spawn Sentinel if possible, otherwise normal mobs
                        if "Auren_Sentinel" in MOBS:  # Ensure mob exists
                            current_possible_mobs = ["Auren_Sentinel"]  # Prioritize quest mob
                        if "Auren_Sentinel" not in current_possible_mobs:
                            # Failsafe if Sentinel wasn't added correctly or if needed elsewhere
                            pass  # Use default hill mobs
                # --- End v1.8 Logic ---

                if current_possible_mobs:  # Check if list isn't empty after filtering
                    enemy_name = random.choice(current_possible_mobs)
                    next_state = "battle"
                    enemy_to_fight = enemy_name

    return next_state, player, enemy_to_fight

    # ==============================================================================
    # ## 5. MAIN GAME LOOP ##
    # (Controls the flow of the game)
    # ==============================================================================

def main():
    game_state = "main_menu"
    player = None
    while game_state != "exit":
        enemy_to_fight = None  # Reset enemy encounter flag each loop

        # Handle states that DON'T require an active player
        if game_state == "main_menu":
            game_state = handle_main_menu()
        elif game_state == "new_game_menu":
            game_state, player = handle_new_game_menu()
        elif game_state == "load_game_menu":
            game_state, player = handle_load_game_menu()
        elif game_state == "game_over":  # Final game over screen
            game_state = handle_game_over()
            player = None  # Ensure player is cleared

        # Handle states that REQUIRE an active player
        elif player:
            if game_state == "playing":
                game_state, player, enemy_to_fight = handle_playing(player)
            elif game_state == "shop":
                game_state, player, enemy_to_fight = handle_shop(player)
            elif game_state == "mayor":
                game_state, player, enemy_to_fight = handle_mayor(player)
            elif game_state == "cave":
                game_state, player, enemy_to_fight = handle_cave(player)
            elif game_state == "town":
                game_state, player, enemy_to_fight = handle_town(player)
            elif game_state == "debug_console":
                game_state, player, enemy_to_fight = handle_debug_console(player)
            elif game_state == "game_won":
                game_state = handle_game_won(player)
                player = None  # Clear player after winning

            # If handle_playing returned an enemy, start battle
            if enemy_to_fight:
                game_state, player = handle_battle(player, enemy_to_fight)
                # handle_battle returns "game_over" if player died permanently
                if game_state == "game_over":
                    player = None  # Ensure player is cleared for game over screen

        # Failsafe: If player data is lost unexpectedly
        elif game_state not in ["main_menu", "new_game_menu", "load_game_menu", "exit", "game_over"]:
            print("Error: Player data lost. Returning to main menu.")
            time.sleep(2)
            game_state = "main_menu"
            player = None

    print(f"\nThank you for playing {GAME_TITLE}!")

# Entry point of the script
if __name__ == "__main__":
    main()