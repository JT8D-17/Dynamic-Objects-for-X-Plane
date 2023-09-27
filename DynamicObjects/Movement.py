#!/usr/bin/python
'''
MODULES
'''
from math import asin,atan2,sin,cos,degrees,radians,sqrt
import os
import xp
'''
VARIABLES
'''
r_Earth = 6372.8
'''
FUNCTIONS
'''
# LEGACY: Switches to the next waypoint upon reaching the waypoint
def waypoint_switcher(obj_list,rte_list,ind):
    # Switch next waypoint
    obj_list[ind][3][0] = obj_list[ind][3][1] # Make second waypoint from now the next one
    # Switch waypoint after next waypoint
    if obj_list[ind][3][2] == "FWD": # Movement mode forward
        if obj_list[ind][3][1] < (len(rte_list[ind][2])-1): # Check if next WP index is less than index of last WP
            obj_list[ind][3][1] += 1 # Increment WP number
        elif rte_list[ind][3][0] == "LOOP": # If not set the next waypoint to the first one when looping
                obj_list[ind][3][1] = 0
        elif rte_list[ind][3][0] == "RETURN": # If not set the next waypoint to the previous one and change mode
                obj_list[ind][3][1] = (len(rte_list[ind][2])-1)-1
    if obj_list[ind][3][2] == "BWD": # Movement mode backward
        if obj_list[ind][3][1] > 0: # Check if next WP index is greater than index of first WP
            obj_list[ind][3][1] -= 1 # Decrement WP number
        elif rte_list[ind][3][0] == "LOOP": # If not set the next waypoint to the last one when looping
                obj_list[ind][3][1] = (len(rte_list[ind][2])-1)
        elif rte_list[ind][3][0] == "RETURN": # If not set the next waypoint to the next one and change mode
                obj_list[ind][3][1] = 1
    # Switch movement mode
    if rte_list[ind][3][0] == "RETURN":
        if obj_list[ind][3][0] >= obj_list[ind][3][1]:
            obj_list[ind][3][2] = "FWD"
        else:
            obj_list[ind][3][2] = "BWD"
    # Release deceleration mode, if active
    if obj_list[ind][3][3] == 1:
        obj_list[ind][3][3] = 0 # Set deceleration mode
    #print(obj_list[ind][3])

# Checks the velocity limit of a waypoint
def check_wp_vel_limit(rte_list,ind,wp_ind):
    if rte_list[ind][2][wp_ind][4] == -1: # Check that there is no waypoint velocity limit
        target_vel = rte_list[ind][1][4] # Set target velocity to maximum object velocity
    else: # Waypoint has velocity limit
        if rte_list[ind][2][wp_ind][4] <= rte_list[ind][1][4]: # If waypoint velocity limit is greater than object velocity limit
            target_vel = rte_list[ind][2][wp_ind][4] # Limit velocity to waypoint velocity limit
        else:
            target_vel = rte_list[ind][1][4] # Target velocity is object velocity limit
    return target_vel

# Manages an object's velocity based on acceleration
def velocity_manager(obj_list,rte_list,ind,obj_vel,wp_dist,wp_ttg,delta_t):
    accel = rte_list[ind][1][0] * delta_t # Get acceleration from performance data
    wp_ind = obj_list[ind][3][0] # Get waypoint index
    target_vel = 0
    # Set target velocity
    if wp_ind == 0 or wp_ind == (len(rte_list[ind][2])-1):
        if rte_list[ind][3][0] == "LOOP": # Only for looping routes
            target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)
        else:
            #if obj_vel == check_wp_vel_limit(rte_list,ind,wp_ind) and wp_dist < (0.5 * rte_list[ind][1][0] * wp_ttg**2):
            #    target_vel = 0
            #else:
                target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)
            #if obj_list[ind][3][3] == 0 and wp_dist > 0:
            #    target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)
            #     #if wp_ttg > (obj_vel / accel) and obj_list[ind][3][3] == 0:
            #    if wp_dist < (0.5 * obj_vel**2 / accel):
             #   #if obj_vel == check_wp_vel_limit(rte_list,ind,wp_ind) and wp_ttg <= (obj_vel / accel):
            #        target_vel = 0 # Stop at route start or route end
            #        obj_list[ind][3][3] = 1 # Set deceleration mode

    else:
        target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)


    print(obj_list[ind][0],(obj_vel / rte_list[ind][1][0]))

    if obj_vel < target_vel:
        obj_vel = obj_vel + accel # Accelerate
        if obj_vel > target_vel: # Clamp to target velocity
            obj_vel = target_vel
    if obj_vel > target_vel:
        obj_vel = obj_vel - accel # Decelerate
        if obj_vel > target_vel:
            obj_vel = target_vel # Clamp to target velocity

    return obj_vel

