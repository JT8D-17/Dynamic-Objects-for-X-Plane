#!/usr/bin/python
'''
LIBRARIES
'''
import os,time #,shutil,re
#import PI_DynamicObjects as DObj
from PI_DynamicObjects.Routes import z_Object_Datarefs
from PI_DynamicObjects import Helpers,Import_Routes,Objects,Movement

'''
VARIABLES
'''
Debug = 0
XPPath = "/media/X-Plane/X-Plane_12_Main"
'''
Route_List format for each dynamic object:
[[Object name,Object1 path,Object2 path,...],[[Point1 Lat,Point1 Lon,Point1 Elevation,Point1 Velocity],[Point2 Lat,Point2 Lon,Point2 Elevation,Point2 Velocity],..],[end mode,end wait time]]

'''
Route_List = [] # Declare route list
'''

'''
Object_List = [] # The list of used objects
starttime = time.monotonic()
interval = 1
cycle = 0
'''
FUNCTIONS
'''
'''
PROGRAM EXECUTION
'''
Helpers.Debug = Debug
Route_List = Import_Routes.Init_Routes(XPPath) # Initialize routes
Object_List = Objects.Init_Objects(Route_List) # Initialize objects
'''
TIMER
'''
#quit()
while True:
    os.system('clear')
    cycle += 1
    print("\nCycle: "+str(cycle))
    Movement.move_objects(Object_List,Route_List,interval)
    z_Object_Datarefs.run_dref_code()
    time.sleep(interval - ((time.monotonic() - starttime) % interval))
    if cycle == 1000:
        break
