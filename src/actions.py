import threading
import time
import math
import win32api, win32con
import pydirectinput
import scan
import random

MAP_COORDS = {
    "blue_base" : (1560, 1000),
    "red_base" : (1875, 690),
    "map" : (1540, 660)
}
OFFSET = 45

def cast_action(action, hold):
    pydirectinput.keyDown(action)
    time.sleep(hold)
    pydirectinput.keyUp(action)

def type_word(word):
    for c in word:
        cast_action(c, 0.01)
    cast_action('enter', 0.01)

def right_click(p):
    win32api.SetCursorPos(p)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def left_click(p):
    win32api.SetCursorPos(p)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def path_to_fountain(active_player):
    if active_player.team == "ORDER":
        right_click(MAP_COORDS["blue_base"])
    elif active_player.team == "CHAOS":
        right_click(MAP_COORDS["red_base"])

def on_start(active_player):
    tm_loc = None
    sc_loc = None
    start_time = time.time()
    while not tm_loc and not sc_loc:
        tm_loc = scan.find(active_player.team, "map", "timer")
        sc_loc = scan.find(active_player.team, "map", "small_camp")
        if int(time.time() - start_time) > 135:
            print("Timed out")
            return
    left_click((960, 540))
    cast_action('enter', 0.1)
    type_word("muting all")
    level_up_ability(active_player)
    buy_item(active_player)

def path_to_camp(active_player):
    m_loc = MAP_COORDS["map"]

    cast_action("y", 0.5)    
    if active_player.team == "ORDER":
        left_click(MAP_COORDS["blue_base"])
    elif active_player.team == "CHAOS":
        left_click(MAP_COORDS["red_base"])
    bc_loc = scan.find(active_player.team, "map", "big_camp")
    sc_loc = scan.find(active_player.team, "map", "small_camp")
    tm_loc = scan.find(active_player.team, "map", "timer")

    if bc_loc:
        right_click((m_loc[0] + bc_loc[0], m_loc[1] + bc_loc[1]))
        return attack_camp(active_player)
    elif sc_loc:
        right_click((m_loc[0] + sc_loc[0], m_loc[1] + sc_loc[1]))
        return attack_camp(active_player)
    elif tm_loc:
        right_click((m_loc[0] + tm_loc[0], m_loc[1] + tm_loc[1]))
        return attack_camp(active_player)
    else:
        cast_action("y", 0.5)
        print("No camps left")
        return check_player(active_player)

def attack_camp(active_player):
    cast_action("y", 0.5)
    cast_time = active_player.champ_info["cast_time"]
    target = scan.find(None, "screen", "red_bar")

    start_time = time.time()
    while not target:
        status = check_player(active_player)
        if status or status is None:
            return status
        target = scan.find(None, "screen", "red_bar")
        if int(time.time() - start_time) >= 45:
            print("Timed out")
            return True
    
    prev_health = math.ceil(active_player.stats["championStats"]["currentHealth"])
    curr_health = 0
    alternate = 1
    while target or not (curr_health in range(prev_health - 2, prev_health + 1)):
        print("Targeting")
        alternate *= -1
        try:
            active_player.update()
        except:
            return None
        start_time = time.time()
        prev_health = math.ceil(active_player.stats["championStats"]["currentHealth"])
        if target:
            prev = target

        random.seed()
        rand = int(random.random() * 15.0)
        status = check_player(active_player)
        if status or status is None:
            return status
        
        if not target:
            right_click((prev[0], prev[1] + (OFFSET + rand)))
        cast_action('q', cast_time['q'])
        cast_action('e', cast_time['e'])

        random.seed()
        rand = int(random.random() * 15.0)
        target = scan.find(None, "screen", "red_bar")
        if target:
            right_click((target[0] - (rand * alternate), target[1] + (OFFSET + rand)))
        status = check_player(active_player)
        if status or status is None:
            return status
        if active_player.get_health() < 0.75:
            cast_action('f', 0.25)
        cast_action('w', cast_time['w'])

        target = scan.find(None, "screen", "red_bar")
        try:
            active_player.update()
        except:
            return None
        curr_health = math.ceil(active_player.stats["championStats"]["currentHealth"])
        if curr_health == prev_health and not target:
            break
        prev_health += math.ceil(active_player.get_regen() * (time.time() - start_time))
    print("Finished with camp")
    return False

def buy_item(active_player):
    try:
        active_player.update()
    except:
        return

    cast_action('p', 1)
    items = active_player.champ_info["items"]
    buy_loc = scan.find(None, "screen", "search_item")
    item_name = items[active_player.item_number][0]
    cost = items[active_player.item_number][1]

    if buy_loc and active_player.get_gold() >= cost:
        left_click(buy_loc)
        time.sleep(0.5)
        pydirectinput.click(button='left')
        time.sleep(0.5)
        left_click(buy_loc)
        time.sleep(0.5)
        type_word(item_name)
        right_click((buy_loc[0], buy_loc[1] - 100))
        time.sleep(0.5)
        pydirectinput.click(button='right')
        time.sleep(0.5)
        right_click((buy_loc[0], buy_loc[1] - 100))
        time.sleep(0.5)
        active_player.item_number += 1
    else:
        print("Could not find item or not enough gold")
    cast_action('p', 1)
    left_click((960, 540))
    right_click((960, 540))