# Manages an object's bearing
def bearing_manager(obj_list,rte_list,ind,obj_brg,wp1_brg,wp2_brg,wp1_ttg,delta_t):
    #
    turn_rate = rte_list[ind][1][2] * delta_t # Heading/turn rate from object performance data scaled by refresh interval
    #
    if obj_list[ind][3][0] > 0 and obj_list[ind][3][0] < (len(rte_list[ind][2])-1): # Current waypoint must not be first or last to initiate a turn
        if (wp1_ttg * 1.1) < ((wp2_brg - wp1_brg) / turn_rate): # Check if time to go + 10% is less than the required time for the turn
            waypoint_switcher(obj_list,rte_list,ind) # Switch to next waypoint
    else:
        if wp1_ttg <= 1: # Switch waypoint at 1 sec before arrival
            waypoint_switcher(obj_list,rte_list,ind) # Switch to next waypoint

    if (wp1_brg - obj_brg) < turn_rate:
        heading = wp1_brg
    else:
        if (wp1_brg - obj_brg) > 0: # Right turn
            heading = obj_brg + turn_rate
        if (wp1_brg - obj_brg) < 0: # Left turn
            heading = obj_brg - turn_rate
    return heading

# Calculate great circle distance between two coordinates using the haversine formula, credit: https://stackoverflow.com/a/45395941
def haversine(lat1,lon1,lat2,lon2):
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
def move(lat1,lon1,dist,bearing):
    lat1,lon1 = radians(lat1),radians(lon1)
    a = radians(bearing)
    dist = dist / 1000 # Convert to km
    lat2 = asin(sin(lat1) * cos(dist/r_Earth) + cos(lat1) * sin(dist/r_Earth) * cos(a))
    lon2 = lon1 + atan2(sin(a) * sin(dist/r_Earth) * cos(lat1),cos(dist/r_Earth) - sin(lat1) * sin(lat2))
    return (degrees(lat2), degrees(lon2))

# Returns a waypoint's coordinates by index
def wp_coords(rte_list,obj_list,index,wp_index):
    return rte_list[index][2][wp_ind][0], rte_list[index][2][wp_ind][1]

# Returns latitude, longitude, distance and bearing of a waypoint
def return_waypoint_data(rte_list,obj_list,index,in_vel,offset):
    wp_index1,wp_index2 = obj_list[index][3][0],obj_list[index][3][1] # Get indicesof waypoints
    if offset == 0:
        lat1,lon1 = obj_list[index][2][0],obj_list[index][2][1] # Current object position
        lat2,lon2 = rte_list[index][2][wp_index1][0],rte_list[index][2][wp_index1][1]
    else:
        lat1,lon1 = rte_list[index][2][wp_index1][0],rte_list[index][2][wp_index1][1]
        lat2,lon2 = rte_list[index][2][wp_index2][0],rte_list[index][2][wp_index2][1]

    out_dist = haversine(lat1,lon1,lat2,lon2)
    out_brg = calc_bearing(lat1,lon1,lat2,lon2)

    if in_vel != 0:
        out_ttg = out_dist / in_vel # Time to go
    else:
        out_ttg = float('inf')

    return (lat2,lon2,out_brg,out_dist,out_ttg)

