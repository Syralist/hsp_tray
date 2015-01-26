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
        # self.set_icon(TRAY_ICON)
        icon = wx.EmptyIcon()
        if STATUS_OPEN:
            icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(StringIO(ICON_OPEN))))
        else:
            icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(StringIO(ICON_CLOSED))))
        # icon.SetWidth(48)
        # icon.SetHeight(48)
        print icon
        self.SetIcon(icon, TRAY_TOOLTIP)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def on_hello(self, event):
        print 'Hello, world!'

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)


def main():
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

    app = wx.PySimpleApp()
    TaskBarIcon()
    app.MainLoop()


if __name__ == '__main__':
    main()
