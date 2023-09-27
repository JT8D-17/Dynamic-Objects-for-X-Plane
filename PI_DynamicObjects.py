#!/usr/bin/python
'''
LIBRARIES
'''
import os
from XPPython3 import xp #,xp_imgui,imgui
from DynamicObjects.Routes import z_Object_Datarefs
from DynamicObjects import Helpers,Import_Routes,Objects,Movement
'''
FUNCTIONS
'''
# Overrides the "print()" command to print to XP's developer console and XPPython3.log
#def print(msg):
#   xp.debugString(f"{msg}\n")
#   #xp.sys_log(f"{msg}\n")
#   xp.log(f"{msg}")

'''
PYTHON INTERFACE CLASS
'''
class PythonInterface:
    '''
    INITIALIZATION
    '''
    def __init__(self):
        # Plugin Properties
        self.Name = "Dynamic Objects"
        self.Sig = "DynObjXP.xppython3"
        self.Desc = "Spawns, displays and controls dynamic objects in X-Plane"
        #
        self.Route_List = [] # Declare route list
        self.Object_List = [] # The list of used objects
        self.Object_Info = [] # Status information
        self.delta_t = 0.05 # Update interval for the flight loop
        self.flightLoopID = None
        #
        self.MenuID = None
        self.CMD_Menu_Toggle = None
        self.cmdRef = []
        # WINDOW
        self.WindowId = None
        self.LineOffset = 0
        self.WindowDims = {'w':10,'h':10,'l':100,'t':100}
        self.WindowDim_Req = {'w':0,'h':0}
        #
    '''

    COMMANDS

    '''
    def Menu_Toggle(self, cmdRef, phase, refCon):
        if phase == xp.CommandBegin:
            if not self.WindowId:
                self.Init_Window()
            else:
                if xp.getWindowIsVisible(self.WindowId) == 0:
                    xp.setWindowIsVisible(self.WindowId,1)
                else:
                    xp.setWindowIsVisible(self.WindowId,0)
        return 1
    def Init_Command(self):
        self.CMD_Menu_Toggle = xp.createCommand("DynObjXP/ToggleWindow","Toggle Dynamic Objects for XP Window")
        xp.registerCommandHandler(self.CMD_Menu_Toggle, self.Menu_Toggle, 1, self.cmdRef)
    '''

    WINDOW

    '''
    def Init_Window(self):
        scr_l,scr_t,scr_r,scr_b = xp.getScreenBoundsGlobal()
        windowInfo = ((scr_l+self.WindowDims['l']),(scr_t-self.WindowDims['t']),(scr_l+self.WindowDims['l']+self.WindowDims['w']),(scr_t-(self.WindowDims['t']+self.WindowDims['h'])), 1,self.DrawWindowCallback,self.MouseClickCallback,self.KeyCallback,self.CursorCallback,self.MouseWheelCallback,0,xp.WindowDecorationRoundRectangle,xp.WindowLayerFloatingWindows,None)
        self.WindowId = xp.createWindowEx(windowInfo)
        #xp.setWindowIsVisible(self.WindowId,0)
    #
    def Auto_Resize(self):
        if self.WindowId:
            scr_l,scr_t,scr_r,scr_b = xp.getScreenBoundsGlobal()
            (left, top, right, bottom) = xp.getWindowGeometry(self.WindowId)
            if (right - left) < self.WindowDim_Req['w']:
                xp.setWindowGeometry(self.WindowId,left,top,(left+self.WindowDim_Req['w']),bottom)
            if (top - bottom) < self.WindowDim_Req['h']:
                xp.setWindowGeometry(self.WindowId,left,top,right,(top-self.WindowDim_Req['h']))
            #print(top,bottom,self.WindowDim_Req['h'])

    #
    def Draw_ObjStatus(self,inWindowID,in_top):
        # FONT
        color = 1.0, 1.0, 1.0
        font = xp.Font_Basic
        (font_w,font_h,digitsOnly) = xp.getFontDimensions(font)
        # WINDOW
        (left, top, right, bottom) = xp.getWindowGeometry(inWindowID)
        pad_l,pad_t = 5,20
        begin_l,begin_t = int(left+pad_l),int(top-in_top-pad_t)
        offset_tab = begin_l
        win_req_width = 0
        # HEADERS
        columns = (["Object",120],["Position",150],["Heading",55],["Velocity",65],["Next WP",230],["Follow-Up WP",230])
        max_lines = 200
        if max_lines > len(self.Object_List):
            max_lines = len(self.Object_List)
        for i in range(len(columns)):
            win_req_width += columns[i][1] + pad_l
            offset_line = begin_t
            dashes = ""
            for j in range(0,int(columns[i][1]/xp.measureString(font,"-"))):
                dashes = dashes + "-"
            if xp.measureString(font,columns[i][0]) > columns[i][1]:
                string = dashes
            xp.drawString(color,offset_tab,offset_line,columns[i][0], 0,font)
            offset_line -= int(font_h * 1.2)
            xp.drawString(color,offset_tab,offset_line,dashes, 0,font)
            for k in range(max_lines):
                offset_line -= int(font_h * 1.2)
                if columns[i][0] == "Object":
                    xp.drawString(color,offset_tab,offset_line,self.Object_Info[k][0], 0,font)
                if columns[i][0] == "Position":
                    xp.drawString(color,offset_tab,offset_line,f'{self.Object_Info[k][1]:8.5f} N, {self.Object_Info[k][2]:9.5f} E', 0,font)
                if columns[i][0] == "Heading":
                    xp.drawString(color,offset_tab,offset_line,f'{self.Object_Info[k][3]:6.2f} °', 0,font)
                if columns[i][0] == "Velocity":
                    xp.drawString(color,offset_tab,offset_line,f'{self.Object_Info[k][4]:6.2f} m/s', 0,font)
                if columns[i][0] == "Next WP":
                    xp.drawString(color,offset_tab,offset_line,f'{self.Object_Info[k][6]:2.0f}/{self.Object_Info[k][5]:2.0f}, {self.Object_Info[k][9]:6.2f}°, {self.Object_Info[k][10]:8.0f} m in {self.Object_Info[k][11]:6.0f} s', 0,font)
                if columns[i][0] == "Follow-Up WP":
                    xp.drawString(color,offset_tab,offset_line,f'{self.Object_Info[k][12]:2.0f}/{self.Object_Info[k][5]:2.0f}, {self.Object_Info[k][15]:6.2f}°, {self.Object_Info[k][16]:8.0f} m in {self.Object_Info[k][17]:6.0f} s', 0,font)

            offset_tab += columns[i][1] + pad_l

        #print(pad_t + (max_lines + 2) * int(font_h * 1.2))
        if (pad_t + (max_lines + 2) * int(font_h * 1.2)) > self.WindowDim_Req['h']:
            self.WindowDim_Req['h'] = (pad_t + (max_lines + 2) * int(font_h * 1.2))
        if win_req_width > self.WindowDim_Req['w']:
            self.WindowDim_Req['w'] = win_req_width


    #
    def DrawWindowCallback(self, inWindowID, inRefcon):
        # First we get the location of the window passed in to us.
        (left, top, right, bottom) = xp.getWindowGeometry(inWindowID)
        #xp.drawTranslucentDarkBox(left, top, right, bottom)
        self.Draw_ObjStatus(inWindowID,0)


    #
    def KeyCallback(self, inWindowID, inKey, inFlags, inVirtualKey, inRefcon, losingFocus):
        pass
    #
    def MouseClickCallback(self, inWindowID, x, y, inMouse, inRefcon):
        return 1
    #
    def CursorCallback(self, inWindowID, x, y, inRefcon):
        return xp.CursorDefault
    #
    def MouseWheelCallback(self, inWindowID, x, y, wheel, clicks, inRefcon):
        return 1
    '''
    FLIGHT LOOP

    '''
    # Callback for the main flight loop
    def MainFlightLoopCallback(self, sinceLast, elapsedTime, counter, refCon):
        #print(f"{elapsedTime}, {counter}")
        self.Object_Info = []
        Movement.move_objects(self.Object_List,self.Route_List,self.delta_t,self.Object_Info)
        z_Object_Datarefs.run_dref_code()
        self.Auto_Resize()
        return self.delta_t
    '''

    INITIALIZATION

    '''
    # Initialization routine, called when scenery was loaded
    def Init_DynamicObjects(self):
        # Load objects
        self.Route_List = Import_Routes.Init_Routes() # Initialize routes
        print("DynObjXP: Parsed routes")
        self.Object_List = Objects.Init_Objects(self.Route_List) # Initialize objects
        print("DynObjXP: Initialized objects")
        # Menu
        self.Init_Command()
        xp.appendMenuItemWithCommand(xp.findPluginsMenu(),'Dynamic Objects Window',self.CMD_Menu_Toggle)
        # Flight loop
        self.FlightLoop_ID = xp.createFlightLoop(self.MainFlightLoopCallback, phase=0, refCon=None)
        xp.scheduleFlightLoop(self.FlightLoop_ID,interval=1)
        print("DynObjXP: Flight loop created with interval "+f'{self.delta_t:.3f}')
    '''

    X-PLANE PLUGIN INTERFACE

    '''
    # Required; Called once by X-Plane on startup (or when plugins are re-starting as part of reload),  You need to return three strings.
    def XPluginStart(self):
        return self.Name, self.Sig, self.Desc
    # Called once by X-Plane on quit (or when plugins are exiting as part of reload). Return is ignored.
    def XPluginStop(self):
        # Command
        xp.unregisterCommandHandler(self.CMD_Menu_Toggle, self.Menu_Toggle, 1, self.cmdRef)
        # Menu
        xp.clearAllMenuItems(xp.findPluginsMenu())
        pass
    # Required, called once by X-Plane, after all plugins have "Started" (including during reload sequence), you need to return an integer 1, if you have successfully enabled, 0 otherwise.
    def XPluginEnable(self):
        print("DynObjXP: Enabled")
        self.Init_DynamicObjects()
        self.Init_Window()
        return 1
    # Called once by X-Plane, when plugin is requested to be disabled. All plugins are disabled prior to Stop. Return is ignored.
    def XPluginDisable(self):
        # Instances
        for n in range(len(self.Object_List)):
            for m in range(len(self.Object_List[n][1])):
                xp.destroyInstance(self.Object_List[n][1][m])
        print("DynObjXP: Instances Destroyed")
        # Flight loop
        if self.flightLoopID:
            xp.destroyFlightLoop(self.flightLoopID)
            self.flightLoopID = None
        print("DynObjXP: Flightloop Terminated")
        # Clean up all Imgui Windows
        xp.destroyWindow(self.WindowId)
        pass
    # Called by X-Plane whenever a plugin message is being sent to your plugin. Messages include MSG_PLANE_LOADED, MSG_ENTERED_VR, etc., as described in XPLMPlugin module. Messages may be custom inter-plugin messages, as defined by other plugins. Return is ignored
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        print(inMessage)
        #if inMessage == 104: #SCENERY_LOADED
        #    Init_DynamicObjects()
        pass