# Main object movement function
def move_objects(obj_list,rte_list,delta_t,out_info):
    for n in range(len(obj_list)): # Iterate through object list
        # Initial waypoint data assignment
        wp_next1 = return_waypoint_data(rte_list,obj_list,n,obj_list[n][2][6],0)
        wp_next2 = return_waypoint_data(rte_list,obj_list,n,obj_list[n][2][6],1)

        # Update Object velocity
        obj_list[n][2][6] = velocity_manager(obj_list,rte_list,n,obj_list[n][2][6],wp_next1[3],wp_next1[4],delta_t) # Manage object velocity
        # Update object bearing
        obj_list[n][2][4] = bearing_manager(obj_list,rte_list,n,obj_list[n][2][4],wp_next1[2],wp_next2[2],wp_next2[4],delta_t) # Manage object heading
        # Update position
        obj_list[n][2][0],obj_list[n][2][1] = move(obj_list[n][2][0],obj_list[n][2][1],(obj_list[n][2][6] * delta_t),obj_list[n][2][4]) # Move object to new lat and lon, using the distance covered in this tick

        # Update waypoint data
        wp_next1 = return_waypoint_data(rte_list,obj_list,n,obj_list[n][2][6],0)
        wp_next2 = return_waypoint_data(rte_list,obj_list,n,obj_list[n][2][6],1)

        # Status output
        '''
        print("------- "+obj_list[n][0]+"\n"+
              "Pos: "+str(obj_list[n][2][0])+" N, "+str(obj_list[n][2][1])+" E, Heading: "+f'{obj_list[n][2][4]:.1f}'+"°, Velocity: "+f'{obj_list[n][2][6]:.1f}'+" m/s\n"+
              "Current WP  : "+str(obj_list[n][3][0]+1)+"/"+str(len(rte_list[n][2]))+" ("+str(wp_next1[0])+" N, "+str(wp_next1[1])+" E), Bearing: "+f'{wp_next1[2]}'+",Dist: "+f'{(wp_next1[3]/1000):.3f}'+" km, TTG: "+f'{wp_next1[4]:.2f}'+" s\n"+
              "Following WP: "+str(obj_list[n][3][1]+1)+"/"+str(len(rte_list[n][2]))+" ("+str(wp_next2[0])+" N, "+str(wp_next2[1])+" E), Bearing: "+f'{wp_next2[2]}'+",Dist: "+f'{(wp_next2[3]/1000):.3f}'+" km, TTG: "+f'{wp_next2[4]:.2f}'+" s\n"
              )
        '''
        #Object: 0:Alias,1:Lat,2:Lon,3:Hdg,4:Vel,5:Total WP
        #Next WP: 6:Index,7:Lat,8:Lon,9:Brg,10:Dist,11:TTG,
        #Follow-Up WP: 12:Index,13:Lat,14:Lon,15:Brg,16:Dist,17:TTG
        out_info.append([obj_list[n][0],obj_list[n][2][0],obj_list[n][2][1],obj_list[n][2][4],obj_list[n][2][6],len(rte_list[n][2]),
                         obj_list[n][3][0],wp_next1[0],wp_next1[1],wp_next1[2],wp_next1[3],wp_next1[4],
                         obj_list[n][3][1],wp_next2[0],wp_next2[1],wp_next2[2],wp_next2[3],wp_next2[4]])
        #print(out_info)

        # Update X-Plane instances
        obj_x,obj_y,obj_z = xp.worldToLocal(obj_list[n][2][0], obj_list[n][2][1],obj_list[n][2][2])
        position = (obj_x,obj_y,obj_z,obj_list[n][2][3],obj_list[n][2][4],obj_list[n][2][5]) # X,Y,Z,Pitch,Heading,Roll
        for m in range(len(obj_list[n][1])):
            #print(obj_list[n][1][m])
            xp.instanceSetPosition(obj_list[n][1][m],position,data=None)
        #distance = haversine(obj_list[n][2][0],obj_list[n][2][1],wp_next1_lat,wp_next1_lon) # Update distance to next waypoint
        #if wp_next1_dist <= (obj_list[n][2][6] * delta_t): # Check if the remaining distance is less than the distance that would be covered this tick
        #    waypoint_switcher(obj_list,rte_list,n)
