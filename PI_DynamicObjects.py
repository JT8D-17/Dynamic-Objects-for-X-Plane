#!/usr/bin/python
'''
LIBRARIES
'''
import os,time
from XPPython3 import xp,xp_imgui,imgui
from PI_DynamicObjects.Routes import z_Object_Datarefs
from PI_DynamicObjects import Helpers,Import_Routes,Objects,Movement
'''
FUNCTIONS
'''
# Overrides the "print()" command to print to XP's developer console and XPPython3.log
def print(msg):
   xp.debugString(f"{msg}\n")
   #xp.sys_log(f"{msg}\n")
   xp.log(f"{msg}")

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
        self.delta_t = 0.05 # Update interval for the flight loop
    '''
    FUNCTIONS
    '''
    def FlightLoopCallback(sinceLast, elapsedTime, counter, refCon):
        #print(f"{elapsedTime}, {counter}")
        Movement.move_objects(Object_List,Route_List,delta_t)
        z_Object_Datarefs.run_dref_code()
        return self.delta_t
    '''
    X-PLANE PLUGIN INTERFACE
    '''
    # Required; Called once by X-Plane on startup (or when plugins are re-starting as part of reload),  You need to return three strings.
    def XPluginStart(self):
        self.Route_List = Import_Routes.Init_Routes() # Initialize routes
        self.Object_List = Objects.Init_Objects(Route_List) # Initialize objects
        # Menu
        #xp.appendMenuItemWithCommand(xp.findPluginsMenu(), 'Dynamic Objects', self.cmd)
        return self.Name, self.Sig, self.Desc
    # Called once by X-Plane on quit (or when plugins are exiting as part of reload). Return is ignored.
    def XPluginStop(self):
        pass
    # Required, called once by X-Plane, after all plugins have "Started" (including during reload sequence), you need to return an integer 1, if you have successfully enabled, 0 otherwise.
    def XPluginEnable(self):
        print("Enabling Dynamic Objects for X-Plane")

        self.FlightLoop_ID = xp.createFlightLoop(FlightLoopCallback, phase=0, refCon=None)
        xp.scheduleFlightLoop(self.FlightLoop_ID,interval=1)
        return 1
    # Called once by X-Plane, when plugin is requested to be disabled. All plugins are disabled prior to Stop. Return is ignored.
    def XPluginDisable(self):
         xp.destroyFlightLoop(self.flightLoopID)
         print("DynObjXP: Flightloop Terminated")
        pass
    # Called by X-Plane whenever a plugin message is being sent to your plugin. Messages include MSG_PLANE_LOADED, MSG_ENTERED_VR, etc., as described in XPLMPlugin module. Messages may be custom inter-plugin messages, as defined by other plugins. Return is ignored
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass
