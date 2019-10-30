#!/bin/bash
# -*- coding:utf-8 -*-

import os
import sys

class GitClass:
    # 初始化
    def  __init__(self ,git_dir):
        self.git_dir = git_dir
    
    # 有未提交或未推送的更改
    def func_changed_not_commit_push(self):
        git_status_info = self.func_status_info()
        if git_status_info.find("Your branch is ahead of") > 0 :
            return True
        if git_status_info.find("Changes not staged for commit") > 0:
            return True
        return False

    # git status
    def func_status_info(self):
        process = os.popen("cd {}  &&  git status".format(self.git_dir))
        status_info = process.read()
        process.close()

        return status_info

    # 分支信息  
    def func_branch_info(self):
        process = os.popen("cd {}  &&  git branch -vv".format(self.git_dir))
        branch_info = process.read()
        process.close()

        return branch_info
    
    # 当前分支信息
    def func_current_branch_info(self):
        branch_info = self.func_branch_info()
        for line in branch_info.split("\n"):
            if (line.startswith("*")):
                return line
        
        return None

    # 当前分支的节点hash
    def func_current_branch_head_commit_hash(self):
        process = os.popen("cd {}  &&  git rev-parse HEAD".format(self.git_dir))
        commit_hash = process.read().strip()
        process.close()

        return commit_hash
    
    # 分支的节点hash
    def func_branch_head_commit_hash(self,branch_name):
        process = os.popen("cd {}  &&  git rev-parse {}".format(self.git_dir , branch_name ))
        commit_hash = process.read().strip()
        process.close()

        return commit_hash

    def func_all_remote_branches(self):
        process = os.popen("cd {}  &&  git branch --list -a".format(self.git_dir))
        str = process.read()
        process.close()

        arr = []
        for line in str.split("\n"):
            if line.find("remotes/origin") > 0 and line.find("->") < 0:
                name = line.split("/")[-1]
                arr.append(name)
        return arr
