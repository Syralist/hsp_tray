import wx
import urllib, json
import requests
from cStringIO import StringIO

TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'hackerspace_icon.png'

HSHBURL = 'https://testhackerspacehb.appspot.com/v2/status'

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
    # if response.json()['open']:
    #     print response.json()['icon']['open']
    # else:
    #     print response.json()['icon']['closed']



def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        global ICON_OPEN
        global ICON_CLOSED
        global STATUS_OPEN
        global STATUS_MESSAGE
        super(TaskBarIcon, self).__init__()
        self.timer = wx.Timer(self, 100)
        self.timer.Start(60000)
        wx.EVT_TIMER(self, 100, self.read_status)
        self.read_status(0)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def on_hello(self, event):
        print 'Hello, world!'

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
