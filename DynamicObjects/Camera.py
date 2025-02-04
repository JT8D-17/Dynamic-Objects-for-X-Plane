#!/usr/bin/python
'''
MODULES
'''
import xp,math
'''
VARIABLES
'''
x,y,dx,dy,dz = 0,0,0,0,0
heading,pitch = 0,0
x_old,y_old = 0,0
dist = 75
'''
FUNCTIONS
'''
def Camera_Watchdog(self):
    (has_control,how_long) = xp.isCameraBeingControlled()
    if self.Object_Camera['num'] == -1 and has_control == 1:
        xp.dontControlCamera()

def MyFunc(outCameraPosition,inIsLosingControl,inRefCon):
    global dx,dy,dz,x,y,heading,pitch,x_old,y_old,dist

    if inIsLosingControl:
        xp.dontControlCamera()
    if (outCameraPosition and not inIsLosingControl):
        # First get the screen size and mouse location.  We will use this to decide
        # what part of the orbit we are in.  The mouse will move us up-down and around.
        w, h = xp.getScreenSize()
        if inRefCon.CameraMouseStatus['RMB'] == 2:
            x_old,y_old = xp.getMouseLocationGlobal()
        if inRefCon.CameraMouseStatus['RMB'] == 1:
            x,y = xp.getMouseLocationGlobal()
            d_heading = (x - x_old) * 0.01
            if d_heading > 5:
                d_heading = 5
            if d_heading < -5:
                d_heading = -5
            heading = heading + d_heading
            #heading = 360.0 * float(x) / float(w)
            d_pitch = (y - y_old) * 0.01
            if d_pitch > 2:
                d_pitch = 2
            if d_pitch < -2:
                d_pitch = -2
            pitch = pitch + d_pitch
            if pitch > 60:
                pitch = 60
            if pitch < -60:
                pitch = -60
            #pitch = 20.0 * ((float(y) / float(h) * 2.0) - 1.0)
        if inRefCon.CameraMouseStatus['RMB'] == 0:
            x_old,y_old = xp.getMouseLocationGlobal()


        if inRefCon.CameraMouseStatus['WHL'] != 0:
            dist = dist + inRefCon.CameraMouseStatus['WHL'] * -3
            inRefCon.CameraMouseStatus['WHL'] = 0

        dx = -dist * math.sin(math.radians(heading))
        dy = -dist * math.tan(math.radians(pitch))
        dz = dist * math.cos(math.radians(heading))
        #dx = dist * math.cos(math.radians(heading)) * math.cos(math.radians(pitch))
        #dz = dist * math.cos(math.radians(heading)) * math.sin(math.radians(pitch))
        #dy = dist * math.sin(math.radians(heading))

        outCameraPosition[0] = inRefCon.Object_Camera['x'] + dx
        outCameraPosition[1] = inRefCon.Object_Camera['y'] + dy
        outCameraPosition[2] = inRefCon.Object_Camera['z'] + dz
        outCameraPosition[3] = pitch
        outCameraPosition[4] = heading
        outCameraPosition[5] = 0
    return 1