def recall(active_player):
    path_to_fountain(active_player)
    time.sleep(8)
    cast_action('b', 1)

    try:
        active_player.update()
    except:
        return
    prev_health = active_player.stats["championStats"]["currentHealth"]
    time.sleep(6.8)
    try:
        active_player.update()
    except:
        return
    curr_health = math.ceil(active_player.stats["championStats"]["currentHealth"])
    is_max = curr_health == math.ceil(prev_health)
    prev_health = math.ceil(prev_health + active_player.get_regen() * 6.8)
    if  prev_health not in range(curr_health - 2, curr_health + 2) and not is_max:
        print("Failed recall")
        recall(active_player)
        return
    start_time = time.time()
    while active_player.get_health() < 1.0:
        try:
            active_player.update()
        except:
            return
        if time.time() - start_time > 20:
            print("Timed out on recall")
            recall(active_player)
            return
    print("Full health")
    time.sleep(1)
    buy_item(active_player)

def level_up_ability(active_player):
    try:
        active_player.current_level = active_player.get_level()
    except:
        return
    
    pydirectinput.keyDown("ctrl")
    for a in active_player.champ_info["cast_order"]:
        cast_action(a, 0.5)
    pydirectinput.keyUp("ctrl")

def detect(object, dat={}):
    obj_loc = scan.find(None, "screen", object)
    if obj_loc:
        dat[object] = True
    else:
        dat[object] = False
    return dat[object]

def path_turret(active_player):
    m_loc = MAP_COORDS["map"]
    turret = scan.find(None, "screen", "turret")
    turret = scan.scale_point(scan.SCREEN_RES, (scan.MAP_SIZE, scan.MAP_SIZE), scan.flip(turret))
    turret = (m_loc[0] + turret[0], m_loc[1] + turret[1])
    path_to_fountain(active_player)
    time.sleep(3)

def attack_enemy(active_player):
    m_loc = MAP_COORDS["map"]
    use_rd = False
    cast_time = active_player.champ_info["cast_time"]
    enemies = scan.find(None, "screen", "enemy_health")
    if not enemies:
        return False
    
    allies = scan.find(None, "screen", "ally_health")
    allies = 0 if allies is None else len(allies)

    while enemies:
        if detect("turret"):
            path_turret(active_player)
        enemies = scan.find(None, "screen", "enemy_health")
        if not enemies:
            break
        enemy = enemies[0]
        allies = scan.find(None, "screen", "ally_health")
        allies = 0 if allies is None else len(allies)

        try:
            active_player.update()
        except:
            break
        if (active_player.get_health() > 0.75) and allies >= len(enemies):
            print("attacking")
            right_click((enemy[0], enemy[1] + OFFSET))
            cast_action('r', cast_time['r'])
            cast_action('q', cast_time['q'])
            if detect("turret"):
                path_turret(active_player)
            cast_action('e', cast_time['e'])
            cast_action('w', cast_time['w'])
        else:
            print("fleeing")
            if not use_rd and (active_player.get_health() <= 0.75):
                right_click(scan.flip(enemy))
                cast_action('r', cast_time['r'])
                cast_action('d', 0.1)
                use_rd = True
            enemy = scan.scale_point(scan.SCREEN_RES, (scan.MAP_SIZE, scan.MAP_SIZE), scan.flip(enemy))
            enemy = (m_loc[0] + enemy[0], m_loc[1] + enemy[1])
            right_click(enemy)
    return True
    
def surrender():
    messages = [
        ["ff"],
        ["surrender"],
        ["please ff"],
        ["i gtg", "surrender"],
        ["ff", "please"],
        ["i have to go eat", "can we surrender"],
    ]
    rand_mes = messages[random.randrange(len(messages))]
    cast_action('enter', 0.1)
    type_word("/ff")
    for mes in rand_mes:
        cast_action('enter', 0.1)
        type_word(mes)

def check_player(active_player): #  Returning true means you disrupt the clearing
    try:
        active_player.update()
    except:
        print("Error updating")
        return None

    threads = []
    dat = {}
    threads.append(threading.Thread(target=detect, args=("enemy_health", dat)))
    threads.append(threading.Thread(target=detect, args=("turret", dat)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    try:
        game_time = active_player.get_time() // 60
        if dat["enemy_health"]:
            print("enemy detected")
            attack_enemy(active_player)
            return True
        if dat["turret"]:
            print("turret detected")
            path_turret(active_player)
            return True
        if active_player.get_health() < 0.25:
            print("recalling")
            recall(active_player)
            return True
        if active_player.get_gold() >= 1300:
            print("recalling for item")
            recall(active_player)
            return True
        if active_player.get_level() > active_player.current_level:
            print("active player level up")
            level_up_ability(active_player)
            return True
        if active_player.get_time() // 60 >= 15 and not game_time % 3 and not active_player.surrendering:
            active_player.surrendering = True
            print(f"Surrendering {game_time}")
            surrender()
            return True
        elif (active_player.get_time() // 60) % 3:
            active_player.surrendering = False
    except:
        return False
    return False