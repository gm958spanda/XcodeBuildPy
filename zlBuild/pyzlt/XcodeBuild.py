#!/bin/bash
# -*- coding:utf-8 -*-

import os
import sys

import pyzlt

class XcodeBuild (pyzlt.CommonClass) :
    def __init__(self):
        pyzlt.CommonClass.__init__(self)

        #输出路径
        self.BuildOutPutPath = os.path.join(sys.path[0],"BuildOutPut")
        
        #xcodebuild的版本，若要指定版本，需要指定XcodeBuild的具体路径
        #或者使用func_setXcodeBuilPath
        self.XcodeBuild = "xcodebuild"

        #workspace 路径
        self.WorkSpacePath = ""
        self.Scheme = ""

        #Debug or Release
        self.Release = True 

        #安静模式
        self.Quiet = True

        #bitcode
        self.Enable_BitCode = False

        #Link Frameworks Automatically
        self.Link_Frameworks_Automatically = False
    
    def func_xcodebuild_cmdstr(self):
        flags = self.XcodeBuild
        # bitcode
        if self.Enable_BitCode:
            flags += " ENABLE_BITCODE=YES"
        else :
            flags += " ENABLE_BITCODE=NO"
        
        #CLANG_MODULES_AUTOLINK  Link Frameworks Automatically
        if self.Link_Frameworks_Automatically:
            flags += " CLANG_MODULES_AUTOLINK=NO"
        else:
            flags += " CLANG_MODULES_AUTOLINK=YES"
        
        #dsym符号
        #flags += 'DEBUG_INFORMATION_FORMAT="dwarf-with-dsym"'

        #ONLY_ACTIVE_ARCH
        flags += " ONLY_ACTIVE_ARCH=NO"

        #安静模式
        if self.Quiet:
            flags += " -quiet"
        
        #workspace
        flags += " -workspace {}".format(self.WorkSpacePath)
        #scheme
        flags += " -scheme {}".format(self.Scheme)

        #Debug or Releae
        if self.Release:    
            flags += " -configuration Debug"
        else:
            flags += " -configuration Release"

        return flags

    #构建真机版
    def func_build_iphoneos(self):
        flags = self.func_xcodebuild_cmdstr()
        shellCMD = flags + " -sdk iphoneos BUILD_DIR={} clean build".format(self.func_get_iphoneos_output())
        self.func_shell(shellCMD)
    
    #构建模拟器版
    def func_build_iphonesimulator(self):
        flags = self.func_xcodebuild_cmdstr()
        shellCMD = flags + " -arch x86_64 -arch i386 -sdk iphonesimulator BUILD_DIR={} clean build".format(self.func_get_iphonesimulator_output())
        self.func_shell(shellCMD)

    def func_get_iphoneos_output(self):
        return os.path.join(self.BuildOutPutPath,"iphoneos")
    def func_get_iphonesimulator_output(self):
        return os.path.join(self.BuildOutPutPath,"iphonesimulator")

    #设置xcode版本
    def func_setXcodeBuilPath(self,path):
        if path.find(".app") > -1 and path.find("xcode") > -1:
            path = os.path.join(path,"Contents/Developer/usr/bin/xcodebuild")
            if os.path.exists(path):
                self.XcodeBuild = path

if __name__ == '__main__':    
    pass
    # print ("python MergeLib -n新库名字 libA libB libC ..." )
    # libPathList = []
    # newlibName = "dst_mergelibs.a"
    # for i in range (1,len(sys.argv)):
    #     ph = sys.argv[i]
    #     if ph.startswith == "-n":
    #         newlibName = ph[len("-n"):]
    #     else:
    #         libPathList.append(ph)
    # MergeLib().func_merge_libs(libPathList,newlibName)
