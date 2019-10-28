#!/bin/bash
# -*- coding:utf-8 -*-

import os
import pyzlt

class MergeFramework (pyzlt.MergeLib):
    def __init__(self):
        pyzlt.MergeLib.__init__(self)

        #新framework路径存放目录和名字
        self.new_framework_dir = self.currentDir + "/merge_dst"
        self.new_framework_name = "zl"
        #需要合并的framework存储路径
        self.src_framework_dir = self.currentDir + "/build_fat"
    
    def func_merge_frameworks_libs(self):

        #创建新目录
        self.func_make_empty_dir(self.new_framework_dir)
        new_framework_path = self.new_framework_dir +"/" + self.new_framework_name
        if not new_framework_path.endswith(".framework"):
            new_framework_path += ".framework"
        self.func_make_empty_dir(new_framework_path)

        # 获取所以文件列表
        pathlist = self.func_get_pathlist(self.src_framework_dir)

        #复制资源文件
        for path in pathlist:
            if path.endswith(".bundle") and path.find(".framework/") < 0:
                result = self.shell_exec("cp -R " + path + " " + os.path.dirname(new_framework_path))
                if not result.success():
                    return result

        #获取lib文件列表
        lib_path_list = []
        for path in pathlist:
            if path.endswith(".framework") and path.find(".framework/") < 0:
                name = os.path.basename(path).replace(".framework","")
                lib_path_list.append(os.path.join(path,name))
            elif path.endswith(".a"):
                lib_path_list.append(path)
        
        #合并lib
        result = self.func_merge_libs(lib_path_list,new_framework_path +"/" +self.new_framework_name)
        if not result.success():
            return result
        
        #复制Headers
        self.func_make_empty_dir(new_framework_path + "/Headers")
        for path in pathlist:
            if path.endswith(".framework"):
                name = os.path.basename(path).replace(".framework","")
                cmdstr = "cp -R " + path + "/Headers" +" " + new_framework_path + "/Headers/" + name
                result = self.shell_exec(cmdstr)
                if not result.success():
                    return result

        #修改头文件
        pathlist = self.func_get_pathlist(new_framework_path + "/Headers")
        module_headers_dict = {} # { FireflyBasekit/xxx.h : None }
        for path in pathlist:
            if os.path.isdir(path):
                continue
            name = os.path.basename(path)
            moduleName = os.path.basename(os.path.dirname(path))
            module_headers_dict["{}/{}".format(moduleName.lower(),name.lower())] = None

        headerfs = open(new_framework_path + "/Headers/" + self.new_framework_name +".h","w")
        for path in pathlist:
            if os.path.isdir(path):
                continue
            name = os.path.basename(path)
            moduleName = os.path.basename(os.path.dirname(path))
            headerfs.write("#import <{}/{}/{}>\r\n".format(self.new_framework_name,moduleName,name))
            
            tmpfs = open (path,"r")
            content_lines = tmpfs.readlines()
            tmpfs.close()
            for i in range(len(content_lines)):
                line = content_lines[i]
                if line.find("import") < 0 or line.find("#") < 0:
                    continue
                
                left_index = line.find("<")
                if left_index < 0 :
                    continue
                right_index = line.rfind(">")
                if right_index < 0 :
                    continue
                if right_index < left_index:
                    continue

                name = line[left_index + 1 : right_index]
                arr = name.split("/")
                if len(arr) == 2 :
                    (moduleName,name) =  arr
                    if module_headers_dict.get("{}/{}".format(moduleName.lower(),name.lower())) != None:
                        line = line.replace("<","<"+self.new_framework_name + "/")
                        content_lines[i] = line
                
            tmpfs = open (path,"w")
            tmpfs.writelines(content_lines)
            tmpfs.close()
            
        headerfs.close()
        return pyzlt.s_operate_success_reult