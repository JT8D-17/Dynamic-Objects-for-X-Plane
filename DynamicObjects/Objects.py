#!/usr/bin/python
'''
MODULES
'''
import xp
from .Helpers import print_list_vert
from .Movement import haversine
'''
VARIABLES
'''
Object_Refs = [] # A list of object references
count = 0
'''
FUNCTIONS
'''
# Generates a fake object reference
#def gen_obj_ref(instring):
#    return "Ref"+str(len(instring))
# Unloads all objects
'''
' Cross checking with a list of previously loaded objects is unnecessary because XP's loadObject/loadObjectAsync only loads an OBJ once to save memory! Object references, however, will be different!
def load_objects(in_routes):
    for n in range(len(in_routes)):
        for m in range(2,len(in_routes[n][0])):
            found = 0
            for o in range(len(Object_Refs)):
                if in_routes[n][0][m] == Object_Refs[o][0]:
                    found = 1
            if found == 0:
                objref = gen_obj_ref(in_routes[n][0][m])
                Object_Refs.append([in_routes[n][0][m],objref])
    print(str(Object_Refs)+"\n")
'''
# Unloads all objects
'''
def unload_objects(Object_Refs):
    #for n in range(len(Object_Refs)):
        #unloadObject(objectRef)
'''
#
def Init_Objects(in_routes):
    out_list = []
    count = 0
    for n in range(len(in_routes)): # Iterate through route list
        init_lat,init_lon = in_routes[n][2][0][0],in_routes[n][2][0][1]
        init_hdg = haversine(init_lat,init_lon,in_routes[n][2][1][0],in_routes[n][2][1][1])
        init_alt,init_pit,init_rol,init_vel = 0,0,0,0
        # Add list: Identifier,[instances],[lat,lon,altitude,pitch,heading,roll,velocity], [next waypoint indices,movement mode,deceleration mode]
        out_list.append([in_routes[n][0][0],[],[init_lat,init_lon,init_alt,init_pit,init_hdg,init_rol,init_vel],[1,0,"FWD",0]])
        # Create object instances
        for m in range(2,len(in_routes[n][0])): # Iterate through objects for given route
            count = count + 1
            #Instanceref = "Instance"+str(count) # Non-XP ONLY!
            Obj_Ref = xp.loadObject(in_routes[n][0][m]) # Calls loadObject/loadObjectAsync in XP here; need to work around delay in returning object handle for loadObjectAsync!!
            if Obj_Ref is None:
                print("ERROR: Could not load "+in_routes[n][0][m])
            Instanceref = xp.createInstance(Obj_Ref, dataRefs=None)
            if Instanceref is None:
                print("ERROR: Could not create instance for "+in_routes[n][0][m])
            out_list[len(out_list)-1][1].append(Instanceref)
        # Read current and next 2 waypoints
        if len(in_routes[n][2]) > 2:
            out_list[n][3][1] = 2

    # Print result
    print_list_vert(out_list)
    return out_list
