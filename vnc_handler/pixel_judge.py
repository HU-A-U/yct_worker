# -*- coding:utf-8 -*-
import json
import os
import random
import shlex

import cv2
import requests
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from vncdotool import api

client = api.connect('127.0.0.1::5900')


class Ftech:
    def __init__(self):
        """基本配置"""
        self.usernames = 'cicjust'
        self.password = 'JYcxys@3030'
        self.base_params = {
            'username': self.usernames,
            'password': self.password,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'
            , }

    def rk_create(self, im, im_type, timeout=10):
        """
        im: 图片字节
        im_type: 题目类型
        """

        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://aiapi.c2567.com/api/create', data=params, files=files, headers=self.headers)
        print r.json()
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update({self.username: self.password})
        r = requests.post('http://aiapi.c2567.com/api/reporterror', data=params, headers=self.headers)
        return r.json()


class Pil_Deal(Ftech):
    def __init__(self):
        Ftech.__init__(self)

    def getPngPix(self, **kwargs):
        '''根据坐标值获取像素'''
        pngPath = r"./{}/screenshot.png".format(self.username)
        img_src = Image.open(pngPath)
        str_strlist = img_src.load()
        if 'pixels' in kwargs:
            items = []
            for i in kwargs['pixels']:
                item = {}
                print i
                pixelX, pixelY = i.split(',')
                x, y, z = str_strlist[int(pixelX), int(pixelY)]
                item[i] = str(x) + ',' + str(y) + ',' + str(z)
                items.append(item)
            img_src.close()
            return items
        else:
            current_map = []
            for m in kwargs['map']:
                current_m = {}
                pixelX, pixelY = m.keys()[0].split(',')
                x, y, z = str_strlist[int(pixelX), int(pixelY)]
                current_m[m.keys()[0]] = str(x) + ',' + str(y) + ',' + str(z)
                current_map.append(current_m)
                img_src.close()
            return current_map

    def vdo_recorder(self, vdo_route, vdo_replay):
        '''vdo文件处理'''
        if not os.path.isfile(vdo_replay):
            garbage_collection = []
            with open(vdo_route, mode='r') as folder:
                text = folder.readlines()
            text.append('end')
            while len(text) > 1:
                if not len(garbage_collection):
                    previous = text.pop(0)
                    if 'end' in previous:
                        break
                else:
                    previous = garbage_collection.pop(0)
                latter = text.pop(0)
                if 'move' in latter:
                    garbage_collection.append(latter)
                elif 'end' in latter:
                    break
                elif 'move' in previous and 'move' not in latter:
                    text.append(previous)
                    text.append(latter)
                elif 'move' not in previous and 'move' not in latter:
                    text.append(previous)
                    text.append(latter)
            with open(vdo_replay, mode='w') as folder:
                for i in text:
                    folder.write(i)

    def on_EVENT_LBUTTONDOWN(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            xy = "%d,%d" % (x, y)
            coordinate = str(x) + ',' + str(y)
            self.pngpix.append(coordinate)
            print self.pngpix
            cv2.circle(self.img, (x, y), 1, (255, 0, 0), thickness=-1)
            cv2.putText(self.img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                        1.0, (0, 0, 0), thickness=0)
            cv2.imshow("image", self.img)

    def picture_coordinates(self):
        '''获取图片的坐标'''
        self.pngpix = []
        coordinates_route = r"./{}/screenshot.png".format(self.username)
        self.img = cv2.imread(coordinates_route)
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.on_EVENT_LBUTTONDOWN)
        cv2.imshow("image", self.img)
        while (True):
            try:
                x = cv2.waitKey(100)
                if x == 27:
                    break
            except Exception:
                cv2.destroyWindow("image")
                break
        return self.pngpix

    def mapping_relation(self, items, event):
        '''建立像素,坐标,图片的映射关系'''
        file = './{}/{}.json'.format(self.username, event)
        if not items:
            with open(file) as folder:
                data = json.load(folder)
            return data
        else:
            mapping_table = {'event': event, 'map': ''}
            mapping_table['map'] = self.getPngPix(pixels=items)
            with open(file, 'w') as folder:
                print mapping_table
                json.dump(mapping_table, folder, ensure_ascii=False)
                return 'success'

    def vnc_screenshot(self, event):
        '''vnc截图'''
        file = './{}/{}.json'.format(self.username, event)
        if not os.path.isfile(file):
            items = self.picture_coordinates()
            res = self.mapping_relation(items, event)
            if 'success' in res:
                return True
        else:
            res = self.mapping_relation(items=None, event=event)
            return res

    def get_random(self, x):
        '''生成随机pause'''
        res = round(random.uniform(0.1, 0.18), 2)
        return res

    def rander_template(self, **kwargs):
        '''生成模板'''
        env = Environment(loader=FileSystemLoader('./'))
        env.filters['get_random'] = self.get_random
        tpl = env.get_template('./page_template.txt')
        if self.main_event == 'auto_login':
            with open('./{}/template.vdo'.format(self.username), 'w+') as fout:
                render_content = tpl.render(kwargs=kwargs)
                fout.write(render_content)
        self.allocate_vncvdo(path='./{}/template.vdo'.format(self.username))

    def allocate_vncvdo(self, path):
        '''调用vncvdo'''
        args = [path]
        while args:
            cmd = args.pop(0)
            if cmd in ('pause', 'sleep'):
                duration = float(args.pop(0)) / 1
                client.pause(duration)
            elif cmd in ('kdown', 'keydown'):
                key = args.pop(0)
                client.keyDown(key)
            elif cmd in ('kup', 'keyup'):
                key = args.pop(0)
                client.keyUp(key)
            elif cmd in ('move', 'mousemove'):
                x, y = int(args.pop(0)), int(args.pop(0))
                client.mouseMove(x, y)
            elif cmd == 'click':
                button = int(args.pop(0))
                client.mousePress(button)
            elif os.path.isfile(cmd):
                lex = shlex.shlex(open(cmd), posix=True)
                lex.whitespace_split = True
                args = list(lex) + args
            else:
                print('unknown cmd "%s"' % cmd)

    def resolve_capture(self, im, im_type):
        '''解析验证码'''
        try:
            return self.rk_create(im, im_type, timeout=10)['data']['result']
        except Exception as e:
            return '12345'

    def jiequ_capture(self):
        '''截取验证码'''
        img = cv2.imread(r"./{}/screenshot.png".format(self.username))
        cropped = img[467:537, 774:884]  # 裁剪坐标为[y0:y1, x0:x1]
        cv2.imwrite("./{}/cv_cut_thor.png".format(self.username), cropped)
        im = open('./{}/cv_cut_thor.png'.format(self.username), 'rb').read()
        return self.resolve_capture(im, im_type=3000)


