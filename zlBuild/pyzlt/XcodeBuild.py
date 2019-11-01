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

        is_iphoneos_output_exits = True
        tmppath = os.path.join(self.func_get_iphoneos_output(),configuration+"-iphoneos")
        if not os.path.exists(self.func_get_iphoneos_output()): 
            #真基版本不存在,尝试使用模拟器版本
            is_iphoneos_output_exits = False
            tmppath = os.path.join(self.func_get_iphonesimulator_output(),configuration+"-iphonesimulator")

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
                
                #只有真机版本和模拟器版本同时存在才需要fatlib操作
                if is_iphoneos_output_exits and os.path.exists(self.func_get_iphonesimulator_output()):
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
                    
                    #只有真机版本和模拟器版本同时存在才需要fatlib操作
                    if is_iphoneos_output_exits and os.path.exists(self.func_get_iphonesimulator_output()):
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
            
        #删除合并前产物（真机和模拟器）
        dir = self.func_get_iphoneos_output()
        if os.path.exists(dir):
            self.shell_exec("rm -fR " + dir)
        dir = self.func_get_iphonesimulator_output()
        if os.path.exists(dir):
            self.shell_exec("rm -fR " + dir)
        return pyzlt.s_operate_success_reult

    #复制资源和依赖库到构建输出目录
    def func_copy_static_libs_resource(self):
        pods_dir = os.path.join( os.path.dirname(self.WorkSpacePath), "Pods")
        
        #通过解析Pod sh文件，获取资源文件路径
        def func_parse_pod_sheme_resources(scheme): 
            shfile = os.path.join(pods_dir ,"Target Support Files/Pods-{}".format(scheme),"Pods-{}-resources.sh".format(scheme))
            if not os.path.exists (shfile):
                return []
            ret = {}
            fs = open(shfile)
            lines = fs.readlines()
            fs.close()
            for line in lines:
                if line.lstrip().startswith("install_resource "):
                    start = '${PODS_ROOT}/'
                    end = '"'
                    line = line[line.find(start) + len(start) : line.rfind(end)]
                    ret[line] = None
            return ret.keys()
        
        #通过解析Pod xcconfg文件 获取依赖库路径
        def func_parse_pod_sheme_SEARCH_PATHS(scheme):
            configfile = os.path.join(pods_dir ,"Target Support Files/Pods-{}".format(scheme),"Pods-{}.release.xcconfig".format(scheme))
            if not os.path.exists (configfile):
                return []
            ret = {}
            fs = open(configfile)
            lines = fs.readlines()
            fs.close()
            for line in lines:
                if line.lstrip().startswith("FRAMEWORK_SEARCH_PATHS"):
                    for item in line.split(" "):
                        item = item.strip()
                        if len(item) == 0:
                            continue
                        if item.startswith('"${PODS'):
                            item = item[item.rfind("/")+1:].replace('"',"")
                            item = os.path.basename(item)
                            ret[item] = None
                if line.lstrip().startswith("LIBRARY_SEARCH_PATHS"):
                    for item in line.split(" "):
                        item = item.strip()
                        if len(item) == 0:
                            continue
                        if item.startswith('"${PODS_ROOT}/'):
                            item = item.replace('"${PODS_ROOT}/',"").replace('"',"")
                            k = item.find("/")
                            if k > 0 :
                                item = item[0: k]
                            ret[item] = None
            return ret.keys()

        def func_get_all_shemes():
            def pp_func_parse_pod_shemes(ret,scheme):
                for i in func_parse_pod_sheme_SEARCH_PATHS(scheme):
                    pp_func_parse_pod_shemes(ret,i)
                ret[scheme] = None
            
            ret = {}
            pp_func_parse_pod_shemes(ret,self.Scheme)
            return ret.keys()
        
        g_res_copied = {}
        for scheme in func_get_all_shemes():
            # 复制资源
            for res in func_parse_pod_sheme_resources(scheme):
                if g_res_copied.has_key(res):
                    continue
                g_res_copied[res] = None
                dst_dir = os.path.join(self.func_get_fatlib_output(), res[:res.find("/")])

                self.func_make_dir_if_not_exist(dst_dir)
                res = os.path.join(pods_dir,res)
                copyCMD = "cp -R " + res + " " + dst_dir 
                result = self.shell_exec(copyCMD)
                if not result.success():
                    return result
            
            #复制 lib 和framework
            if self.Scheme == scheme: #此时，会构建新的framework，不从Pods中拷贝
                continue
            for lib in self.func_get_pathlist(pods_dir + "/" + scheme):
                if lib.find(".framework/") > 0 :
                    continue
                if lib.endswith(".a") or lib.endswith(".framework"):
                    dst_dir = os.path.join(self.func_get_fatlib_output(),scheme)
                    self.func_make_dir_if_not_exist(dst_dir)
                    tmp = dst_dir + "/" + os.path.basename(lib)
                    if not os.path.exists(tmp):
                        copyCMD = "cp -R " + lib + " " + tmp
                        result = self.shell_exec(copyCMD)
                        if not result.success():
                            return result
        # scheme自身的资源文件复制
        # for (scheme, config) in self.schemelist.items():
        #     dst_dir = self.build_dst_dir + "/" + scheme
        #     self.func_make_dir_if_not_exist(dst_dir)
        #     if config.has_key("resources"):
        #         reslist = config["resources"]
        #         for res in reslist:
        #             respath = os.path.join(os.path.dirname(self.podfileJsonPath) ,res )
        #             copyCMD = "cp -R " +  respath + " " + dst_dir
        #             self.func_shell(copyCMD)
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
