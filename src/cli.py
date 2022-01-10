from actions import cast_action, right_click, left_click, type_word
import scan
import time

CHAMP_LIST = [
    "warwick",
    "udyr",
    "nunu & willump",
    "fiddlesticks",
]

def find_button(button, wait_time):
    loc = None
    start_time = time.time()

    while not loc and time.time() - start_time < wait_time:
        loc = scan.find(None, "screen", button)
        time.sleep(0.5)
    if loc:
        print(f"Found {button}")
        left_click(loc)
        return True
    else:
        print(f"Processing")
        return False

def cli_open(obj, wait_time):
    loc = None
    start_time = time.time()

    while not loc and time.time() - start_time < wait_time:
        loc = scan.find(None, "screen", obj)
        time.sleep(0.5)
    if loc:
        print(f"Found {obj}")
        return True
    else:
        print(f"Processing")
        return False

def lock_in(champ):
    if find_button(champ, 1):
        print(f"{champ} found")
    else:
        print(f"could not find {champ}")
        return False
    if find_button("lock_in", 1):
        print("locking in")
        return True
    print(f"could not lock in")
    return False

def try_locking_in():
    for champion in CHAMP_LIST:
        find_button("search", 1)
        type_word(champion)
        if lock_in(champion):
            return True
        find_button("search", 1)
        find_button("x", 1)
    return False

def in_queue():
    return find_button("accept", 1) or find_button("in_queue", 1) or find_button("find_match", 1)

def ban():
    if find_button("none", 1):
        find_button("ban", 3)
        return True
    else:
        return False