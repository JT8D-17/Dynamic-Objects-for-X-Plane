#!/usr/bin/python
'''
MODULES
'''
import xp
from DynamicObjects import Camera
'''
VARIABLES
'''
columns = (["Object",200],["Position",150],["Altitude",55],["Heading",55],["Velocity",65],["Next WP",320],["Follow-Up WP",320])
# FONT
color = 1.0, 1.0, 1.0
'''
FUNCTIONS
'''
# Initialize the object information window
def Init_Window(self):
    scr_l,scr_t,scr_r,scr_b = xp.getScreenBoundsGlobal()
    windowInfo = ((scr_l+self.WindowDims['l']),(scr_t-self.WindowDims['t']),(scr_l+self.WindowDims['l']+self.WindowDims['w']),(scr_t-(self.WindowDims['t']+self.WindowDims['h'])),1,DrawWindowCallback,MouseClickCallback,KeyCallback,CursorCallback,MouseWheelCallback,self,xp.WindowDecorationRoundRectangle,xp.WindowLayerFloatingWindows,None)
    self.WindowId = xp.createWindowEx(windowInfo)
    #xp.setWindowIsVisible(self.WindowId,0)
# Automatically resize the window to fit its content
def Auto_Resize(self):
    if self.WindowId:
        #scr_l,scr_t,scr_r,scr_b = xp.getScreenBoundsGlobal()
        (self.WindowDims['l'],self.WindowDims['t'],self.WindowDims['r'],self.WindowDims['b']) = xp.getWindowGeometry(self.WindowId)
        if (self.WindowDims['t'] - self.WindowDims['b']) < self.WindowDim_Req['h']:
            self.WindowDims['h'] = (self.WindowDims['t']-self.WindowDim_Req['h'])
            xp.setWindowGeometry(self.WindowId,self.WindowDims['l'],self.WindowDims['t'],self.WindowDims['r'],self.WindowDims['h'])
        if (self.WindowDims['r'] - self.WindowDims['l']) < self.WindowDim_Req['w']:
            self.WindowDims['w'] = (self.WindowDims['l']+self.WindowDim_Req['w'])
            xp.setWindowGeometry(self.WindowId,self.WindowDims['l'],self.WindowDims['t'],self.WindowDims['w'],self.WindowDims['b'])
        #print(self.WindowDims['t'],self.WindowDims['b'],self.WindowDim_Req['h'])

# This draws the window's content
def Draw_ObjStatus(inRefCon,inWindowID,in_top):
    # WINDOW
    (left, top, right, bottom) = xp.getWindowGeometry(inWindowID)
    inRefCon.WindowContent['l'],inRefCon.WindowContent['t'] = int(left+inRefCon.Padding['l']),int(top-in_top-inRefCon.Padding['t'])
    offset_tab = inRefCon.WindowContent['l']
    win_req_width = 0
    NumLineLimit = inRefCon.MaxLines
    # HEADERS
    if NumLineLimit > len(inRefCon.Object_List):
        NumLineLimit = len(inRefCon.Object_List)
    for i in range(len(columns)):
        win_req_width += columns[i][1] + inRefCon.Padding['l']
        offset_line = inRefCon.WindowContent['t']
        dashes = ""
        for j in range(0,int(columns[i][1]/xp.measureString(inRefCon.WindowFont,"-"))):
            dashes = dashes + "-"
        if xp.measureString(inRefCon.WindowFont,columns[i][0]) > columns[i][1]:
            string = dashes
        xp.drawString(color,offset_tab,offset_line,columns[i][0], 0,inRefCon.WindowFont)
        offset_line -= inRefCon.LineHeight
        xp.drawString(color,offset_tab,offset_line,dashes, 0,inRefCon.WindowFont)
        if len(inRefCon.Object_Info) < NumLineLimit:
            NumLineLimit = len(inRefCon.Object_Info)
        for k in range(NumLineLimit):
            offset_line -= inRefCon.LineHeight
            if columns[i][0] == "Object":
                xp.drawString(color,offset_tab,offset_line,inRefCon.Object_Info[k][0], 0,inRefCon.WindowFont)
                if inRefCon.Object_Camera['num'] == k:
                    xp.drawTranslucentDarkBox(offset_tab,(offset_line+8),(offset_tab + columns[i][1]),(offset_line-3))
                inRefCon.Object_Window[k][1] = [offset_tab,(offset_line+8),(offset_tab + columns[i][1]),(offset_line-3)]
            if columns[i][0] == "Position":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][1]:8.5f} N, {inRefCon.Object_Info[k][2]:9.5f} E', 0,inRefCon.WindowFont)
            if columns[i][0] == "Altitude":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][3]:6.2f} m', 0,inRefCon.WindowFont)
            if columns[i][0] == "Heading":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][4]:6.2f} °', 0,inRefCon.WindowFont)
            if columns[i][0] == "Velocity":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][5]:6.2f} m/s', 0,inRefCon.WindowFont)
            if columns[i][0] == "Next WP":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][7]:2.0f}/{inRefCon.Object_Info[k][6]:2.0f},{inRefCon.Object_Info[k][10]:8.1f} m {inRefCon.Object_Info[k][11]}, {inRefCon.Object_Info[k][12]:6.2f}°, {inRefCon.Object_Info[k][13]:8.0f} m in {inRefCon.Object_Info[k][14]:6.0f} s', 0,inRefCon.WindowFont)
            if columns[i][0] == "Follow-Up WP":
                xp.drawString(color,offset_tab,offset_line,f'{inRefCon.Object_Info[k][15]:2.0f}/{inRefCon.Object_Info[k][6]:2.0f},{inRefCon.Object_Info[k][18]:8.1f} m {inRefCon.Object_Info[k][19]}, {inRefCon.Object_Info[k][20]:6.2f}°, {inRefCon.Object_Info[k][21]:8.0f} m in {inRefCon.Object_Info[k][22]:6.0f} s', 0,inRefCon.WindowFont)

        offset_tab += columns[i][1] + inRefCon.Padding['l']

    #print(f'{win_req_width:d}')
    #print(inRefCon.Padding['t'] + (NumLineLimit + 2) * inRefCon.LineHeight)
    if (inRefCon.Padding['t'] + (NumLineLimit + 2) * inRefCon.LineHeight) > inRefCon.WindowDim_Req['h']:
        inRefCon.WindowDim_Req['h'] = (inRefCon.Padding['t'] + (NumLineLimit + 2) * inRefCon.LineHeight)
    if win_req_width > inRefCon.WindowDim_Req['w']:
        inRefCon.WindowDim_Req['w'] = win_req_width

