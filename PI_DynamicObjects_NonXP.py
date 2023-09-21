#!/usr/bin/python
'''
LIBRARIES
'''
import os,time
from PI_DynamicObjects.Routes import z_Object_Datarefs
from PI_DynamicObjects import Helpers,Import_Routes,Objects,Movement
'''
FUNCTIONS
'''
def Fake_Flightloop():
    Cycle = 0
    StartTime = time.monotonic()
    delta_t = 0.1
    while True:
        os.system('clear')
        Cycle += 1
        print("\nCycle: "+str(Cycle))
        Movement.move_objects(Object_List,Route_List,delta_t)
        z_Object_Datarefs.run_dref_code()
        time.sleep(delta_t - ((time.monotonic() - StartTime) % delta_t))
        if Cycle == (1000 / delta_t):
            break
'''
__init__(self):
'''
Route_List = [] # Declare route list
Object_List = [] # The list of used objects
'''
XPLUGINSTART
'''
Route_List = Import_Routes.Init_Routes() # Initialize routes
Object_List = Objects.Init_Objects(Route_List) # Initialize objects
'''
XPLUGINENABLE
'''
print("Enabling Dynamic Objects for X-Plane")
#quit()
Fake_Flightloop()