class yct_login(Pil_Deal):
    def __init__(self):
        Pil_Deal.__init__(self)
        self.username = '13564118478'
        self.password = '55111134'
        self.main_event = 'auto_login'

    def login_function(self):
        '''登录功能'''
        while True:
            if self.login_recorder():
                if self.auto_login():
                    return '成功登录'

    def auto_login(self):
        '''登录模块'''
        events = ['click_firefox', 'login_appear', 'login_success']
        events_response = ['click_firefox', 'move_login', 'first_login', 'click_capture',
                           'click_capture_again']
        while len(events) > 0:
            event = events[0]
            if 'click_firefox' in event:
                client.captureScreen(r'./{}/screenshot.png'.format(self.username))
                map_table = self.mapping_relation(items=None, event=event)['map']
                if map_table == self.getPngPix(map=map_table):
                    events.pop(0)
                    event_response = events_response[0]
                    with open('./replay/{}.vdo'.format(event_response), mode='r') as folder:
                        text = folder.readlines()
                    self.rander_template(event=event_response, text=text)
            elif 'login_appear' in event:
                client.captureScreen(r'./{}/screenshot.png'.format(self.username))
                map_table = self.mapping_relation(items=None, event=event)['map']
                if map_table == self.getPngPix(map=map_table):
                    events_response.pop(0)
                    event_response = events_response[0]
                    with open('./replay/{}.vdo'.format(event_response), mode='r') as folder:
                        text = folder.readlines()
                    self.rander_template(event=event_response, text=text)
                    events_response.pop(0)
                    events.pop(0)
            elif 'login_success' in event:
                event_response = events_response[0]
                if 'first_login' in event_response:
                    self.rander_template(event=event_response, username=self.username,
                                         password=self.password, capture=self.jiequ_capture())
                    events_response.pop(0)
                    client.captureScreen(r'./{}/screenshot.png'.format(self.username))
                    map_table = self.mapping_relation(items=None, event=event)['map']
                    if map_table == self.getPngPix(map=map_table):
                        return '登录成功'
                elif 'click_capture' in events_response:
                    while True:
                        with open('./replay/{}.vdo'.format(event_response), mode='r') as folder:
                            text = folder.readlines()
                        self.rander_template(event=event_response, text=text)
                        self.rander_template(event=events_response[-1],
                                             capture=self.jiequ_capture())
                        client.captureScreen(r'./{}/screenshot.png'.format(self.username))
                        map_table = self.mapping_relation(items=None, event=event)['map']
                        if map_table == self.getPngPix(map=map_table):
                            return '登录成功'
                        else:
                            continue

    def login_recorder(self):
        '''录制模块'''
        try:
            with open('./{}/auth.json'.format(self.username), 'r') as folder:
                data = json.load(folder)['auto_login_state']
                if 'login' in data:
                    return True
        except IOError as e:
            if self.help_recorder():
                return True

    def help_recorder(self):
        '''生成坐标轨迹'''
        events = ['click_firefox', 'login_appear', 'login_success']
        for event in events:
            client.captureScreen(r'./{}/screenshot.png'.format(self.username))
            self.vnc_screenshot(event)
        with open('./{}/auth.json'.format(self.username), 'w') as folder:
            state = {'auto_login_state': 'login_ready'}
            json.dump(state, folder, ensure_ascii=False)
        return True


yct_login().login_function()
