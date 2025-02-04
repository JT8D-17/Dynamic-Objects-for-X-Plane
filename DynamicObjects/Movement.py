#!/usr/bin/python
'''
MODULES
'''
from math import asin,atan,atan2,sin,cos,degrees,pi,radians,sqrt,tan
import os,xp
'''
VARIABLES
'''
r_Earth = 6372.8 # Earth's radius, in km
gravity = 9.80665 # m/s²
Labels_Objects = [] # Array for object labels
Labels_Waypoint_1 = [] # Array for waypoint labels
Labels_Waypoint_2 = [] # Array for waypoint labels
'''
FUNCTIONS
'''
# LEGACY: Switches to the next waypoint upon reaching the waypoint
def waypoint_switcher(obj_list,rte_list,index):
    # Switch next waypoint
    obj_list[index][3][0] = obj_list[index][3][1] # Make second waypoint from now the next one
    # Switch waypoint after next waypoint
    if obj_list[index][3][2] == "FWD": # Movement mode forward
        if obj_list[index][3][1] < (len(rte_list[index][2])-1): # Check if next WP index is less than index of last WP
            obj_list[index][3][1] += 1 # Increment WP number
        elif rte_list[index][3][0] == "LOOP": # If not set the next waypoint to the first one when looping
                obj_list[index][3][1] = 0
        elif rte_list[index][3][0] == "RETURN": # If not set the next waypoint to the previous one and change mode
                obj_list[index][3][1] = (len(rte_list[index][2])-1)-1
    if obj_list[index][3][2] == "BWD": # Movement mode backward
        if obj_list[index][3][1] > 0: # Check if next WP index is greater than index of first WP
            obj_list[index][3][1] -= 1 # Decrement WP number
        elif rte_list[index][3][0] == "LOOP": # If not set the next waypoint to the last one when looping
                obj_list[index][3][1] = (len(rte_list[index][2])-1)
        elif rte_list[index][3][0] == "RETURN": # If not set the next waypoint to the next one and change mode
                obj_list[index][3][1] = 1
    # Switch movement mode
    if rte_list[index][3][0] == "RETURN":
        if obj_list[index][3][0] >= obj_list[index][3][1]:
            obj_list[index][3][2] = "FWD"
        else:
            obj_list[index][3][2] = "BWD"

# Checks the velocity limit of a waypoint
def check_wp_vel_limit(rte_list,index,wp_ind):
    if rte_list[index][2][wp_ind][4] == -1: # Check that there is no waypoint velocity limit
        target_vel = rte_list[index][1][4] # Set target velocity to maximum object velocity
    else: # Waypoint has velocity limit
        if rte_list[index][2][wp_ind][4] <= rte_list[index][1][4]: # If waypoint velocity limit is lower than object velocity limit
            target_vel = rte_list[index][2][wp_ind][4] # Limit velocity to waypoint velocity limit
        else:
            target_vel = rte_list[index][1][4] # Target velocity is object velocity limit
    return target_vel

# Calculate great circle distance between two coordinates using the haversine formula, credit: https://stackoverflow.com/a/45395941
def calc_distance(lat1,lon1,lat2,lon2):
    dLat,dLon = radians(lat2 - lat1),radians(lon2 - lon1)
    lat1,lat2 = radians(lat1),radians(lat2)
    dist = r_Earth * 2 * asin(sqrt(sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2))
    return dist * 1000

# Calculates a bearing between two lat-lon pairs, credit: https://stackoverflow.com/a/53434109
def calc_bearing(lat1,lon1,lat2,lon2):
    lat1,lon1 = radians(lat1),radians(lon1)
    lat2,lon2 = radians(lat2),radians(lon2)
    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2);
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dLon);
    brng = degrees(atan2(y, x));
    if brng < 0: brng += 360
    return brng

# Moves a point to a new lat and lon based on distance and bearing
def move_great_circle(lat1,lon1,dist,bearing):
    lat1,lon1 = radians(lat1),radians(lon1)
    a = radians(bearing)
    dist = dist / 1000 # Convert to km
    lat2 = asin(sin(lat1) * cos(dist/r_Earth) + cos(lat1) * sin(dist/r_Earth) * cos(a))
    lon2 = lon1 + atan2(sin(a) * sin(dist/r_Earth) * cos(lat1),cos(dist/r_Earth) - sin(lat1) * sin(lat2))
    return (degrees(lat2), degrees(lon2))


