# -*- coding: UTF-8 -*-

import os
import subprocess

class zl_operate_result:
    def __init__(self):
        #标准输出
        self.stderr = None
        self.stdout = None
        self.returncode = 0

        self.stderrPrint = None
        self.stdoutPrint = None
        #操作结果
        self.resultlist = []

    def success(self):
        return self.returncode == 0

s_operate_success_reult = zl_operate_result()

def shell_exec(cmdstr, result):
    proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
    while proc.poll() is None:
        for line in iter(proc.stdout.readline, b''):
            s = str(line)
            result.stdoutPrint(s)
            if result.stdout == None:
                result.stdout = [s]
            else:
                result.stdout.append(s)

    proc.wait()
    if result.stdout != None:
        result.stdout = "\n".join(result.stdout)
    result.stderr = proc.stderr.read()
    result.returncode = proc.returncode
