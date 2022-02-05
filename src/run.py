import requests
import warnings
import scan
import cv2
import json
import time
import math
import actions
import keyboard
import cli
import multiprocessing

warnings.filterwarnings('ignore')

ENDPOINTS = {
    "eventdata" : "https://127.0.0.1:2999/liveclientdata/eventdata",
    "activeplayer": "https://127.0.0.1:2999/liveclientdata/activeplayer",
    "activeplayerabilities" : "​https://127.0.0.1:2999/liveclientdata/activeplayerabilities",
    "playerlist" : "https://127.0.0.1:2999/liveclientdata/playerlist",
    "gamestats" : "https://127.0.0.1:2999/liveclientdata/gamestats",
    "allgamedata" : "https://127.0.0.1:2999/liveclientdata/allgamedata"
}

class Settings:
    def __init__(self, record=False, name=None, games=0, config=None) -> None:
        self.record = record
        self.name = name
        self.games = games
        self.config = config
    def set_record(self):
        self.record = not self.record
    def set_name(self):
        self.name = not self.name
    def set_games(self):
        self.games = not self.games

class player:
    def __init__(self):
        self.current_level = 1
        self.item_number = 0
        self.stats = None
        self.team = None
        self.champ = None
        self.champ_info = None
        self.surrendering = False
    def set_champ_info(self):
        f = open('..\settings\champs.json')
        self.champ_info = json.load(f)[self.champ]
    def get_gold(self):
        return math.floor(self.stats["currentGold"])
    def get_level(self):
        return self.stats["level"]
    def get_time(self):
        return requests.get(ENDPOINTS["allgamedata"], verify=False).json()["gameData"]["gameTime"]
    def get_regen(self):
        return self.stats["championStats"]["healthRegenRate"]
    def get_health(self):
        return self.stats["championStats"]["currentHealth"] / self.stats["championStats"]["maxHealth"]
    def update(self):
        self.stats = requests.get(ENDPOINTS["activeplayer"], verify=False).json()

def fetch(object):
    players = None
    start_time = time.time()

    while not players and time.time() - start_time < 240:
        try:
            players = requests.get(ENDPOINTS[object], verify=False).json()
        except:
            time.sleep(1)
            continue
        return players
    return 0

def in_game(objects, settings):
    active_player = player()

    while not fetch("eventdata"):
        pass
    print("On Loading Screen")
    while not active_player.team:
        try:
            for i, p in enumerate(fetch("playerlist")):
                team = fetch("playerlist")[i]["team"]
                if p["summonerName"] == settings.name and team:
                    active_player.team = team
                    active_player.champ = fetch("playerlist")[i]["championName"].lower()
                    active_player.set_champ_info()
                    break
        except:
            time.sleep(1)
            continue
    print(f"On team {active_player.team}")
    time.sleep(1)
    print("In game")
    time.sleep(5)
    objects[:] = ["big_red", "red_bar", "minion", "enemy_health", "ally_health", "turret", "search_item"]
    actions.on_start(active_player)
    print("Bought starting item")
    while True:
        try:
            active_player.update()
            print("Updating player")
        except:
            "Game is over"
            break
        if actions.path_to_camp(active_player) is None:
            "Game is over"
            break

def start(objects, settings):
    game_count = 0
    print("Starting")
    while True:
        objects[:] = ["find_match", "in_queue", "accept", "ok"]
        while cli.in_queue():
            if cli.find_button("ok", 1):
                continue
        time.sleep(15)
        objects[:] = ["none", "ok", "cli_open", "ban"]
        while not cli.in_queue() and cli.cli_open("cli_open", 3):
            if cli.find_button("ok", 1):
                continue
            if cli.ban():
                break
        time.sleep(3)
        objects[:] = ["ok", "lock_in", "search", "x", "warwick", "udyr", "nunu & willump", "fiddlesticks"]
        while not cli.try_locking_in():
            #   Somebody dodged or player declined
            if cli.find_button("ok", 1):
                continue
            if cli.in_queue():
                break
        if cli.in_queue():
            continue
        print("Champ locked in")
        while not cli.in_queue() and cli.cli_open("cli_open", 3):
            if cli.find_button("ok", 1):
                continue
        if cli.in_queue():
            continue
        in_game(objects, settings)
        print("Match ended")
        start_time = time.time()
        time.sleep(3)
        objects[:] = ["next", "ok", "claim", "gg", "ok_game", "play_again"]
        while not cli.find_button("play_again", 1) and time.time() - start_time < 180:
            cli.find_button("next", 1)
            cli.find_button("ok", 1)
            cli.find_button("claim", 1)
            cli.find_button("gg", 1)
            cli.find_button("ok_game", 1)
        if start_time - time.time() > 180:
            print("Timed out after 180 seconds")
        game_count += 1
        if game_count == settings.games:
            break

def key_input(objects, settings):
    if settings.record:
        FPS = 10.0
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter("..\output.mp4", fourcc, FPS, scan.SCREEN_RES)
    while not keyboard.is_pressed('`'):
        if settings.record:
            try:
                frame = scan.display(objects, img="screen", team=None)
            except:
                continue
            out.write(frame)
        pass
    if settings.record:
        out.release()

def run_app(settings):
    with open(rf"{settings.config}\game.cfg", "r") as infile:
        orig_cfg = infile.read()
    with open(rf"{settings.config}\PersistedSettings.json", "r") as infile:
        orig_set = infile.read()

    with open(r"..\settings\game.cfg", "r") as infile:
        bot_cfg = infile.read()
    with open(r"..\settings\PersistedSettings.json", "r") as infile:
        bot_set = infile.read()
    
    with open(rf"{settings.config}\game.cfg", "w") as outfile:
        outfile.write(bot_cfg)
    with open(rf"{settings.config}\PersistedSettings.json", "w") as outfile:
        outfile.write(bot_set)

    manager = multiprocessing.Manager()
    shared_list = manager.list()

    proc1 = multiprocessing.Process(target=start, args=[shared_list, settings])
    proc2 = multiprocessing.Process(target=key_input, args=[shared_list, settings])
    proc1.start()
    proc2.start()
    while proc2.is_alive():
        pass
    print("Quitting")
    proc1.terminate()
    proc2.join()
    
    with open(rf"{settings.config}\game.cfg", "w") as outfile:
        outfile.write(orig_cfg)
    with open(rf"{settings.config}\PersistedSettings.json", "w") as outfile:
        outfile.write(orig_set)