# Probes the terrain at a given location
def probe_terrain(probe_ref,lat,lon,alt):
    altitude = 0
    probe_x,probe_y,probe_z = xp.worldToLocal(lat,lon,alt) # Convert to OpenGL coordinates using input waypoint's lat, lon and alt
    probe_info = xp.probeTerrainXYZ(probe_ref,probe_x,probe_y,probe_z) # Probe using OGL coordinates
    if probe_info.result == 0:
        altitude = xp.localToWorld(probe_info.locationX,probe_info.locationY,probe_info.locationZ)[2] # Convert probe result back to world coordinates and return altitude
    return altitude

# Updates properties such as lat, lon, altitude and altitude mode for a waypoint
def get_waypoint_data(rte_list,obj_list,index):
    # Loop runs through 0 and 1, works on next and next after next waypoints
    for i in range(0,2):
        wp_index = obj_list[index][3][i] # Get index of waypoint
        # Latitude, longitude
        obj_list[index][4][i][0] = rte_list[index][2][wp_index][0] # Update waypoint latitude
        obj_list[index][4][i][1] = rte_list[index][2][wp_index][1] # Update waypoint longitude
        # Altitude
        obj_list[index][4][i][2] = rte_list[index][2][wp_index][3] # Update waypoint altitude
        obj_list[index][4][i][3] = rte_list[index][2][wp_index][2] # Update waypoint altitude mode
        # Probe ground if object has a probe and if waypoint is agl
        if obj_list[index][5][0] and obj_list[index][4][i][3] == "AGL":
            obj_list[index][4][i][4] = obj_list[index][4][i][2] + probe_terrain(obj_list[index][5][0],obj_list[index][4][i][0],obj_list[index][4][i][1],obj_list[index][4][i][2]) # Probe with lat, lon and alt, then correct WP altitude
        else:
            obj_list[index][4][i][4] = obj_list[index][4][i][2] # If no probe, corrected WP alt is alt from route list
        print(f'{obj_list[index][0]}: Updated data for WP {wp_index} (Alt: {(obj_list[index][4][i][4]):6.3f} m)')

# Calculates the bearing, distance and time to go to a waypoint
def update_waypoint_targets(obj_list,index,wp_offset):
    if wp_offset == 0: # Current object position to first waypoint
        obj_list[index][6][0][0] = calc_bearing(obj_list[index][2][0],obj_list[index][2][1],obj_list[index][4][0][0],obj_list[index][4][0][1]) # Bearing from object to next waypoint
        obj_list[index][6][0][1] = calc_distance(obj_list[index][2][0],obj_list[index][2][1],obj_list[index][4][0][0],obj_list[index][4][0][1]) # Distance from object to next waypoint
    else:
        obj_list[index][6][1][0] = calc_bearing(obj_list[index][4][0][0],obj_list[index][4][0][1],obj_list[index][4][1][0],obj_list[index][4][1][1]) # Bearing from object to second next waypoint
        obj_list[index][6][1][1] = calc_distance(obj_list[index][4][0][0],obj_list[index][4][0][1],obj_list[index][4][1][0],obj_list[index][4][1][1]) # Distance from object to second next waypoint

    if obj_list[index][2][6] != 0: # Check if object velocity is zero
        obj_list[index][6][wp_offset][2] = obj_list[index][6][wp_offset][1] / obj_list[index][2][6] # Distance / velocity = time to go
    else:
        obj_list[index][6][wp_offset][2] = float('inf') # Set object velocity to infinity

