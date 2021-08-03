#!/bin/bash
devices=`adb devices|tac|sed -n '2p'|cut -f1`

if [[ $devices =~ ^List ]]
then
    echo -e "No devices detected.\nConnect your phone to pc using usb, turn on developers option and set connection to file transfer mode."
    exit 1
else
    echo "Your device: $devices"
fi

if [[ $devices =~ ([0-9]{1,3}\.){3}[0-9]{1,3} ]]
then
    echo "Already connected wirelessly. Youre good to go."
    exit 0
fi

ip=`adb shell ip addr|grep "inet " |tail -n1|grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}'|head -n1`
echo "Your phone ip: $ip"

adb tcpip 5555 >>/dev/null 2>&1
connect=`adb connect $ip:5555`

if [[ $connect =~ ^failed ]]
then
    echo "Your pc and phone should be connected to the same router, which means campus wifi may not work."
    exit 2
fi

echo "Connection established."
