from cnocr import CnOcr
import d3dshot
import time
import json
import codecs
import pyautogui
import Levenshtein

cfg = json.load(codecs.open('config.json', encoding='utf-8'))
places = json.load(codecs.open('places.json', encoding='utf-8'))
place_con = {}
words = set()
for k, v in places.items():
    for place in v:
        for w in place:
            words.add(w)
        place_con[place] = k
ocr = CnOcr(model_name='densenet-lite-gru')
d = d3dshot.create(capture_output="numpy")
time.sleep(1)
region = cfg['region']
region = region[0], region[1], region[0] + region[2], region[1] + region[3]
d.capture(region=region)
st = time.time()
while time.time() - st < 80:
    frame = d.get_latest_frame()
    if frame is None:
        time.sleep(0.001)
        continue
    ocr_res = ocr.ocr_for_single_line(frame)
    ocr_res = "".join(ocr_res)
    if "，" in ocr_res:
        ocr_res = ocr_res.split("，")[0]
    fix_res = list(filter(lambda x: x in words, ocr_res))
    fix_res = "".join(fix_res)
    print(f'result: {fix_res} ocr result: {ocr_res}')
    check = [(k, Levenshtein.distance(k, fix_res)) for k in place_con]
    place, dis = sorted(check, key=lambda x: x[1])[0]
    if dis <= 1:
        con = place_con[place]
        click_pos = cfg['postbox'][con]
        print(f'click on {con}')
        pyautogui.leftClick(click_pos[0], click_pos[1], interval=0.1, duration=0.1)
d.stop()
