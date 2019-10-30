#!/bin/bash
# -*- coding:utf-8 -*-

import os
import sys
from CommonClass import CommonClass

class PodSpecClass (CommonClass) :
    # 初始化
    def  __init__(self ,podspec_path):
        self.spec_path = podspec_path
        self.content_lines = None
    
    def func_change_podspec_path(self,podspec_path):
        self.spec_path = podspec_path
    #读取内容
    def func_read_contentlines(self):
        if not os.path.exists(self.spec_path)  or os.path.isdir(self.spec_path):
            self.func_print_error("{} 不存在或者不是文件".format(self.spec_path))

        tmpfs = open(self.spec_path)
        self.content_lines = tmpfs.readlines()
        tmpfs.close()
    #保存内容
    def func_save_contentlines(self):
        tmpfs = open(self.spec_path,"w")
        tmpfs.writelines(self.content_lines)
        tmpfs.close()
    def func_get_current_version(self) :
        for i in range(len(self.content_lines)):
            line = self.content_lines[i]
            if line.find(".version") > 0 and line.find(".source") < 0:
                oldver = line[line.find("'")+1:]
                oldver = oldver[:oldver.find("'")]
                return oldver
    #升级版本号
    def func_increase_version(self) :
        for i in range(len(self.content_lines)):
            line = self.content_lines[i]
            if line.find(".version") > 0 and line.find(".source") < 0:
                oldver = line[line.find("'")+1:]
                oldver = oldver[:oldver.find("'")]
                arr = list(oldver.split("."))
                arr[-1] = "{}".format(int(arr[-1]) +1)
                ver_str = ".".join(arr)
                self.content_lines[i] = line.replace(oldver,ver_str)
                return ver_str
    #设置描述
    def func_set_desc(self,desc):
        n_desc_begin = 0
        n_desc_end = 0
        for i in range(len(self.content_lines)):
            line = self.content_lines[i]
            if line.find("<<-DESC") > 0 and line.find(".description") > 0:
                n_desc_begin = i
            elif n_desc_begin > 0 and line.find("DESC")>0:
                n_desc_end = i
                break
        if type(desc) == type([]):
            self.content_lines = self.content_lines[:n_desc_begin+1] + desc + self.content_lines[n_desc_end:]
        elif type(desc) == type(""):
            self.content_lines = self.content_lines[:n_desc_begin+1] + [desc] + self.content_lines[n_desc_end:]
    
    #设置源代码路径 使用commint提交点的hash
    def func_set_source_using_commit(self ,commit_hash):
        for j in range(len(self.content_lines)):
            line = self.content_lines[j]
            if line.find(".source") > 0 :
                arr = line.split(",")
                for k in range(len(arr)):
                    if arr[k].find(":tag") >= 0 or arr[k].find(":commit")>=0 or arr[k].find(":branch") >=0 :
                        s = " :commit => '{}'".format(commit_hash)
                        if k == len(arr) -1:
                            s += " }\n"
                        arr[k] = s
                        break

                self.content_lines[j] = ",".join(arr)
                break
    
    #设置源代码路径 使用branch 
    def func_set_source_using_branch(self ,branch_name):
        for i in range(len(self.content_lines)):
            line = self.content_lines[i]
            if line.find(".source") > 0 :
                arr = line.split(",")
                for k in range(len(arr)):
                    if arr[k].find(":tag") >= 0 or arr[k].find(":commit")>=0 or arr[k].find(":branch") >=0 :
                        s = ":branch => '{}'".format(branch_name)
                        if k == len(arr) -1:
                            s += " }\n"
                        arr[k] = s
                        break

                self.content_lines[i] = ",".join(arr)
                break
