#!/usr/bin/python
'''
MODULES
'''
from math import asin,atan2,sin,cos,degrees,radians,sqrt
import os
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
#
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
def velocity_manager(obj_list,rte_list,ind,obj_vel,wp_dist,wp_ttg,dt):
    accel = rte_list[ind][1][0] # Get acceleration from performance data
    wp_ind = obj_list[ind][3][0] # Get waypoint index
    target_vel = 0
    # Set target velocity
    if wp_ind == 0 or wp_ind == (len(rte_list[ind][2])-1):
        if rte_list[ind][3][0] == "LOOP": # Only for looping routes
            target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)
        else:
            if wp_dist > (0.5 * accel * wp_ttg**2):
                target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)
            elif obj_list[ind][3][3] == 0: # Check if deceleration mode is on
                target_vel = 0 # Stop at route start or route end
                obj_list[ind][3][3] = 1 # Set deceleration mode
    else:
        target_vel = check_wp_vel_limit(rte_list,ind,wp_ind)


    print(target_vel, (obj_vel / accel))

    if obj_vel < target_vel:
        obj_vel = obj_vel + (accel * dt) # Accelerate
        if obj_vel > target_vel: # Clamp to target velocity
            obj_vel = target_vel
    if obj_vel > target_vel:
        obj_vel = obj_vel - (accel * dt) # Decelerate
        if obj_vel > target_vel:
            obj_vel = target_vel # Clamp to target velocity

    return obj_vel
# Manages an object's bearing
def bearing_manager(obj_list,rte_list,ind,obj_brg,wp1_brg,wp2_brg,wp1_ttg):
    #
    turn_rate = rte_list[ind][1][2] #* 9 # Heading/turn rate from object performance data
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
# Main object movement function
def move_objects(obj_list,rte_list,dt):
    for n in range(len(obj_list)): # Iterate through object list
        # Next waypoint
        wp_next1_ind = obj_list[n][3][0] # Index
        wp_next1_lat,wp_next1_lon = rte_list[n][2][wp_next1_ind][0],rte_list[n][2][wp_next1_ind][1] # Coordinates
        wp_next1_dist = haversine(obj_list[n][2][0],obj_list[n][2][1],wp_next1_lat,wp_next1_lon) # Distance from current position
        wp_next1_brg = calc_bearing(obj_list[n][2][0],obj_list[n][2][1],wp_next1_lat,wp_next1_lon) # Current bearing
        # Waypoint after next waypoint
        wp_next2_ind = obj_list[n][3][1] # Index
        wp_next2_lat,wp_next2_lon = rte_list[n][2][wp_next2_ind][0],rte_list[n][2][wp_next2_ind][1] # Coordinates
        wp_next2_dist = haversine(wp_next1_lat,wp_next1_lon,wp_next2_lat,wp_next2_lon) + wp_next1_dist # Distance from current position, considering next waypoint
        wp_next2_brg = calc_bearing(wp_next1_lat,wp_next1_lon,wp_next2_lat,wp_next2_lon) # Bearing between waypoints

        if obj_list[n][2][6] != 0:
            wp_next1_ttg = wp_next1_dist / obj_list[n][2][6] # Time to go
            wp_next2_ttg = wp_next2_dist / obj_list[n][2][6] # Time to go
        else:
            wp_next1_ttg = float('inf')
            wp_next2_ttg = float('inf')
        # Update Object velocity
        obj_list[n][2][6] = velocity_manager(obj_list,rte_list,n,obj_list[n][2][6],wp_next1_dist,wp_next1_ttg,dt) # Manage object velocity
        # Update object bearing
        obj_list[n][2][4] = bearing_manager(obj_list,rte_list,n,obj_list[n][2][4],wp_next1_brg,wp_next2_brg,wp_next1_ttg) # Manage object heading
        # Update position
        obj_list[n][2][0],obj_list[n][2][1] = move(obj_list[n][2][0],obj_list[n][2][1],(obj_list[n][2][6] * dt),obj_list[n][2][4]) # Move object to new lat and lon, using the distance covered in this tick
        # Status output
        print("------- "+obj_list[n][0]+"\n"+
              "Pos: "+str(obj_list[n][2][0])+" N, "+str(obj_list[n][2][1])+" E, Heading: "+f'{obj_list[n][2][4]:.1f}'+"°, Velocity: "+f'{obj_list[n][2][6]:.1f}'+" m/s\n"+
              "Current WP  : "+str(wp_next1_ind+1)+"/"+str(len(rte_list[n][2]))+" ("+str(wp_next1_lat)+" N, "+str(wp_next1_lon)+" E), Bearing: "+f'{wp_next1_brg}'+",Dist: "+f'{(wp_next1_dist/1000):.3f}'+" km, TTG: "+f'{wp_next1_ttg:.2f}'+" s\n"+
              "Following WP: "+str(wp_next2_ind+1)+"/"+str(len(rte_list[n][2]))+" ("+str(wp_next2_lat)+" N, "+str(wp_next2_lon)+" E), Bearing: "+f'{wp_next2_brg}'+",Dist: "+f'{(wp_next2_dist/1000):.3f}'+" km, TTG: "+f'{wp_next2_ttg:.2f}'+" s\n"
              )

        #distance = haversine(obj_list[n][2][0],obj_list[n][2][1],wp_next1_lat,wp_next1_lon) # Update distance to next waypoint
        #if wp_next1_dist <= (obj_list[n][2][6] * dt): # Check if the remaining distance is less than the distance that would be covered this tick
        #    waypoint_switcher(obj_list,rte_list,n)
