#!/usr/bin/python
'''
LIBRARIES
'''
import os
from XPPython3 import xp #,xp_imgui,imgui
from DynamicObjects.Routes import z_Object_Datarefs
from DynamicObjects import Helpers,Import_Routes,Labels,Objects,Movement,Window,Camera,Menu
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
        self.Object_Window = [] # Information about the object in the status window
        self.delta_t = 0.05 # Update interval for the flight loop
        self.flightLoopID = None
        # Menu
        self.MenuID = None
        self.CMD_Menu_Toggle = None
        self.Draw_Labels = 1
        # WINDOW
        self.WindowId = None
        self.LineOffset = 0
        self.MaxLines = 200
        self.WindowDims = {'w':10,'h':10,'r':110,'b':110,'l':100,'t':100}
        self.WindowDim_Req = {'w':0,'h':0}
        self.Padding = {'t':10,'l':5}
        self.WindowContent = {'t':0,'l':0}
        self.WindowFont = xp.Font_Basic
        (font_w,self.FontHeight,digitsOnly) = xp.getFontDimensions(self.WindowFont)
        self.LineHeight = int(self.FontHeight * 1.2)
        # Camera
        self.Object_Camera = {'num':-1,'x':0,'y':0,'z':0}
        self.CameraWindowID = None
        self.CameraMouseStatus = {'LMB':0,'RMB':0,'WHL':0}
        # General
        self.DR_Paused = None

    '''
    FLIGHT LOOP

    '''
    # Callback for the main flight loop
    def MainFlightLoopCallback(self, sinceLast, elapsedTime, counter, refCon):
        #print(f"{elapsedTime}, {counter}")
        self.Object_Info = []
        if xp.getDatai(self.DR_Paused) == 0:
            Movement.move_objects(self.Object_List,self.Route_List,self.delta_t,self.Object_Info,self.Object_Camera)
            z_Object_Datarefs.run_dref_code()
        Window.Auto_Resize(self)
        Camera.Camera_Watchdog(self)
        Menu.Menu_Watchdog(self)
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
        for k in range(len(self.Object_List)):
            self.Object_Window.append([self.Object_List[k][0],[0,0,0,0],0]) # Object name, line information in object window, is active
        print("DynObjXP: Initialized objects")
        # Menu
        Menu.Init_Command(self)
        Menu.Init_Menu(self)
        # Flight loop
        self.FlightLoop_ID = xp.createFlightLoop(self.MainFlightLoopCallback, phase=0, refCon=None)
        xp.scheduleFlightLoop(self.FlightLoop_ID,interval=1)
        print("DynObjXP: Flight loop created with interval "+f'{self.delta_t:.3f}')
        # Drawcall for labels
        Labels.Init_Labels()
        Labels.Init_Label_Callback(self)
    '''

    X-PLANE PLUGIN INTERFACE

    '''
    # Required; Called once by X-Plane on startup (or when plugins are re-starting as part of reload),  You need to return three strings.
    def XPluginStart(self):
        return self.Name, self.Sig, self.Desc
    # Called once by X-Plane on quit (or when plugins are exiting as part of reload). Return is ignored.
    def XPluginStop(self):
        Menu.Menu_Clean(self)
        pass
    # Required, called once by X-Plane, after all plugins have "Started" (including during reload sequence), you need to return an integer 1, if you have successfully enabled, 0 otherwise.
    def XPluginEnable(self):
        print("DynObjXP: Enabled")
        self.Init_DynamicObjects()
        Window.Init_Window(self)
        self.DR_Paused = xp.findDataRef("sim/time/paused")
        return 1
    # Called once by X-Plane, when plugin is requested to be disabled. All plugins are disabled prior to Stop. Return is ignored.
    def XPluginDisable(self):
        # Draw callback
        Labels.Uninit_Label_Callback(self)
        # Clean up all Imgui Windows
        xp.destroyWindow(self.WindowId)
        # Instances
        for n in range(len(self.Object_List)):
            for m in range(len(self.Object_List[n][1])):
                xp.destroyInstance(self.Object_List[n][1][m])
        print("DynObjXP: Instances Destroyed")
        # Flight loop
        if self.FlightLoop_ID:
            xp.destroyFlightLoop(self.FlightLoop_ID)
            self.FlightLoop_ID = None
        print("DynObjXP: Flightloop Terminated")
        pass
    # Called by X-Plane whenever a plugin message is being sent to your plugin. Messages include MSG_PLANE_LOADED, MSG_ENTERED_VR, etc., as described in XPLMPlugin module. Messages may be custom inter-plugin messages, as defined by other plugins. Return is ignored
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        #print(inMessage)
        #if inMessage == 104: #SCENERY_LOADED
            #self.Init_DynamicObjects()
            #self.Init_Window()
        pass
