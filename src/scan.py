import pyautogui
import cv2
import numpy
import time
import threading

MAP_SIZE = 350
SCREEN_RES = (1920, 1080)

def find(team, img, object):
    if img == "screen":
        iml = pyautogui.screenshot(region=(0, 0, SCREEN_RES[0], SCREEN_RES[1]))
        iml = cv2.cvtColor(numpy.array(iml), cv2.COLOR_RGB2BGR)
    elif img == "map":
        iml = pyautogui.screenshot(region=(1540, 660, MAP_SIZE, MAP_SIZE))
        iml = cv2.cvtColor(numpy.array(iml), cv2.COLOR_RGB2BGR)
    img_object = cv2.imread(fr"..\res\{object}.png", cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(iml, img_object, cv2.TM_CCOEFF_NORMED)
    
    w = img_object.shape[1]
    h = img_object.shape[0]

    if object == "red_bar" or object == "minion":
        thresh = 0.98
    elif object == "small_camp" or object == "big_camp":
        thresh = 0.80
    elif object == "buy":
        thresh = 0.75
    elif object == "enemy_health" or object == "ally_health":
        thresh = 0.70
    else:
        thresh = 0.90
    
    yloc, xloc = numpy.where(result >= thresh)
    locs = [((x + w // 2), (y + h // 2)) for (x, y) in zip(xloc, yloc)]
    locs = unify(img_object, locs)
    res = []
    if object == "red_bar" and not len(locs):
        res = find(None, img, "minion")
        return res
    if team == "ORDER":
        res = [loc for loc in locs if loc[0] < loc[1]]
    elif team == "CHAOS":
        res = [loc for loc in locs if loc[0] > loc[1]]
    elif team is None:
        res = [loc for loc in locs]
    sorted(res, key = lambda x: x[1])
    res.reverse()
    if object == "enemy_health":
        return filter(iml, res, range(160, 205), range(30, 90), range(20, 110))
    elif object == "ally_health":
        return filter(iml, res, range(20, 110), range(140, 210), range(200, 255))
    elif object == "buy":
        return res if len(res) > 0 else None
    return res[0] if res else None

def unify(object, group):
    w = object.shape[1]
    h = object.shape[0]
    recs = []

    for (x, y) in group:
        recs.append([int(x), int(y), int(w), int(h)])
        recs.append([int(x), int(y), int(w), int(h)])
    recs, weights = cv2.groupRectangles(recs, 1, 0.75)
    return [(rec[0], rec[1]) for rec in recs]

def filter(img, group, r_ran, g_ran, b_ran):
    targets = []
    for p_target in group:
        b, g, r = img[p_target[1]][p_target[0]]
        if r in r_ran and g in g_ran and b in b_ran:
            targets.append(p_target)
    return targets if len(targets) > 0 else None

def flip(p):
    return (SCREEN_RES[0] - p[0], SCREEN_RES[1] - p[1])

def scale_point(s1, s2, p):
    new_x = int((p[0] / s1[0]) * s2[0])
    new_y = int((p[1] / s1[1]) * s2[1])
    return (new_x, new_y)

def display_find(team, img, object, locs):
    img_object = cv2.imread(fr"..\res\{object}.png", cv2.IMREAD_UNCHANGED)
    w = img_object.shape[1] // 2
    h = img_object.shape[0] // 2
    res = find(team, img, object)
    if isinstance(res, list) and res:
        for r in [(loc[0], loc[1], w, h) for loc in res]:
            locs.append(r)
    elif res:
        locs.append((res[0], res[1], w, h))

def display(objects, img, team):
    locs = []
    if img == "screen":
        iml = pyautogui.screenshot(region=(0, 0, SCREEN_RES[0], SCREEN_RES[1]))
        iml = cv2.cvtColor(numpy.array(iml), cv2.COLOR_RGB2BGR)
    elif img == "map":
        iml = pyautogui.screenshot(region=(1540, 660, MAP_SIZE, MAP_SIZE))
        iml = cv2.cvtColor(numpy.array(iml), cv2.COLOR_RGB2BGR)
    threads = [None] * len(objects)
    for i, object in enumerate(objects):
        threads[i] = threading.Thread(target=display_find, args=(team, img, object, locs))
        threads[i].start()
    for t in threads:
        if t:
            t.join()

    for (x, y, w, h) in locs:
        cv2.rectangle(iml, (x - w, y - h), (x + w, y + h), (0, 255, 0), 2)
    return iml
