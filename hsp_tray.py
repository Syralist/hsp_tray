#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.adv
import urllib.request, json
import requests
from io import StringIO
import datetime
import sys
import base64
# reload(sys)
# sys.setdefaultencoding("utf-8")

TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'hackerspace_icon.png'

HSHBURL = 'https://testhackerspacehb.appspot.com/v2/status'

ICON_OPEN = ''
ICON_CLOSED = ''
STATUS_OPEN = False
STATUS_MESSAGE = ''
LAST_TIME = ''
LAST_CHANGE = 0
LAST_CHANGE_DT = 0

def get_Status():
    global ICON_OPEN
    global ICON_CLOSED
    global STATUS_OPEN
    global STATUS_MESSAGE
    global LAST_TIME
    global LAST_CHANGE
    global LAST_CHANGE_DT

    response = requests.get(HSHBURL)
    print(response.json())

    STATUS_OPEN = response.json()['open']
    STATUS_MESSAGE = response.json()['status']
    icon = urllib.request.urlopen(response.json()['icon']['open'])
    ICON_OPEN = icon.read()
    # print(ICON_OPEN)
    # print(StringIO(ICON_OPEN).getvalue())
    icon.close()
    icon = urllib.request.urlopen(response.json()['icon']['closed'])
    ICON_CLOSED = icon.read()
    icon.close()
    LAST_TIME = response.json()['RESULT']['ST2']
    LAST_CHANGE = int(response.json()['lastchange'])
    LAST_CHANGE_DT = datetime.datetime.fromtimestamp(LAST_CHANGE)
    # print LAST_CHANGE

def set_Status(SetOpen, Message, User, Pw):
    cmdUrl = "https://testhackerspacehb.appspot.com/v2/cmd/"
    if SetOpen:
        cmdUrl += "open"
    else:
        cmdUrl += "close"
    r = requests.post(cmdUrl, data={"name":User, "pass":Pw, "message":Message})
    print(r.status_code, r.reason)
    # get_Status()

def change_Status(Message, User, Pw):
    # print Message
    # print User
    # print Pw
    cmdUrl = "https://testhackerspacehb.appspot.com/v2/cmd/message"
    r = requests.post(cmdUrl, data={"name":User, "pass":Pw, "message":Message, "time": LAST_TIME})
    print(r.status_code, r.reason)
    # get_Status()
    print(r.text)

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

class StatusDialog(wx.Frame):
    def __init__(self, *args, **kw):
        global STATUS_OPEN
        super(StatusDialog, self).__init__(*args, **kw)
        self.SetTitle("Status ändern")
        if STATUS_OPEN:
            self.opencloselabel = "Schliessen"
        else:
            self.opencloselabel = "Öffnen"
        self.InitUI()
        # wx.EVT_CLOSE(self, self.onClose)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def InitUI(self):
        self.panel = wx.Panel(self)
        self.status = wx.TextCtrl(parent=self.panel,size=(250,300),style=wx.TE_MULTILINE|wx.TAB_TRAVERSAL)
        self.user = wx.TextCtrl(parent=self.panel, style=wx.TAB_TRAVERSAL)
        self.pw = wx.TextCtrl(parent=self.panel, style=wx.TE_PASSWORD|wx.TAB_TRAVERSAL)
        self.openclose = wx.Button(parent=self.panel, label=self.opencloselabel)
        self.openclose.Bind(wx.EVT_BUTTON, self.clickOpenClose)
        self.change = wx.Button(parent=self.panel, label="Nachricht ändern")
        self.change.Bind(wx.EVT_BUTTON, self.clickChange)

        self.textsizer = wx.BoxSizer(wx.VERTICAL)
        self.textsizer.Add(wx.StaticText(self.panel, label="Nachricht"), flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(self.status, flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(wx.StaticText(self.panel, label="Benutzer"), flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(self.user, flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(wx.StaticText(self.panel, label="Passwort"), flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(self.pw, flag=wx.ALL|wx.EXPAND)

        self.buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsizer.Add(self.openclose, flag=wx.ALL|wx.EXPAND)
        self.buttonsizer.Add(self.change, flag=wx.ALL|wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textsizer, flag=wx.ALL|wx.EXPAND)
        self.sizer.Add(self.buttonsizer, flag=wx.ALL|wx.EXPAND)

        self.panel.SetSizer(self.sizer)
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer.Add(self.panel, 1, wx.EXPAND)
        # self.topSizer.Fit(self)
        # self.topSizer.Layout() 

        self.SetSizer(self.topSizer)

    def UpdateUI(self, Message):
        if STATUS_OPEN:
            self.opencloselabel = "Schließen"
        else:
            self.opencloselabel = "Öffnen"
        self.openclose.SetLabel(self.opencloselabel)
        self.status.SetValue(Message)

    def clickOpenClose(self, event):
        set_Status(not STATUS_OPEN, self.status.Value, self.user.Value, self.pw.Value)
        self.UpdateUI(STATUS_MESSAGE)

    def clickChange(self, event):
        change_Status(self.status.Value, self.user.Value, self.pw.Value)
        self.UpdateUI(STATUS_MESSAGE)

    def onClose(self, event):
        self.Hide()


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        global ICON_OPEN
        global ICON_CLOSED
        global STATUS_OPEN
        global STATUS_MESSAGE
        super(TaskBarIcon, self).__init__()
        self.frame = frame
        self.timer = wx.Timer(self, 100)
        self.timer.Start(300000)
        self.Bind(wx.EVT_TIMER, self.read_status, self.timer)
        self.read_status(0)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.StatDialog = StatusDialog(None, size=(300,400))

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Status ändern', self.on_status)
        menu.AppendSeparator()
        create_menu_item(menu, 'Beenden', self.on_exit)
        return menu

    def on_left_down(self, event):
        self.read_status(0)

    def on_status(self, event):
        self.StatDialog.UpdateUI(STATUS_MESSAGE)
        self.StatDialog.Show()

    def read_status(self, event):
        get_Status()
        icon = wx.Icon()
        status = 'Der Space ist '
        if STATUS_OPEN:
            icon.CopyFromBitmap(wx.Bitmap.NewFromPNGData(ICON_OPEN,len(ICON_OPEN)))
            status = status + 'geöffnet'
        else:
            icon.CopyFromBitmap(wx.Bitmap.NewFromPNGData(ICON_CLOSED,len(ICON_CLOSED)))
            status = status + 'geschlossen'
        status = status + ' seit '
        status = status + LAST_CHANGE_DT.strftime('%d.%m.%y %H:%M:%S')
        status = status + '.\nAktuelle Nachricht:\n'

        status = status + STATUS_MESSAGE
        
        self.SetIcon(icon, status)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        print("on_exit")
        self.frame.Close()
        wx.GetApp().ExitMainLoop()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():

    app = App(False)
    # TaskBarIcon()
    app.MainLoop()


if __name__ == '__main__':
    main()
