#!/bin/bash
# -*- coding:utf-8 -*-

import os
import sys
import shutil

import pyzlt

class MergeLib (pyzlt.CommonClass) :
    def __init__(self):
        pyzlt.CommonClass.__init__(self)
        self.continueOrCancelAsk = self.__continueOrCancelAsk
        
    def __continueOrCancelAsk(self,tip,continueStr,cancelStr):
        ask = raw_input("{}({},{})".format(tip,continueStr,cancelStr))
        return ask

    #获取fatlib的指令集列表
    def func_get_fatlib_arch_list(self,libfile):
        result = self.shell_exec("lipo -info " + libfile)
        if not result.success():
            return result
        
        output = result.stdout
        arr = output.split("are:")
        if len(arr) == 1 :
            arr = output.split("architecture:")
        output = arr[-1].strip()
        output = output.split(" ")

        result.resultlist = output
        return result

    #根据指令集 拆分fatlib
    def func_thin_lib_by_arch(self,libfile,dstdir):
        result = self.func_get_fatlib_arch_list(libfile)
        if not result.success():
            return result

        arch_list = result.resultlist
        if len(arch_list) == 1:
            ask = self.continueOrCancelAsk("{}不是fat lib，单指令集架构，是否继续？".format(libfile),"y","n")
            if ask.lower() != "y":
                self.infoPrint("已主动终止")
                if self.continueOrCancelAsk == self.__continueOrCancelAsk:
                    exit(1)
                return result

        libName = os.path.basename(libfile).replace(".a","")
        namelist = []
        for arch in arch_list:
            name = libName + "_"+ arch + ".a"
            namelist.append((arch,dstdir + "/" + name))

            cmdstr = "cd " + dstdir
            if len(arch_list) > 1 : #只有一个指令集
                cmdstr = cmdstr + " && lipo -output {} -thin {} {}".format(name, arch, libfile)
            else:
                cmdstr = cmdstr + " && cp {} {}".format(libfile,name)
            
            result = self.shell_exec(cmdstr)
            if not result.success():
                return result
        result = pyzlt.zl_operate_result()
        result.resultlist = namelist #[(armv7,1_armv7.a),(arm64,1_arm64.a)]
        return result 

    #fat lib
    def func_fat_lib(self,lib_file_list, newLibName , dstdir):
        if len(lib_file_list) < 2:
            return pyzlt.s_operate_success_reult
        
        cmdstr = "cd " + dstdir
        cmdstr += " && lipo -create -output " + newLibName
        for lib in lib_file_list:
            cmdstr += " " + lib
        return self.shell_exec(cmdstr)

    #合并多个lib文件
    def func_merge_libs(self,lib_file_list,newlibName):

        if len(lib_file_list) < 2 :
            return pyzlt.s_operate_success_reult
        
        dstdir = self.currentDir + "/dst_tmp_mergelibs"
        result = self.func_make_empty_dir(dstdir)
        if not result.success():
            return result

        self.infoPrint("thin lib to arch o")
        arch_lib_dict = {} # { armv7:[1.a,2.a],arm64:[3.a,4.a]}
        for libfile in lib_file_list:
            result = self.func_thin_lib_by_arch(libfile,dstdir)
            if not result.success():
                return result
            for (arch,name) in result.resultlist:
                d = arch_lib_dict.get(arch)
                if d == None:
                    d = []
                    arch_lib_dict[arch] = d
                d.append(name)

        self.infoPrint("ar arch o to lib")
        firstLibList = []
        for (arch,liblist) in arch_lib_dict.items():
            if len(liblist) == 0 :
                continue

            archdir = dstdir + "/" + arch
            result = self.shell_exec("mkdir " + archdir)
            if not result.success():
                return result
            
            archlibName = archdir + "/merge_tmp_" + arch + ".a"
            for i in range(len(liblist)):
                objdir = archdir + "/" + os.path.basename(liblist[i])
                cmdstr = "mkdir " + objdir
                cmdstr += " && cd " + objdir
                cmdstr += " && ar -x " + liblist[i]
                result = self.shell_exec(cmdstr)
                if not result.success():
                    return result
                
                for obj in os.listdir(objdir):
                    if not obj.endswith(".o"):
                        continue
                    src =  objdir + "/" + obj
                    dst = archdir + "/" +os.path.basename(liblist[i]) + "_" + obj
                    shutil.move(src,dst)
            cmdstr = "cd " + archdir
            cmdstr += " && ar -rcs "  + archlibName + " *.o" 
            result = self.shell_exec(cmdstr)
            if not result.success():
                return result
            firstLibList.append(archlibName)

        print ("lipo lib to fat lib")
        result = self.func_fat_lib(firstLibList, newlibName, dstdir)
        if not result.success():
            return result
        result = self.shell_exec("rm -fR " + dstdir)
        if not result.success():
            return result
        else:
            self.infoPrint("merge libs end")
            return result

if __name__ == '__main__':    
    print ("python MergeLib -n新库名字 libA libB libC ..." )
    libPathList = []
    newlibName = "dst_mergelibs.a"
    for i in range (1,len(sys.argv)):
        ph = sys.argv[i]
        if ph.startswith == "-n":
            newlibName = ph[len("-n"):]
        else:
            libPathList.append(ph)
    MergeLib().func_merge_libs(libPathList,newlibName)
