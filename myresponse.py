#!/usr/bin/env python
# coding=utf-8
import os
import glob
import numpy as np
import json
from flask import request, render_template, redirect, url_for


class DataResponse(object):
    def __init__(self, fp_result='grade.txt'):
        self.fp_result = fp_result
        self.Finish = False

    def login(self):
        self.user = request.form['user']
        self.conf_dir = os.path.join("user",self.user)
        os.makedirs(self.conf_dir, exist_ok=True)
        self.conf_path = os.path.join(self.conf_dir,"configure.json")
        try:
            self.configure()
        except:
            print("configure...")
        if not os.path.exists(self.conf_path):
            return redirect(url_for('conf'))
        else:
            return redirect(url_for('work'))

    def load_cpt(self):
        with open(self.OutPath, 'r') as fp:
            cpt = fp.readlines()
            cpt = [i[:-1].split(',') for i in cpt]
        self.cpt = np.array(cpt)
        self.ind_tocheck = np.argwhere(self.cpt[:, 1] == '-1').reshape(-1)
        self.ind_tocheck_len = len(self.ind_tocheck)

    def getfiles_init(self):
        files = glob.glob(os.path.join(self.dir, '*.png'))
        self.fps = [i.replace(self.dir + '/', '') for i in files]
        self.fps = np.sort(self.fps)
        self.ranks = np.ones(self.fps.shape[0], dtype=np.int32) * -1
        with open(self.OutPath, 'w') as fp:
            for i in range(len(self.fps)):
                temp = "{},{}".format(self.fps[i], self.ranks[i])
                fp.writelines(temp + '\n')
        self.prop = {'index': -1, 'code': -1, 'path': ''}

    def _save_conf(self):
        conf = dict(request.form)
        conf_json = json.dumps(conf)
        with open(self.conf_path, 'w') as fp:
            fp.write(conf_json)

    def _load_conf(self):
        with open(self.conf_path, 'r') as fp:
            json_string = fp.readline()
        return json.loads(json_string)

    def getConf(self):
        message = self._load_conf()
        print(message)
        return message

    def _configure(self):
        self._save_conf()
        self.configure()
        return redirect(url_for('work'))

    def configure(self):
        try:
            self.save()  #save result
        except:
            pass
        conf = self._load_conf()
        self.dir = conf['dir']
        self.keys = {}
        self.keys[conf['A']] = {'rank': '1', 'next': 1}
        self.keys[conf['B']] = {'rank': '2', 'next': 1}
        self.keys[conf['C']] = {'rank': '3', 'next': 1}
        self.keys[conf['N']] = {'rank': '0', 'next': 1}
        self.keys[conf['next']] = {'next': 1}
        self.keys[conf['pre']] = {'next': -1}
        self.keys['-1'] = {'next': 0}

        dir_result = os.path.join(self.conf_dir, 'result')
        os.makedirs(dir_result, exist_ok=True)
        self.OutPath = os.path.join(dir_result, self.fp_result)
        print(self.OutPath)
        if not os.path.exists(self.OutPath):
            self.getfiles_init()
        self.load_cpt()

    def save(self):
        print('saving')
        with open(self.OutPath, 'w') as fp:
            for i in range(len(self.cpt)):
                text = self.cpt[i]
                temp = "{},{}".format(text[0], text[1])
                fp.writelines(temp + '\n')

    def autosave(self):
        self.save()
        return "0"

    def _get(self):
        index = int(request.args.get('index'))
        path = request.args.get('path')
        isinit = path == ""
        code = request.args.get('code')
        if not isinit:
            assert self.cpt[self.ind_tocheck[index]][0] == path, (
                index, path, self.cpt[self.ind_tocheck[index]][0])
        else:
            index = 0
            path = self.cpt[self.ind_tocheck[index]][0]
            code = '-1'
        self.prop = {'index': index, 'code': code, 'path': path}

    def _method(self):
        code = self.prop['code']
        index = self.prop['index']
        if 'rank' in self.keys[code]:
            self.Rank = self.keys[code]['rank']
        else:
            if self.cpt[self.ind_tocheck[index]][1] == '-1':
                self.Rank = 0
            else:
                self.Rank = self.cpt[self.ind_tocheck[index]][1]
        self.Next = self.keys[code]['next']

    def _next(self):
        response = {}
        index = self.prop['index']
        new_ind = self.Next + index
        if new_ind >= self.ind_tocheck_len:
            self.save()
            self.Finish = True
            new_ind = 0
            response['finish'] = self.Finish
        new_rank = self.cpt[self.ind_tocheck[new_ind]][1]
        new_path = self.cpt[self.ind_tocheck[new_ind]][0]
        response['index'] = new_ind
        response['rank'] = new_rank
        response['path'] = new_path
        response['finish'] = self.Finish
        response['len'] = self.ind_tocheck_len
        response['oldRank'] = self.Rank
        return response

    def response(self):
        res = self._next()
        return res

    def step(self):
        self._get()
        self._method()
        # update rank
        self.cpt[self.ind_tocheck[self.prop['index']]][1] = self.Rank
        # next image
        res = self._next()
        print(res)
        return res

    def page_finish(self):
        self.Finish = False
        return "Finish!"

    def __call__(self):
        message = self.step()
        return message


if __name__ == "__main__":
    dr = DataResponse('/home/mtx/git/ranklens/data')
