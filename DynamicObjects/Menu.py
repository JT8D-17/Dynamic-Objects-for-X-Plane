#!/usr/bin/python
'''
MODULES
'''
import xp
from DynamicObjects import Window,Labels
'''
VARIABLES
'''
Aux_Vars = {'Labels':1,'Refresh':0} # Helper variables
'''
FUNCTIONS
'''
# Initializes the menu
def Init_Menu(self):
    self.MenuID = xp.createMenu("Dynamic Objects",handler=Menu_Handler,refCon="Dynamic Objects Menu")
    print(self.CMD_Menu_Toggle)
    xp.appendMenuItemWithCommand(self.MenuID,'Toggle Window',commandRef=self.CMD_Menu_Toggle) # Index 0
    xp.appendMenuItem(self.MenuID, "Toggle Labels", refCon="Labels") # Index 1
    xp.appendMenuItem(self.MenuID, "Force Label Refresh", refCon="LabelRefresh") # Index 2
# The menu handler
def Menu_Handler(menuRefCon,itemRefCon):
    global Aux_Vars
    if itemRefCon == "Labels":
        if Aux_Vars['Labels'] == 1:
            Aux_Vars['Labels'] = 0
        elif Aux_Vars['Labels'] == 0:
            Aux_Vars['Labels'] = 1
    if itemRefCon == "LabelRefresh":
        Aux_Vars['Refresh'] = 1
# Monitors menu items for changes
def Menu_Watchdog(self):
    global Aux_Vars
    if Aux_Vars['Refresh'] == 0 and self.Draw_Labels != Aux_Vars['Labels']:
        self.Draw_Labels = Aux_Vars['Labels']
    if Aux_Vars['Refresh'] == 1:
        self.Draw_Labels = 0
        Labels.Uninit_Label_Callback(self)
        self.Draw_Labels = 1
        Labels.Init_Label_Callback(self)
        print("Labels Refreshed")
        Aux_Vars['Refresh'] = 0
    # Index 0
    if xp.getWindowIsVisible(self.WindowId) == 0:
        xp.checkMenuItem(self.MenuID,index=0,checked=0)
    else:
        xp.checkMenuItem(self.MenuID,index=0,checked=2)
    # Index 1
    if self.Draw_Labels == 0:
        xp.checkMenuItem(self.MenuID,index=1,checked=0)
    elif self.Draw_Labels == 1:
        xp.checkMenuItem(self.MenuID,index=1,checked=2)

'''

COMMANDS

'''
#
def Menu_Toggle(cmdRef,phase,refCon):
    if phase == xp.CommandBegin:
        if not refCon.WindowId:
            Window.Init_Window()
        else:
            if xp.getWindowIsVisible(refCon.WindowId) == 0:
                xp.setWindowIsVisible(refCon.WindowId,1)
            else:
                xp.setWindowIsVisible(refCon.WindowId,0)
    return 1
#
def Init_Command(self):
    self.CMD_Menu_Toggle = xp.createCommand("DynObjXP/ToggleWindow","Toggle Dynamic Objects for XP Window")
    xp.registerCommandHandler(self.CMD_Menu_Toggle,Menu_Toggle,1,self)

def Menu_Clean(self):
    # Command
    xp.unregisterCommandHandler(self.CMD_Menu_Toggle,Menu_Toggle,1,self)
    # Menu
    if self.MenuID:
        xp.destroyMenu(self.MenuID)
    xp.clearAllMenuItems(xp.findPluginsMenu())
