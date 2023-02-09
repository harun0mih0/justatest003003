#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from datetime import timedelta

import random
import requests
import re
import json
import urllib.request

import time
from plurk_oauth import PlurkAPI

plurk = PlurkAPI('6eomfCWLFFlL', '0kiAIyR1GlzanQpSDV9UPlVlqpEtdtxJ')
plurk.authorize('FTWUNPZMrTRb', 'lAmkWfnhrjCpEqAish5G8MLk30fQjz15')
comet = plurk.callAPI('/APP/Realtime/getUserChannel')
data = plurk.callAPI('/APP/FriendsFans/getCompletion')
new_offset = data.get('new_offset', -1)
comet_channel = comet.get('comet_server') + "&new_offset=%d"
jsonp_re = re.compile('CometChannel.scriptCallback\((.+)\);\s*');


def auth():
    plurk.authorize('FTWUNPZMrTRb', 'lAmkWfnhrjCpEqAish5G8MLk30fQjz15')
    time.sleep(0.1)
    comet = plurk.callAPI('/APP/Realtime/getUserChannel')
    try:
        comet_channel = comet.get('comet_server') + "&new_offset=%d"
        jsonp_re = re.compile('CometChannel.scriptCallback\((.+)\);\s*');
    except Exception as e:
        print("[err]auth:")
        print(e)
    print("auth ok!")


def setFriendList():
    try:
        data = plurk.callAPI('/APP/FriendsFans/getCompletion')
        if data is not None:
            for user in data:
                if not user in friend_list:
                    friend_list.append(user)
    except Exception as e:
        print(f"setFriendList err: {e}")


def initApi():
    auth()
    plurk.callAPI('/APP/Alerts/addAllAsFriends')
    time.sleep(0.1)
    setFriendList()
    # print("init:"+str(new_offset))
    req = urllib.request.urlopen(comet_channel % new_offset, timeout=80)
    time.sleep(0.1)
    rawdata = req.read()
    match = jsonp_re.match(rawdata.decode('ISO-8859-1'))
    return match



def findTargetResponse(res_list, res_id):
    for res in res_list:
        if res['id'] == res_id:
            return res['content_raw']

    return "not found"


def responseMentioned():
    plurks = plurk.callAPI('/APP/Alerts/getActive')
    if plurks is not None:
        for pu in plurks:
            if pu is not None:
                if pu['type'] == "mentioned":
                    res_id = pu['response_id']
                    pid = pu['plurk_id']
                    res_json = plurk.callAPI('/APP/Responses/get', {'plurk_id': pid})
                    if res_json is None:
                        pass
                    else:
                        res_list = res_json['responses']
                        target = findTargetResponse(res_list, res_id)
                        dealContent(pid, target, True, pu, pu['from_user']['id'])



def dealContent(pid, content, isCmd, pu, user_id):
    print("reply plurk id:" + str(pid) + " content:" + content + " pu:" + str(pu))
    if content.find("狗狗") != -1 or content.find("狗勾") != -1:
        plurkResponse(pid, '真麻煩')
    else:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        x = current_time.split(":")
        h = x[0]
        if content.find("謝謝") != -1:
            plurkResponse(pid, "不客氣！[emo9]")
        elif content.find("女友") != -1 or content.find("女朋友") != -1:
            plurkResponse(pid, "謝謝你的喜歡！也記得要這麼喜歡自己喔！[emo9]")
        elif content.find("我愛你") != -1:
            plurkResponse(pid, "窩也愛你！[emo9]")
        else:
            random.shuffle(random_list)
            plurkResponse(pid, random_list[0])

            
while True:
    match = initApi()
    if match:
        rawdata = match.group(1)
    data = json.loads(rawdata)
    new_offset = data.get('new_offset', -1)
    msgs = data.get('data')
    responseMentioned()
    print("Seal bot is working!")
    if not msgs:
        continue
    for msg in msgs:
        pid = msg.get('plurk_id')
        user_id = msg.get('user_id')

        if user_id is None:
            try:
                pid = msg['plurk']['plurk_id']
                user_id = msg['plurk']['user_id']
            except Exception as e:
                print("sth wrong: msg:" + str(e))
                continue

        if str(user_id) not in friend_list:
            print("Not in friend list.")
            continue

        if msg.get('type') == 'new_plurk':
            print(f"reply now user:{user_id} msg: {msg.get('content')}")
            content = msg.get('content_raw')
            if content.find("--noreply") != -1 or content.find("慎入") != -1:
                print(":p")
            else:
                dealContent(pid, content, False, "", user_id)
