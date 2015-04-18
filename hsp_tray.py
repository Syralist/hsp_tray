import wx
import urllib, json
import requests
from cStringIO import StringIO

TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'hackerspace_icon.png'

HSHBURL = 'https://hackerspacehb.appspot.com/v2/status'

ICON_OPEN = ''
ICON_CLOSED = ''
STATUS_OPEN = False
STATUS_MESSAGE = ''

def get_Status():
    global ICON_OPEN
    global ICON_CLOSED
    global STATUS_OPEN
    global STATUS_MESSAGE

    response = requests.get(HSHBURL)
    print response.json()

    STATUS_OPEN = response.json()['open']
    STATUS_MESSAGE = response.json()['status']
    icon = urllib.urlopen(response.json()['icon']['open'])
    ICON_OPEN = icon.read()
    icon.close()
    icon = urllib.urlopen(response.json()['icon']['closed'])
    ICON_CLOSED = icon.read()
    icon.close()

def set_Status(SetOpen, Message, User, Pw):
    cmdUrl = "https://hackerspacehb.appspot.com/v2/cmd/"
    if SetOpen:
        cmdUrl += "open"
    else:
        cmdUrl += "close"
    r = requests.post(cmdUrl, data={"name":User, "pass":Pw, "message":Message})
    print(r.status_code, r.reason)
    # get_Status()

def change_Status(Message, User, Pw):
    cmdUrl = "https://hackerspacehb.appspot.com/v2/cmd/message"
    r = requests.post(cmdUrl, data={"name":User, "pass":Pw, "message":Message, "format":"de"})
    print(r.status_code, r.reason)
    # get_Status()

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class StatusDialog(wx.Frame):
    def __init__(self, *args, **kw):
        global STATUS_OPEN
        super(StatusDialog, self).__init__(*args, **kw)
        if STATUS_OPEN:
            self.opencloselabel = "Close"
        else:
            self.opencloselabel = "Open"
        self.InitUI()

    def InitUI(self):
        self.panel = self #wx.Panel(self)
        self.status = wx.TextCtrl(parent=self.panel,style=wx.TE_MULTILINE)
        self.user = wx.TextCtrl(parent=self.panel)
        self.pw = wx.TextCtrl(parent=self.panel, style=wx.TE_PASSWORD)
        self.openclose = wx.Button(parent=self.panel, label=self.opencloselabel)
        self.openclose.Bind(wx.EVT_BUTTON, self.clickOpenClose)
        self.change = wx.Button(parent=self.panel, label="Change")
        self.change.Disable()
        self.change.Bind(wx.EVT_BUTTON, self.clickChange)

        self.textsizer = wx.BoxSizer(wx.VERTICAL)
        self.textsizer.Add(self.status, flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(self.user, flag=wx.ALL|wx.EXPAND)
        self.textsizer.Add(self.pw, flag=wx.ALL|wx.EXPAND)

        self.buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonsizer.Add(self.openclose, flag=wx.ALL|wx.EXPAND)
        self.buttonsizer.Add(self.change, flag=wx.ALL|wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textsizer, flag=wx.ALL|wx.EXPAND)
        self.sizer.Add(self.buttonsizer, flag=wx.ALL|wx.EXPAND)

        self.panel.SetSizer(self.sizer)

    def clickOpenClose(self, event):
        set_Status(not STATUS_OPEN, self.status.Value, self.user.Value, self.pw.Value)

    def clickChange(self, event):
        change_Status(self.status.Value, self.user.Value, self.pw.Value)

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        global ICON_OPEN
        global ICON_CLOSED
        global STATUS_OPEN
        global STATUS_MESSAGE
        super(TaskBarIcon, self).__init__()
        self.timer = wx.Timer(self, 100)
        self.timer.Start(300000)
        wx.EVT_TIMER(self, 100, self.read_status)
        self.read_status(0)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.StatDialog = StatusDialog(None)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Change Status', self.on_status)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'
        self.read_status(0)

    def on_status(self, event):
        print 'Hello, world!'
        self.StatDialog.Show()
        # self.StatDialog.Destroy()

    def read_status(self, event):
        get_Status()
        icon = wx.EmptyIcon()
        if STATUS_OPEN:
            icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(StringIO(ICON_OPEN))))
        else:
            icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(StringIO(ICON_CLOSED))))
        print icon
        self.SetIcon(icon, STATUS_MESSAGE)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)

def main():

    app = wx.PySimpleApp()
    TaskBarIcon()
    app.MainLoop()


if __name__ == '__main__':
    main()