# The callback for the window
def DrawWindowCallback(inWindowID,inRefCon):
    # First we get the location of the window passed in to us.
    (left, top, right, bottom) = xp.getWindowGeometry(inRefCon.WindowId)
    #xp.drawTranslucentDarkBox(left, top, right, bottom)
    Draw_ObjStatus(inRefCon,inRefCon.WindowId,0)

# Callback for keypresses
def KeyCallback(inWindowID, inKey, inFlags, inVirtualKey, inRefCon, losingFocus):
    pass
# Callback for mouse clicks
def MouseClickCallback(inWindowID, x, y, inMouse, inRefCon):
    if inMouse == xp.MouseDown: # Only react on left click
        for i in range(len(inRefCon.Object_Window)): # Loop through window object information array
            if x > inRefCon.Object_Window[i][1][0] and x < inRefCon.Object_Window[i][1][2] and y < inRefCon.Object_Window[i][1][1] and y > inRefCon.Object_Window[i][1][3]: # Check if click x and y is on object's name
                if inRefCon.Object_Camera['num'] != i:
                    inRefCon.Object_Camera['num'] = i
                    xp.controlCamera(xp.ControlCameraUntilViewChanges,Camera.MyFunc,inRefCon)
                    Init_Camera_Window(inRefCon)
                else:
                    inRefCon.Object_Camera['num'] = -1
                    xp.destroyWindow(inRefCon.CameraWindowID)
                    xp.getWindowIsVisible(inRefCon.CameraWindowID)
                    xp.dontControlCamera()
    return 1
# Callback for mouse cursor
def CursorCallback(inWindowID, x, y, inRefCon):
    return xp.CursorDefault
# Callback for mouse wheel
def MouseWheelCallback(inWindowID, x, y, wheel, clicks, inRefCon):
    return 1


# Initialize the camera control overlay window
def Init_Camera_Window(inRefCon):
    scr_l,scr_t,scr_r,scr_b = xp.getScreenBoundsGlobal()
    windowInfo = (scr_l,scr_t,scr_r,scr_b,1,CameraWindowCallback,CameraWindowMouseClickCallback,CameraWindowKeyCallback,CameraWindowCursorCallback,CameraWindowMouseWheelCallback,inRefCon,xp.WindowDecorationSelfDecorated,xp.WindowLayerFlightOverlay,CameraWindowRightClickCallback)
    inRefCon.CameraWindowID = xp.createWindowEx(windowInfo)
# Camera window callback
def CameraWindowCallback(inWindowID,inRefCon):
    return 1
# Camera window callback for mouse clicks
def CameraWindowMouseClickCallback(inWindowID,x,y,inMouse,inRefCon):
    if inMouse == 2: # Drag
        inRefCon.CameraMouseStatus['LMB'] = 1
    if inMouse == 3: # Release
        inRefCon.CameraMouseStatus['LMB'] = 0
    return 0
# Camera window callback for keypresses
def CameraWindowKeyCallback(inWindowID,inKey,inFlags,inVirtualKey,inRefCon,losingFocus):
    pass
# Camera window callback for the mouse cursor
def CameraWindowCursorCallback(inWindowID,x,y,inRefCon):
    return xp.CursorDefault
# Camera window callback for the mouse wheel
def CameraWindowMouseWheelCallback(inWindowID,x,y,wheel,clicks,inRefCon):
    inRefCon.CameraMouseStatus['WHL'] = clicks
    return 1
# Camera window callback for the right mouse button
def CameraWindowRightClickCallback(windowID, x, y,inMouse,inRefCon):
    if inMouse == 1: # Down
        inRefCon.CameraMouseStatus['RMB'] = 2
    if inMouse == 2: # Drag
        inRefCon.CameraMouseStatus['RMB'] = 1
    if inMouse == 3: # Release
        inRefCon.CameraMouseStatus['RMB'] = 0
    return 1
