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
    
    #设置xcode版本
    def func_setXcodeBuilPath(self,path):
        if path.find(".app") > -1 and path.find("xcode") > -1:
            path = os.path.join(path,"Contents/Developer/usr/bin/xcodebuild")
            if os.path.exists(path):
                self.XcodeBuild = path

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
        
        #生成dsym符号
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
            flags += " -configuration Release"
        else:
            flags += " -configuration Debug"

        return flags

    def func_get_iphoneos_output(self):
        return os.path.join(self.BuildOutPutPath,"out_iphoneos")
    def func_get_iphonesimulator_output(self):
        return os.path.join(self.BuildOutPutPath,"out_iphonesimulator")
    def func_get_fatlib_output(self):
        return os.path.join(self.BuildOutPutPath,"out_fatlib")
    #构建真机版
    def func_build_iphoneos(self):
        BUILD_DIR = self.func_get_iphoneos_output()
        if os.path.exists(BUILD_DIR):
            self.shell_exec("rm -fR {}".format(BUILD_DIR))
        flags = self.func_xcodebuild_cmdstr()
        shellCMD = flags + " -sdk iphoneos BUILD_DIR={} clean build".format(BUILD_DIR)
        return self.shell_exec(shellCMD)
    
    #构建模拟器版
    def func_build_iphonesimulator(self):
        BUILD_DIR = self.func_get_iphonesimulator_output()
        if os.path.exists(BUILD_DIR):
            self.shell_exec("rm -fR {}".format(BUILD_DIR))
        flags = self.func_xcodebuild_cmdstr()
        shellCMD = flags + " -arch x86_64 -arch i386 -sdk iphonesimulator BUILD_DIR={} clean build".format(BUILD_DIR)
        return self.shell_exec(shellCMD)

    #fatlib
    def func_fatlib_after_build(self):
        fatlib_dir = self.func_get_fatlib_output()
        configuration = None
        if self.Release :
            configuration = "Release"
        else:
            configuration = "Debug"

        if os.path.exists(fatlib_dir):
            result = self.shell_exec("rm -fR " + fatlib_dir)
        os.makedirs(fatlib_dir)

        tmppath = os.path.join(self.func_get_iphoneos_output(),configuration+"-iphoneos")
        for buildOutput in self.func_get_pathlist(tmppath):
            # 输出是framework
            if buildOutput.endswith(".framework"):
                framework = buildOutput

                baseName = os.path.basename(framework)
                libname = baseName.replace(".framework","")
                if baseName.startswith("Pods_"):
                    continue
                
                targetframework = os.path.join(fatlib_dir ,libname)
                self.func_make_empty_dir(targetframework)
                targetframework = os.path.join(targetframework, baseName)
                self.func_make_empty_dir(targetframework)

                lipo_iphoneos = framework
                copyCMD = "cp -R " + lipo_iphoneos + "/Headers "+targetframework+"/Headers "
                copyCMD = copyCMD + " && cp " + lipo_iphoneos + "/Info.plist " +targetframework
                copyCMD = copyCMD + " && cp -R " + lipo_iphoneos + "/Modules " +targetframework+"/Modules "
                copyCMD = copyCMD + " && cp " + lipo_iphoneos + "/" + libname + " " +targetframework

                result = self.shell_exec(copyCMD)
                if not result.success():
                    return result

                lipoDST = os.path.join(targetframework ,libname)
                lipoSRC_iphoneos = os.path.join(lipo_iphoneos ,libname)
                lipoSRC_iphonesimulator = lipoSRC_iphoneos.replace(self.func_get_iphoneos_output(),self.func_get_iphonesimulator_output())
                lipoSRC_iphonesimulator = lipoSRC_iphonesimulator.replace("{}-iphoneos".format(configuration),"{}-iphonesimulator".format(configuration))
                lipoCMD = "lipo -create -output " + lipoDST + " " + lipoSRC_iphoneos + " " + lipoSRC_iphonesimulator
                result = self.shell_exec(lipoCMD)
                if not result.success():
                    return result
            #输出是libxxx.a
            elif buildOutput.endswith(".a"):
                libMainName = self.Scheme
                if buildOutput == "lib{}.a".format(libMainName): #是指定构建的scheme
                    libpath = buildOutput
                    
                    lipoDST = os.path.join(fatlib_dir, libMainName)
                    self.func_make_empty_dir(lipoDST)
                    #复制头文件
                    copyCMD = "cp -R " + os.path.dirname(libpath) + "/include/"+libMainName+" "+lipoDST+"/include "
                    result = self.shell_exec(copyCMD)
                    if not result.success():
                        return result
                    
                    lipoDST = lipoDST + "/" + libname
                    
                    #合并lib => fat lib
                    lipo_iphoneos = libpath
                    lipoSRC_iphoneos = libpath
                    lipoSRC_iphonesimulator = lipoSRC_iphoneos.replace(self.func_get_iphoneos_output() ,self.func_get_iphonesimulator_output())
                    lipoSRC_iphonesimulator = lipoSRC_iphonesimulator.replace("{}-iphoneos".format(configuration),"{}-iphonesimulator".format(configuration))
                    lipoCMD = "lipo -create -output " + lipoDST + " " + lipoSRC_iphoneos + " " + lipoSRC_iphonesimulator
                    result = self.shell_exec(lipoCMD)
                    if not result.success():
                        return result
        return pyzlt.s_operate_success_reult


class XcodeBuildUtil:
    @classmethod
    def schemeListOfWorkSpace(self,workspacePath):
        ret = pyzlt.zl_operate_result()
        pyzlt.shell_exec("xcodebuild -list -workspace {}".format(workspacePath),ret)
        stdout = ret.stdout

        schemeslist = None
        if stdout != None:
            for line in  stdout.split("\n"):
                line = line.strip()
                if len(line) == 0 or line.startswith("Pods-"):
                    continue
                if line == "Schemes:":
                    schemeslist = []
                elif schemeslist != None:
                    schemeslist.append(line)
        if schemeslist == None:
            schemeslist = []
        return schemeslist


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
