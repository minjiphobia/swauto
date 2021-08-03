#!/usr/bin/python3
# -*- encoding=utf8 -*-
__author__ = "Minji"

import cv2 as cv
import numpy as np
import subprocess
import shlex
import datetime
import time
from colorama import Fore
from colorama import Style

import images
import pos
# script content

ok_hw=39
ok_hh=26
ok_pos=(0, 0)

default_sleep_dura=0.5
threshold=0.9

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
        time.sleep(1)
        
        i = (i + 1) % n
        if i == 0:
            deadloop_handler(screenshot)


def buy_energy():
    print_time()
    print("buy a refill.")

    touch(pos.shop_pos)
    time.sleep(default_sleep_dura)
    touch(pos.shop_pos)
    time.sleep(default_sleep_dura)
    touch(pos.yes_pos)
    time.sleep(default_sleep_dura)

    # when there is a quiz ring alarm and quit
    subprocess.check_output(shlex.split("adb shell screencap -p /sdcard/screencap.png")) 
    subprocess.check_output(shlex.split("adb pull /sdcard/screencap.png"))
    screenshot = cv.imread('screencap.png', 0)
    if match(screenshot, images.quiz_gray):
        subprocess.check_output(shlex.split("adb shell am start -n com.tencent.qqmusic/.activity.AppStarterActivity -d /sdcard/qqmusic/song/AmericanPieLive.mp3"))
        time.sleep(default_sleep_dura)
        subprocess.check_output(shlex.split("adb shell input keyevent 85"))
        quit()

    touch((1160, 675))#ok
    time.sleep(default_sleep_dura)
    touch((1050, 900))#close
    time.sleep(default_sleep_dura)
    touch(pos.replay_pos)#replay
    time.sleep(default_sleep_dura)
    touch(pos.start_pos)

def fail():
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
    touch((ok_pos[0]+ok_hw, ok_pos[1]+ok_hh))
    time.sleep(default_sleep_dura)
    touch(pos.replay_pos)#replay
    time.sleep(default_sleep_dura)
    touch(pos.start_pos)
    print_time()
    print(f'finish one stage')

def deadloop_handler(screenshot):
    if match(screenshot, images.network_gray):
        touch((850, 650))#yes
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

print_time()
print("start da fcking grinding...")
main()
