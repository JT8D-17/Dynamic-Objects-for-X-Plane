#!/usr/bin/python
'''
MODULES
'''
import xp
from .Helpers import print_list_vert
#from .Movement import calc_distance
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
        init_hdg = -999 # Initial heading
        init_alt = in_routes[n][2][0][3] # Initial altitude
        init_pit,init_rol,init_vel = 0,0,0
        '''Add list:
        0:Identifier,1:[instances],
        2:[lat,lon,altitude,pitch,heading,roll,velocity],
        3:[0:Index next wp,1:Index 2nd next WP,2:Movement mode],
        4:[0:[0:WP_n lat,1:WP_n lon,2:WP_n alt,3:WP_n alt mode,4:WP_n corrected altitude],1:[0:WP_n+1 lat,1:WP_n+1 lon,2:WP_n+1 alt,3:WP_n+1 alt mode,4:WP_n+1 corrected altitude]],
        5:[0:TerrainProbeReference]
        6:[0:[0:WP_n bearing,1:WP_n distance,2:WP_n time to go,3:WP_n velocity,4:WP_n turn velocity],0:[0:WP_n+1 bearing,1:WP_n+1 distance,2:WP_n+1 time to go,3:WP_n+1 velocity,4:WP_n+1 turn velocity]]
        '''
        out_list.append([in_routes[n][0][0],[],[init_lat,init_lon,init_alt,init_pit,init_hdg,init_rol,init_vel],[1,0,"FWD"],[[0,0,0,"None",0],[0,0,0,"None",0]],[None],[[-99,0,0,0,0],[-99,0,0,0,0]]])
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

            if in_routes[n][0][1] == "HELICOPTER" or in_routes[n][0][1] == "AIRPLANE":
                out_list[len(out_list)-1][5][0] = xp.createProbe()
                print(in_routes[n][0][0]+" is type "+in_routes[n][0][1]+", created terrain probe ref: "+str(out_list[len(out_list)-1][5][0]))

        # Read current and next 2 waypoints
        if len(in_routes[n][2]) > 2:
            out_list[n][3][1] = 2

    #print_list_vert(out_list) # Print result
    return out_list