# Calculates the turn velocity at the next waypoint
def get_turn_velocity(rte_list,obj_list,index):
    if rte_list[index][0][1] == "AIRPLANE" and obj_list[index][4][1][2] > 0: # Special case: Airplanes do not decelerate when second to next waypoint is in the air
        obj_list[index][6][0][4] = check_wp_vel_limit(rte_list,index,obj_list[index][3][0]) # Turn velocity is what the route segment or object allows
    else: # All other cases
        side_accel = 0.5 * (1 - (obj_list[index][6][0][0] / 360)) # Centripetal acceleration in m/s², but scaled by turn angle as a fraction of 180
        if side_accel < 0.001:
            side_accel = 0.001 # Insurance against division by zero
        turn_radius = (check_wp_vel_limit(rte_list,index,obj_list[index][3][0])**2) / side_accel # Calculate turn radius of object with centripetal acceleration
        if turn_radius > (0.5 * obj_list[index][6][1][1]): # If turn radius is larger than half the distance to the waypoint, calculate the maximum turn velocity; r = v² / a
            if rte_list[index][3][0] == "RETURN" and (obj_list[index][3][1] == (len(rte_list[index][2])-1) or obj_list[index][3][1] == 0): # Return type of routes always end with a complete stop
                obj_list[index][6][0][4] = 0 # Turn velocity is zero
            else:
                obj_list[index][6][0][4] = sqrt(0.5 * side_accel * obj_list[index][6][1][1]) # Calculate the required velocity for a turning radius of less than half the distance to the next waypoint; v = sqrt(a*r)
        else:
            if rte_list[index][3][0] == "RETURN" and (obj_list[index][3][1] == (len(rte_list[index][2])-1) or obj_list[index][3][1] == 0): # Return type of routes always end with a complete stop
                obj_list[index][6][0][4] = 0 # Turn velocity is zero
            else:
                obj_list[index][6][0][4] = check_wp_vel_limit(rte_list,index,obj_list[index][3][0]) # Turn velocity is what the route segment or object allows

