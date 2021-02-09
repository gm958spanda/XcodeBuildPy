# -*- coding: UTF-8 -*-

import sys
import os
import json

class GConfig (object):
    
    def __init__(self):
        #合并lib库的路径
        self.mergeLibInputPath = sys.path[0]
        self.mergeLibOutputPath = sys.path[0]

        #构建lib库的路径
        self.buildLibInputPath = sys.path[0]
        self.buildLibOutputPath = sys.path[0]
        self.buildLibTargetDevice= True #真机版
        self.buildLibTargetSimulator = True #模拟器版
        self.buildLibRelease = True #Release or Debug
        self.buildLibBitCode = False #bitcode


        dict = self.loadFromFile()
        for (name,_) in self.__dict__.items():
            value = dict.get(name)
            if value != None:
                self.__setattr__(name,value)

    def loadFromFile(self):
        path = os.path.join(sys.path[0], "gconfig.json")
        if os.path.exists(path):
            try:
                jsonfp = open(path)
                dict = json.load(jsonfp)
                jsonfp.close()
                return dict
            except:
                return {}
        else:
            return {}

    def syncToFile(self):

        dict = {}
        for (name,_) in self.__dict__.items():
            value = self.__getattribute__(name)
            if value != None:
                dict[name] = value

        path = os.path.join(sys.path[0], "gconfig.json")
        if os.path.exists(path):
            os.remove(path)
        jsonfp = open(path ,"w")
        json.dump(dict,jsonfp)
        jsonfp.close()


gConfig = GConfig()