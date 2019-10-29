# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Oct 23 17:45:09 2019
#

import wx
# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

import time
import os
import thread

from GConfig import gConfig
from pyzlt import XcodeBuild,XcodeBuildUtil

class buildLibDialog(wx.Dialog):
    def __init__(self, *args, **kwds):

        # begin wxGlade: buildLibDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("dialog")
        
        sizer_1 = wx.FlexGridSizer(8, 1, 10, 2)
        
        grid_sizer_1 = wx.FlexGridSizer(2, 3, 10, 3)
        sizer_1.Add(grid_sizer_1, 10, wx.EXPAND, 0)
        
        static_text_1 = wx.StaticText(self, wx.ID_ANY, u"工程路径")
        static_text_1.SetMinSize((60, 16))
        grid_sizer_1.Add(static_text_1, 0, 0, 0)
        
        self.inputWorkProjectPathTextView = wx.TextCtrl(self, wx.ID_ANY, "")
        self.inputWorkProjectPathTextView.SetMinSize((600, 22))
        grid_sizer_1.Add(self.inputWorkProjectPathTextView, 0, 0, 0)
        
        self.workProjectPathButton = wx.Button(self, wx.ID_ANY, u"选择路径")
        grid_sizer_1.Add(self.workProjectPathButton, 0, 0, 0)
        
        static_text_2 = wx.StaticText(self, wx.ID_ANY, u"输出路径")
        static_text_2.SetMinSize((60, 16))
        grid_sizer_1.Add(static_text_2, 0, 0, 0)
        
        self.outputLibPathTextView = wx.TextCtrl(self, wx.ID_ANY, "")
        self.outputLibPathTextView.SetMinSize((600, 22))
        grid_sizer_1.Add(self.outputLibPathTextView, 0, 0, 0)
        
        self.outputLibPathButton = wx.Button(self, wx.ID_ANY, u"选择路径")
        grid_sizer_1.Add(self.outputLibPathButton, 0, 0, 0)
        
        grid_sizer_4 = wx.GridSizer(1, 2, 0, 0)
        sizer_1.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        
        static_text_3 = wx.StaticText(self, wx.ID_ANY, u"编译项")
        grid_sizer_4.Add(static_text_3, 0, wx.EXPAND, 0)
        
        self.combo_box_scheme_targets = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        grid_sizer_4.Add(self.combo_box_scheme_targets, 0, wx.EXPAND, 0)
        
        sizer_1.Add((0, 0), 0, 0, 0)
        
        sizer_1.Add((0, 0), 0, 0, 0)
        
        sizer_1.Add((0, 0), 0, 0, 0)
        
        grid_sizer_2 = wx.GridSizer(1, 3, 0, 0)
        sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        
        self.check_list_box_RunEnv = wx.CheckListBox(self, wx.ID_ANY, choices=[u"真机", u"模拟器"])
        self.check_list_box_RunEnv.SetSelection(0)
        grid_sizer_2.Add(self.check_list_box_RunEnv, 0, wx.EXPAND, 0)
        
        self.radio_box_ReleaseDebug = wx.RadioBox(self, wx.ID_ANY, u"配置类型", choices=["Release", "Debug"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.radio_box_ReleaseDebug.SetSelection(0)
        grid_sizer_2.Add(self.radio_box_ReleaseDebug, 0, 0, 0)
        
        grid_sizer_2.Add((0, 0), 0, 0, 0)
        
        sizer_2 = wx.GridSizer(1, 1, 0, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        
        self.buildButton = wx.Button(self, wx.ID_ANY, u"构建")
        sizer_2.Add(self.buildButton, 0, wx.ALIGN_CENTER, 0)
        
        grid_sizer_3 = wx.FlexGridSizer(1, 1, 0, 0)
        sizer_1.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        
        self.printTextView = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_NOHIDESEL | wx.TE_READONLY)
        self.printTextView.SetMinSize((750, 300))
        grid_sizer_3.Add(self.printTextView, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onClickLibPathButton, self.workProjectPathButton)
        self.Bind(wx.EVT_BUTTON, self.onClickOutputLibPathButton, self.outputLibPathButton)
        self.Bind(wx.EVT_CHECKLISTBOX, self.onCheckListBoxRunEnv, self.check_list_box_RunEnv)
        self.Bind(wx.EVT_RADIOBOX, self.onRadioBoxReleaseDebug, self.radio_box_ReleaseDebug)
        self.Bind(wx.EVT_BUTTON, self.onClickBuildButton, self.buildButton)
        # end wxGlade

        self.inputWorkProjectPathTextView.SetValue(gConfig.buildLibInputPath)
        self.loadSchemeTargetList(gConfig.buildLibInputPath)
        self.outputLibPathTextView.SetValue(gConfig.buildLibOutputPath)
        arr = []
        if gConfig.buildLibTargetDevice :
            arr.append(0)
        if gConfig.buildLibTargetSimulator:
            arr.append(1)
        self.check_list_box_RunEnv.SetCheckedItems(arr)
        if gConfig.buildLibRelease:
            self.radio_box_ReleaseDebug.SetSelection(0)
        else:
            self.radio_box_ReleaseDebug.SetSelection(1)

    def loadSchemeTargetList(self,path):
        def __loadSchemeTargetList(path):
            arr = []
            if path.endswith(".xcworkspace"):
                arr = XcodeBuildUtil.schemeListOfWorkSpace(path)
            self.combo_box_scheme_targets.SetItems(arr)
        wx.CallAfter(__loadSchemeTargetList,path)

    def onClickLibPathButton(self, event):  # wxGlade: buildLibDialog.<event_handler>
        picker = wx.FileDialog(self)
        picker.SetPath(gConfig.buildLibInputPath)
        if picker.ShowModal() != wx.ID_CANCEL :
            path = picker.GetPath()
            gConfig.buildLibInputPath = path
            self.inputWorkProjectPathTextView.SetValue(path)
            self.loadSchemeTargetList(path)
                
        event.Skip()

    def onClickOutputLibPathButton(self, event):  # wxGlade: buildLibDialog.<event_handler>
        picker = wx.DirDialog(self)
        picker.SetPath(gConfig.buildLibOutputPath)
        if picker.ShowModal() != wx.ID_CANCEL :
            path = picker.GetPath()
            gConfig.buildLibOutputPath = path
            self.outputLibPathTextView.SetValue(path)
        event.Skip()
    
    def onClickBuildButton(self, event):  # wxGlade: buildLibDialog.<event_handler>
        self.printTextView.Value = ""
        if self.outputLibPathTextView.Value.lower().startswith(self.inputWorkProjectPathTextView.Value.lower()):
            self.infoPrint("输出路径不能等于工程路径，或是其子目录")
            return
        
        def start():
            self.infoPrint("***************开始构建***************")

            arrIndexes  = self.check_list_box_RunEnv.GetCheckedItems()
            arrStrs =  self.check_list_box_RunEnv.GetCheckedStrings()
            for index in arrIndexes:
                task = XcodeBuild()
                task.infoPrint = self.infoPrint
                task.errorPrint = self.errorPrint
                task.WorkSpacePath = self.inputWorkProjectPathTextView.Value.encode('utf-8')
                task.BuildOutPutPath = self.outputLibPathTextView.Value.encode('utf-8')
                task.Scheme = self.combo_box_scheme_targets.GetStringSelection()
                task.Release = self.radio_box_ReleaseDebug.GetSelection() == 0

                self.infoPrint("构建 {} - {} - Release:{}".format(task.Scheme,arrStrs[index].encode('utf-8'),task.Release))
                success = True
                if index == 0 :
                    success = task.func_build_iphoneos().returncode == 0
                elif index == 1 :
                    success = task.func_build_iphonesimulator() == 0
                self.infoPrint("结束 {} - {} - Release:{}".format(task.Scheme,arrStrs[index].encode('utf-8'),task.Release))

                if not success:
                    break
            self.infoPrint("***************结束构建***************")

        thread.start_new_thread(start, () )
        event.Skip()
    
    def onRadioBoxReleaseDebug(self, event):  # wxGlade: buildLibDialog.<event_handler>
        gConfig.buildLibRelease = self.radio_box_ReleaseDebug.GetSelection() == 0
        event.Skip()

    def onCheckListBoxRunEnv(self, event):  # wxGlade: buildLibDialog.<event_handler>
        gConfig.buildLibTargetDevice = False
        gConfig.buildLibTargetSimulator = False
        arr  = self.check_list_box_RunEnv.GetCheckedItems()
        for s in arr:
            if s == 0:
                gConfig.buildLibTargetDevice = True
            elif s == 1:
                gConfig.buildLibTargetSimulator = True
        event.Skip()

    def infoPrint(self,info):
        wx.CallAfter(self.__infoPrint,info)
        
    def __infoPrint(self,info):
        self.printTextView.AppendText(info + "\n")

    def errorPrint(self,error):
        wx.CallAfter(self.__errorPrint,error)

    def __errorPrint(self,error):
        self.printTextView.AppendText(error + "\n")
# end of class buildLibDialog