# Main object movement function
def move_objects(obj_list,rte_list,delta_t,out_info,camera_info):
    # Clear the label arrays. IMPORTANT!
    Labels_Objects.clear()
    Labels_Waypoint_1.clear()
    Labels_Waypoint_2.clear()
    for n in range(len(obj_list)): # Iterate through object list
        '''

        INITIALIZATION

        '''
        # Assign initial object values at XP session start
        if obj_list[n][2][4] == -999:
            get_waypoint_data(rte_list,obj_list,n)
            update_waypoint_targets(obj_list,n,0)
            update_waypoint_targets(obj_list,n,1)
            obj_list[n][2][4] = obj_list[n][6][0][0] # Set initial bearing
            obj_list[n][6][0][3] = check_wp_vel_limit(rte_list,n,obj_list[n][3][0]) # Set initial velocity limit
            obj_list[n][2][2] = obj_list[n][4][0][4] # Set initial altitude
            obj_list[n][2][6] = check_wp_vel_limit(rte_list,n,obj_list[n][3][0]) # Set initial velocity
            get_turn_velocity(rte_list,obj_list,n) # Calculate turn velocity
            print(f'{obj_list[n][0]}: Initial bearing {obj_list[n][2][4]:.2f}, target velocity {obj_list[n][6][0][3]:.2f}, target altitude {obj_list[n][4][0][4]:.3f}')
        '''

        UPDATE TARGETS

        '''
        # This is done at every waypoint switch
        if obj_list[n][6][0][0] == -99:
            get_waypoint_data(rte_list,obj_list,n) # Get new waypoint data
            update_waypoint_targets(obj_list,n,0) # Update waypoint target
            update_waypoint_targets(obj_list,n,1) # Update waypoint target
            get_turn_velocity(rte_list,obj_list,n) # Calculate turn velocity
            print(f'{obj_list[n][0]}: New WP bearing {obj_list[n][6][0][0]:.2f}, target altitude {obj_list[n][4][0][4]:.3f}, turn velocity target {obj_list[n][6][0][4]:.2f}')
        '''

        CALCULATE BEARING

        '''
        # Simple proportional controller for bearing adjustment
        bearing_err = obj_list[n][6][0][0] - obj_list[n][2][4] # Calculate bearing error
        # Limit the bearing error to a maximum of +/-180° because more tends to mess up turning to the next waypoint
        if bearing_err >= 180:
            bearing_err = bearing_err - 360
        elif bearing_err <= -180:
            bearing_err = 360 - bearing_err

        # Discriminate between flying airplanes and everything else
        if rte_list[n][0][1] == "AIRPLANE" and obj_list[n][4][0][2]:
            #time_arc = abs(pi * obj_list[n][6][0][1] * (bearing_err / 360)) / obj_list[n][2][6] # Calculate the time required to fly a length of arc that must be travelled to get to waypoint at current velocity
            #turn_rate_req = bearing_err / time_arc # Calculate the required turn rate
            #turn_rate_req = obj_list[n][2][6] / (obj_list[n][6][0][1] / 2)  # Calculate required turn rate in rad/s from half distance to WP and velocity
            #bank_angle_req = degrees(atan(turn_rate_req * obj_list[n][2][6]  / gravity)) # Required bank angle for turn rate in radians, then converted to degrees; See http://www.luizmonteiro.com/Article_Bank_Angle_for_Std_Rate_03.aspx

            #bank_angle_req = atan((obj_list[n][2][6]**2)/(obj_list[n][6][0][1] / 2)*gravity)
            #if bearing_err < 0:
            #    bank_angle_req = -bank_angle_req #Left turn
            #bank_angle_err = bank_angle_req - obj_list[n][2][5] # Bank angle error
            #bank_angle_p = bank_angle_err

            # Calculate the bearing change rate from current bank angle
            #heading_rate = sqrt(tan(radians(obj_list[n][2][5])) * gravity / (obj_list[n][6][0][1] / 2))
            #if bank_angle_err > 0:
            #    obj_list[n][2][4] = obj_list[n][2][4] + heading_rate
            #if bank_angle_err < 0:
            #    obj_list[n][2][4] = obj_list[n][2][4] - heading_rate
            #(rte_list[n][1][2] * delta_t)
            #

            bearing_p = bearing_err * 1
            bearing_i = bearing_err * delta_t * 1
            bearing_d = bearing_err / delta_t * 0

            turn_rate = bearing_p + bearing_i + bearing_d

            bank_target = degrees(atan(radians(turn_rate) * obj_list[n][2][6] / gravity))

            bank_angle_err = bank_target - obj_list[n][2][5]
            bank_angle_p = bank_angle_err
            # Clamp to maximum bank rate
            if bank_angle_p > (rte_list[n][1][3] * delta_t):
                bank_angle_p = (rte_list[n][1][3] * delta_t)
            if bank_angle_p < -(rte_list[n][1][3] * delta_t):
                bank_angle_p = -(rte_list[n][1][3] * delta_t)
            obj_list[n][2][5] = obj_list[n][2][5] + bank_angle_p
            # Clamp to maximum bank angle
            if obj_list[n][2][5] > rte_list[n][1][6]:
                obj_list[n][2][5] = rte_list[n][1][6]
            if obj_list[n][2][5] < -rte_list[n][1][6]:
                obj_list[n][2][5] = -rte_list[n][1][6]

            heading_rate = degrees(tan(radians(obj_list[n][2][5]) * gravity / obj_list[n][2][6]))

            obj_list[n][2][4] = obj_list[n][2][4] + (heading_rate * delta_t)

            #print(f'{turn_rate:.1f},{bank_target:.1f}°, {bank_angle_err:.1f}° --> {obj_list[n][2][5]:.2f}°')
        else:
            bearing_p = bearing_err # Proportional control is simply the bearing error, no proportional constant
            if bearing_p > (rte_list[n][1][2] * delta_t): # Make sure proportional control does not exceed turn rate
                bearing_p = (rte_list[n][1][2] * delta_t)
            if bearing_p < -(rte_list[n][1][2] * delta_t):
                bearing_p = -(rte_list[n][1][2] * delta_t)

            obj_list[n][2][4] = obj_list[n][2][4] + bearing_p # New bearing is current bearing plus proportional control

        if obj_list[n][2][4] < 0: # Clamp bearing range to 0 or 360
            obj_list[n][2][4] = 360
        if obj_list[n][2][4] > 360: # Clamp bearing range to 0 or 360
            obj_list[n][2][4] = 0

        '''

        CALCULATE VELOCITY

        '''
        # Check if deceleration for next waypoint is required
        if (obj_list[n][6][0][3] != obj_list[n][6][0][4]):
            # If yes, check if object is at or below required deceleration distance
            #print(obj_list[n][0]+str(obj_list[n][6][0][1])+" , "+str(((obj_list[n][6][0][4] - obj_list[n][2][6])**2) / (2 * 0.5 * rte_list[n][1][0])))
            if obj_list[n][6][0][1] <= (((obj_list[n][2][6] - obj_list[n][6][0][4])**2) / (2 * 0.5 * rte_list[n][1][0])): # Braking distance formula: s = v^2 / 2*a
                #print(obj_list[n][0]+": Slowing down for turn") # Debug
                obj_list[n][6][0][3] = obj_list[n][6][0][4] # Assign turn velocity

        # Accelerate or slow object
        if obj_list[n][2][6] < obj_list[n][6][0][3]:
            obj_list[n][2][6] = obj_list[n][2][6] + (rte_list[n][1][0] * delta_t) # Accelerate
            if obj_list[n][2][6] > obj_list[n][6][0][3]: # Clamp to target velocity
                obj_list[n][2][6] = obj_list[n][6][0][3]
        if obj_list[n][2][6] > obj_list[n][6][0][3]:
            obj_list[n][2][6] = obj_list[n][2][6] - (rte_list[n][1][0] * delta_t) # Decelerate
            if obj_list[n][2][6] < obj_list[n][6][0][3]:
                obj_list[n][2][6] = obj_list[n][6][0][3] # Clamp to target velocity

        # Release turn velocity constraint after turn has been completed
        if (abs(bearing_err) < 5):
            obj_list[n][6][0][3] = check_wp_vel_limit(rte_list,n,obj_list[n][3][0])
        '''

        CALCULATE MOVEMENT

        '''
        # Lateral movement from lat1, lon1 with a given velocity and bearing
        obj_list[n][2][0],obj_list[n][2][1] = move_great_circle(obj_list[n][2][0],obj_list[n][2][1],(obj_list[n][2][6] * delta_t),obj_list[n][2][4])
        # Vertical movement
        if rte_list[n][0][1] == "HELICOPTER" or rte_list[n][0][1] == "AIRPLANE":

            target_pitch = atan2((obj_list[n][4][0][4] - obj_list[n][2][2]),obj_list[n][6][0][1]) # Calculate target path pitch in radians as tangens from vertical (opposite) and horizontal (adjacent) distance



            obj_list[n][2][2] = obj_list[n][2][2] + (tan(target_pitch) * (obj_list[n][2][6] * delta_t)) # Altitude is tangens of path pitch angle in radians times the distance covered in this tick

        '''

        UPDATE STATUS

        '''
        # Update waypoint data
        update_waypoint_targets(obj_list,n,0)
        update_waypoint_targets(obj_list,n,1)
        '''

        WAYPOINT SWITCHING

        '''
        # Calculate trigger distance for the waypoint switcher
        min_dist = obj_list[n][6][0][4]
        if min_dist < 3:
            min_dist = 3

        if (obj_list[n][6][0][1] < min_dist) and (obj_list[n][2][6] == obj_list[n][6][0][3]): # Object has attained turn velocity
            print(obj_list[n][0]+" has arrived at waypoint "+str(obj_list[n][3][0]+1))
            waypoint_switcher(obj_list,rte_list,n)
            obj_list[n][6][0][0] = -99
        '''

        STATUS INFORMATION

        '''
        # Status output
        '''
        print("------- "+obj_list[n][0]+"\n"+
              "Pos: "+str(obj_list[n][2][0])+" N, "+str(obj_list[n][2][1])+" E, Heading: "+f'{obj_list[n][2][4]:.1f}'+"°, Velocity: "+f'{obj_list[n][2][6]:.1f}'+" m/s\n"+
              "Current WP  : "+str(obj_list[n][3][0]+1)+"/"+str(len(rte_list[n][2]))+" ("+str(obj_list[n][4][0][0])+" N, "+str(obj_list[n][4][0][1])+" E), Bearing: "+f'{obj_list[n][6][0][0]}'+",Dist: "+f'{(obj_list[n][6][0][1]/1000):.3f}'+" km, TTG: "+f'{obj_list[n][6][0][2]:.2f}'+" s\n"+
              "Following WP: "+str(obj_list[n][3][1]+1)+"/"+str(len(rte_list[n][2]))+" ("+str(obj_list[n][4][1][0])+" N, "+str(obj_list[n][4][1][1])+" E), Bearing: "+f'{obj_list[n][6][1][0]}'+",Dist: "+f'{(obj_list[n][6][1][1]/1000):.3f}'+" km, TTG: "+f'{obj_list[n][6][1][2]:.2f}'+" s\n"
              )
        '''
        #Object: 0:Alias,1:Lat,2:Lon,3:Alt,4:Hdg,5:Vel,6:Total WP
        #Next WP: 7:Index,8:Lat,9:Lon,10:Alt,11:Alt mode,12:Brg,13:Dist,14:TTG,
        #Follow-Up WP: 15:Index,16:Lat,17:Lon,18:Alt,19:Alt mode,20:Brg,21:Dist,22:TTG
        out_info.append([obj_list[n][0],obj_list[n][2][0],obj_list[n][2][1],obj_list[n][2][2],obj_list[n][2][4],obj_list[n][2][6],len(rte_list[n][2]),
                         (obj_list[n][3][0]+1),obj_list[n][4][0][0],obj_list[n][4][0][1],obj_list[n][4][0][4],obj_list[n][4][0][3],obj_list[n][6][0][0],obj_list[n][6][0][1],obj_list[n][6][0][2],
                         (obj_list[n][3][1]+1),obj_list[n][4][1][0],obj_list[n][4][1][1],obj_list[n][4][1][4],obj_list[n][4][0][3],obj_list[n][6][1][0],obj_list[n][6][1][1],obj_list[n][6][1][2]])
        '''

        UPDATE X-PLANE INSTANCES

        '''
        # Update X-Plane instance position
        obj_x,obj_y,obj_z = xp.worldToLocal(obj_list[n][2][0],obj_list[n][2][1],obj_list[n][2][2])
        wp1_x,wp1_y,wp1_z = xp.worldToLocal(obj_list[n][4][0][0],obj_list[n][4][0][1],obj_list[n][4][0][4])
        wp2_x,wp2_y,wp2_z = xp.worldToLocal(obj_list[n][4][1][0],obj_list[n][4][1][1],obj_list[n][4][1][4])
        # Update object label array [OGL_x,OGL_y,OGL_z],string from: object name, object bearing, object velocity
        Labels_Objects.append(["Object",[obj_x,obj_y,obj_z,1.0],f'{obj_list[n][0]} {obj_list[n][2][2]:6.2f} m {obj_list[n][2][4]:6.2f}° {obj_list[n][2][6]:6.2f} m/s WP {(obj_list[n][3][0]+1):d} E: {(bearing_err):4.2f} TV: {(obj_list[n][6][0][4]):3.2f}'])
        # Update waypoint label arrays [OGL_x,OGL_y,OGL_z],object name
        Labels_Waypoint_1.append(["Waypoint",[wp1_x,wp1_y,wp1_z,1.0],f'X -- {obj_list[n][0]} WP {obj_list[n][3][0]+1}/{len(rte_list[n][2])} {obj_list[n][4][0][4]:6.2f} m'])
        Labels_Waypoint_2.append(["Waypoint",[wp2_x,wp2_y,wp2_z,1.0],f'X -- {obj_list[n][0]} WP {obj_list[n][3][1]+1}/{len(rte_list[n][2])} {obj_list[n][4][1][4]:6.2f} m'])
        # Assemble instance position information
        position = (obj_x,obj_y,obj_z,obj_list[n][2][3],obj_list[n][2][4],obj_list[n][2][5]) # X,Y,Z,Pitch,Heading,Roll
        # Update object position for camera
        if n == camera_info['num']:
            camera_info['x'] = obj_x
            camera_info['y'] = obj_y
            camera_info['z'] = obj_z
        # Update XP instance
        for m in range(len(obj_list[n][1])):
            #print(obj_list[n][1][m])
            xp.instanceSetPosition(obj_list[n][1][m],position,data=None)
