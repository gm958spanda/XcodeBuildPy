#!/bin/bash
# -*- coding:utf-8 -*-

import os
import sys
import pyzlt.Shellexec

class CommonClass:
    def __init__(self):
        self.currentDir = sys.path[0]#脚本目录
        self.errorPrint = self.__print
        self.infoPrint = self.__print

    def __print(self,str):
        print(str)

    #执行shell命令
    def shell_exec(self,cmdStr):
        result = pyzlt.Shellexec.zl_operate_result()
        result.stdoutPrint = self.infoPrint
        result.stderrPrint = self.errorPrint

        pyzlt.Shellexec.shell_exec(cmdStr,result)
        if result.stderr != None:
            if self.errorPrint == self.__print:
                self.errorPrint("\033[7;31m{}\r\n{}\033[0;;m".format(result.stderr,cmdStr))
                exit(1)
            else:
                self.errorPrint("{}\r\n{}".format(result.stderr,cmdStr))
        return result
    
    #强制创建空文件夹
    def func_make_empty_dir(self,dir):
        if os.path.exists(dir):
            result = self.shell_exec("rm -fR " + dir)
            if not result.success():
                return result
        return self.shell_exec("mkdir " + dir)


    #如果不存在，则创建文件夹
    def func_make_dir_if_not_exist(self,dir):
        if not os.path.exists(dir):
            return self.shell_exec("mkdir " + dir)
        return pyzlt.s_operate_success_reult

    #递归获取文件夹下的文件路径
    def func_get_pathlist(self,dir):
        pathlist = []
        def pp_func_pathlist(dirpath):
            if not os.path.exists(dirpath):
                return
            for ph in os.listdir(dirpath):
                sub = os.path.join(dirpath, ph)
                if os.path.isdir(sub):
                    pathlist.append(sub)
                    pp_func_pathlist(sub)
                else:
                    pathlist.append(sub)
        pp_func_pathlist(dir)
        return pathlist

    #执行shell命令
    def func_shell(self,cmdStr):
        result = self.shell_exec(cmdStr)
        if result.success():
            if not result.stdout == None and not self.infoPrint == None:
                self.infoPrint(result.stdout)
            return result.stdout
        else:
            self.errorPrint("\033[7;31m{}\r\n{}\033[0;;m".format(result.stderr,cmdStr))
            if self.errorPrint == self.__print:
                exit(1)
        return None
    #打印错误
    def func_print_error(self,str):
        print('\033[7;31m{} \033[0;;m'.format(str))
    
