#!/usr/bin/python
'''
MODULES
'''
import os
import xp
'''
VARIABLES
'''
End_Mode = "LOOP" # The default route terminator
End_Wait_Time = 0 # The default wait time at the last waypoint
Obj_Heading_Rate = 5 # The object' turn rate in °/s
Obj_Vel_Max = 15 # The default maximum object velocity in m/s
Obj_Vel_Rate = 5 # The default acceleration in m/s²
Obj_Pitch_Max = 30 # The default maximum object pitch in °
Obj_Pitch_Rate = 10 # The object's pitch rate in °/s
Obj_Roll_Max = 30 # The default maximum object roll in °
Obj_Roll_Rate = 10 # The object's roll rate in °/s
WP_AltMode = "AGL" # The default altitude reference
WP_AltOffset = 0 # The default altitude offset at waypoints
WP_Vel = -1 # The default maximum velocity for a waypoint (determined by object)
req_len_obj = 4 # Required minimum elements for OBJECT lines
req_len_pt = 3 # Required minimum elements for POINT lines
'''
FUNCTIONS
'''
def Init_Routes():
    temp_object = []
    out_list = []
    object_count = 0 # Reset object counter
    route_count = 0 # Reset route counter
    for root, dirs, files in os.walk(os.getcwd()): # Walk through all subdirectories
        for file in files:  # Do for files
            if file.startswith("Route_") and file.endswith(".txt"): # Find all "Route_...txt" files
                print("\nROUTE FILE READ: "+file+"")
                with open(os.path.join(root, file), encoding='utf-8') as in_file: # Open route file
                    list_lines = [line.rstrip('\n') for line in in_file] # Read all lines
                    line_count = 0 # Reset line counter in new file
                for n in list_lines:
                    line_count += 1 # Increment line counter for information purposes
                    tempdata = n.split(",") # Split line at comma
                    ## OBJECT
                    if tempdata[0] == "OBJECT":
                        temp_object = []
                        temp_perf = [Obj_Vel_Rate,Obj_Pitch_Rate,Obj_Heading_Rate,Obj_Roll_Rate,Obj_Vel_Max,Obj_Pitch_Max,Obj_Roll_Max]
                        temp_waypoints = []
                        temp_route_end = [End_Mode,End_Wait_Time]
                        temp_datarefs = []
                        if len(tempdata) >= req_len_obj: # Check for malformed OBJECT lines
                            object_count += 1 # Increment object counter for generic object name generation
                            temp_object = ["None","UNKNOWN"]
                            ## OBJECT NAME, TYPE
                            if tempdata[1]: # Check for empty names
                                temp_object[0] = tempdata[1] # Use custom name
                            if tempdata[2]: # Check object type
                                temp_object[1] = tempdata[2]
                            ## OBJECT(S) PATH
                            for x in range(3,len(tempdata)):
                                tempdata2 = tempdata[x].split(";") # Split line at semicolon
                                if tempdata2[0]: # Check for missing path information
                                    #obj_path = tempdata2[0].replace("XPROOT","/mnt/Data/X-Plane_12_Develop").replace("LOCAL",os.path.dirname(os.path.realpath(__file__))) # Replace placeholders by actual paths
                                    obj_path = tempdata2[0].replace("XPROOT",xp.getSystemPath()).replace("LOCAL",xp.PLUGINSPATH+"/DynamicObjects/") # Replace placeholders by actual paths
                                    print(obj_path)
                                    if os.path.isfile(obj_path): # Check if file exists
                                        temp_object.append(obj_path)
                                        print("ROUTE CHECK: "+str(temp_object[0]))
                                    else: # Print error if it does not
                                        print("ERROR: Object path "+obj_path+" not found.")
                                else:
                                    print("ERROR: Missing object path information in line "+str(line_count)+", skipping object.")
                                # OBJECT DATAREFS
                                if len(tempdata2) > 1:
                                    temp_datarefs.append([])
                                    for y in range(1,len(tempdata2)):
                                        temp_datarefs[-1].append(tempdata2[y])
                            if len(temp_object) == 1:
                                print("ERROR: Not enough valid object paths assigned to "+temp_object[0]+" (see line "+str(line_count)+"), skipping route.")
                            elif len(temp_object) > 2 and temp_object[0] == "None": #Check for object name
                                print(temp_object)
                                temp_object[0] = os.path.basename(temp_object[2]) # Generate generic object name from object file name
                        else:
                            print("ERROR: OBJECT in "+file+", at line "+str(line_count)+" requires >="+str(req_len_obj)+" elements, skipping route.")
                    ## PERFORMANCE
                    if tempdata[0] == "PERFORMANCE":
                        if len(temp_object) >= (req_len_obj-1):
                            if len(tempdata) >= 2 and tempdata[1]: # Check acceleration
                                temp_perf[0] = float(tempdata[1])
                            if len(tempdata) >= 3 and tempdata[2]: # Check pitch rate
                                temp_perf[1] = float(tempdata[2])
                            if len(tempdata) >= 4 and tempdata[3]: # Check heading rate
                                temp_perf[2] = float(tempdata[3])
                            if len(tempdata) >= 5 and tempdata[4]: # Check roll rate
                                temp_perf[3] = float(tempdata[4])
                            if len(tempdata) >= 6 and tempdata[5]: # Check max velocity
                                temp_perf[4] = float(tempdata[5])
                            if len(tempdata) >= 7 and tempdata[6]: # Check max pitch
                                temp_perf[5] = float(tempdata[6])
                            if len(tempdata) >= 8 and tempdata[7]: # Check max max roll
                                temp_perf[6] = float(tempdata[7])
                    ## ROUTE POINTS
                    if tempdata[0] == "POINT" and len(temp_object) >= (req_len_obj-1):
                        if len(tempdata) >= req_len_pt: # Check for malformed POINT lines
                            temp_waypoints.append([0,0,WP_AltMode,WP_AltOffset,WP_Vel]) # Append waypoint list
                            if tempdata[1]:
                                temp_waypoints[-1][0] = float(tempdata[1])
                            else:
                                print("ERROR: POINT in "+file+", at line "+str(line_count)+" has no latitude value.")
                            if tempdata[2]:
                                temp_waypoints[-1][1] = float(tempdata[2])
                            else:
                                print("ERROR: POINT in "+file+", at line "+str(line_count)+" has no longitude value.")
                            if len(tempdata) >= 4 and tempdata[3]: # AGL or ABS, string
                                temp_waypoints[-1][2] = tempdata[3]
                            if len(tempdata) >= 5 and tempdata[4].isnumeric(): # AGL offset or ABS alt; number
                                temp_waypoints[-1][3] = float(tempdata[4])
                            if len(tempdata) >= 6 and tempdata[5].isnumeric(): # Waypoint velocity; number
                                temp_waypoints[-1][4] = float(tempdata[5])
                            #print(str(temp_waypoints))
                        else:
                            print("ERROR: POINT in "+file+", at line "+str(line_count)+" requires >="+str(req_len_pt)+" elements, skipping point.")
                    ## ROUTE END MODE
                    if (tempdata[0] == "LOOP" or tempdata[0] == "RETURN" or tempdata[0] == "STOP") and len(temp_object) >= (req_len_obj-1): # Look for route end mode data
                        temp_route_end[0] = tempdata[0]
                        if len(tempdata) > 1 and tempdata[1] is not None and tempdata[1].isnumeric():
                            temp_route_end[1] = tempdata[1]
                        #print("Found route terminator: "+temp_route_end[0]+" with wait time "+str(temp_route_end[1])+" s.")
                    ## END OF ROUTE
                    if (not n.strip() or line_count == len(list_lines)) and len(temp_object) > 0 and len(temp_waypoints) > 0: # At blank lines or end of file, check for object data and waypoints
                        if len(temp_object) >= 2 and len(temp_waypoints) >= 2:
                            out_list.append([temp_object,temp_perf,temp_waypoints,temp_route_end,temp_datarefs])
                            route_count += 1
                            print("---------- ROUTE "+str(route_count)+"\nObject(s):   "+str(out_list[-1][0])+"\nPerformance: "+str(out_list[-1][1])+"\nWaypoints:   "+str(out_list[-1][2])+"\nTerminator:  "+str(out_list[-1][3])+"\nDatarefs:    "+str(out_list[-1][4])+"\n----------")
                        elif len(temp_waypoints) < 2:
                            print("ERROR: Less than 2 waypoints in route, skipping route.")
                        temp_object = []
                        temp_perf = [Obj_Vel_Rate,Obj_Pitch_Rate,Obj_Heading_Rate,Obj_Roll_Rate,Obj_Vel_Max,Obj_Pitch_Max,Obj_Roll_Max]
                        temp_waypoints = []
                        temp_route_end = [End_Mode,End_Wait_Time]
                        temp_datarefs = []


    #print("\nFINISHED ADDING ROUTES (Total: "+str(route_count)+")\n")
    return out_list
