#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Feb 10 15:50:10 2021
#

# This is an automatically generated file.
# Manual changes will be overwritten without warning!

import wx
from mainFrame import mainFrame


class MyApp(wx.App):
    def OnInit(self):
        self.frame = mainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
