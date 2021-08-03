#!/usr/bin/python3
# -*- encoding=utf8 -*-
__author__ = "Minji"

import cv2 as cv
import subprocess
import shlex
import datetime
import time
import atexit
from colorama import Fore
from colorama import Style

import images
import pos

# script content

ok_hw=39
ok_hh=26
ok_pos=(0, 0)

default_sleep_dura=0.5
threshold=0.95

# stats
s6rare=0
s6hero=0
s6leng=0
sells=0
materials=0
fails=0
refills=0

def print_time():
    current_time = datetime.datetime.now()
    print(current_time.strftime("%H:%M:%S"),end=": ")

def touch(pos):
    subprocess.check_output(shlex.split("adb shell input tap {} {}".format(pos[0], pos[1])))

def match(pic, templ):
    res = cv.matchTemplate(pic, templ, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    if max_val < threshold:
        return False
    else:
        return max_loc

def main():
    i = 0
    n = 10
    while True:
        subprocess.check_output(shlex.split("adb shell screencap -p /sdcard/screencap.png")) 
        subprocess.check_output(shlex.split("adb pull /sdcard/screencap.png"))
        screenshot = cv.imread('screencap.png', 0)
        global ok_pos
        ok_pos = match(screenshot, images.ok_gray)
        if ok_pos:
            success(screenshot)
        if match(screenshot, images.revive_gray):
            fail()
        if match(screenshot, images.shop_gray):
            buy_energy()
        touch(pos.idle_pos)
        time.sleep(default_sleep_dura)
        touch(pos.idle_pos)
        time.sleep(2*default_sleep_dura)

        i = (i + 1) % n
        if i == 0:
            deadloop_handler(screenshot)

def deadloop_handler(screenshot):
    if match(screenshot, images.network_gray):
        touch((910, 650))#yes
        return
    if match(screenshot, images.network2_gray):
        touch((910, 710))#yes
        return
    if match(screenshot, images.revive_gray):
        fail()
        return
    if match(screenshot, images.replay_gray):
        touch(pos.replay_pos)#replay
        return
    if match(screenshot, images.start_gray):
        touch(pos.start_pos)#start
        return
    if match(screenshot, images.prepare_gray):
        touch(pos.prepare_pos)#prepare
        return

def buy_energy():
    global refills
    refills+=1

    print_time()
    print("buy a refill.")

    touch(pos.shop_pos)
    time.sleep(default_sleep_dura)
    touch(pos.shop_pos)
    time.sleep(default_sleep_dura)
    touch(pos.yes_pos)
    time.sleep(default_sleep_dura)

    # when there is a quiz, ring alarm and quit
    subprocess.check_output(shlex.split("adb shell screencap -p /sdcard/screencap.png")) 
    subprocess.check_output(shlex.split("adb pull /sdcard/screencap.png"))
    screenshot = cv.imread('screencap.png', 0)
    if match(screenshot, images.quiz_gray):
        subprocess.check_output(shlex.split("adb shell am start -n com.tencent.qqmusic/.activity.AppStarterActivity -d /sdcard/qqmusic/song/AmericanPieLive.mp3"))
        time.sleep(5*default_sleep_dura)
        subprocess.check_output(shlex.split("adb shell input keyevent 85"))
        quit()

    touch((1160, 675))#ok
    time.sleep(default_sleep_dura)
    touch((1050, 900))#close
    time.sleep(default_sleep_dura)
    touch(pos.replay_pos)#replay

def fail():
    global fails
    fails+=1
    touch(pos.no_pos)#no
    time.sleep(default_sleep_dura)
    touch(pos.idle_pos)
    time.sleep(default_sleep_dura)
    touch(pos.prepare_pos)#prepare
    time.sleep(default_sleep_dura)
    touch(pos.start_pos)#start
    print_time()
    print("fail one time. thx rngesus")
        
def success(screenshot):
    # rune select
    rune_level=''
    rune_grade=''
    global s6leng
    global s6hero
    global s6rare
    global s5leng
    global materials
    if match(screenshot, images.s6_gray):
        rune_level='6'
        if match(screenshot, images.leng_gray):
            rune_grade='leng'
            s6leng+=1
        elif match(screenshot, images.hero_gray):
            rune_grade='hero'
            s6hero+=1
        else: 
            rune_grade='rare'
            if not match(screenshot, images.speed_gray) and not match(screenshot, images.percent_gray):
                sell_rune()
                print_time()
                print(f"{Fore.RED}SELL{Style.RESET_ALL} a {rune_level}* {rune_grade} trash rune.  thx com2us")
                return
            s6rare+=1
    else:
        materials+=1

    touch((ok_pos[0]+ok_hw, ok_pos[1]+ok_hh))
    time.sleep(default_sleep_dura)
    touch(pos.replay_pos)#replay
    print_time()
    if rune_level != '':
        print(f"{Fore.GREEN}GET{Style.RESET_ALL}  a {rune_level}* {rune_grade} trash rune.  thx com2us")
    else:
        print(f"{Fore.YELLOW}GET{Style.RESET_ALL} more useless materials. thx com2us")

def sell_rune():
    global sells
    sells+=1
    touch(pos.sell_pos)
    time.sleep(default_sleep_dura) #wait extra time to circumvent traffic delay after sending selling info
    touch(pos.yes_pos)#yes
    time.sleep(4*default_sleep_dura)
    touch(pos.replay_pos)#replay

def print_loot():
    print("\n\n")
    print(f"TOTAL STATS:")
    elapsed_time = datetime.datetime.now() - start_time
    print(f"elapsed time:", "{:.1f}".format(elapsed_time.total_seconds()/60))
    print(f"6* leng rune: {s6leng}")
    print(f"6* hero rune: {s6hero}")
    print(f"6* rare rune: {s6hero}")
    print(f"sells       : {sells}")
    print(f"materials   : {materials}")
    print(f"fails       : {fails}")
    print(f"total runs  : {s6leng+s6hero+sells+materials+fails}")
    print(f"refills     : {refills}")

def update_stats():
    f = open ("stats", "r+")
    cin = f.read().splitlines()
    cout = ""
    cout = cout + cin[0] + "\n"
    cout = cout + cin[1][:15] + str(int(cin[1][15:]) + s6leng) + "\n"
    cout = cout + cin[2][:15] + str(int(cin[2][15:]) + s6hero) + "\n"
    cout = cout + cin[3][:15] + str(int(cin[3][15:]) + s6rare) + "\n"
    cout = cout + cin[4][:15] + str(int(cin[4][15:]) + sells) + "\n"
    cout = cout + cin[5][:15] + str(int(cin[5][15:]) + materials) + "\n"
    cout = cout + cin[6][:15] + str(int(cin[6][15:]) + fails) + "\n"
    cout = cout + cin[7][:15] + str(int(cin[7][15:]) + s6leng+s6hero+s6rare+sells+materials+fails) + "\n"
    cout = cout + cin[8][:15] + str(int(cin[8][15:]) + refills) + "\n"
    f.seek(0)
    f.truncate()
    f.write(cout)
    f.close()

atexit.register(print_loot)
atexit.register(update_stats)

start_time = datetime.datetime.now()
print_time()
print("start da fcking grinding...")
main()
