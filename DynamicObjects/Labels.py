#!/usr/bin/python
'''

Drawing 2D lebels in the 3D world

Original by Laminar Research, updated by Birger Hoppe
Python port by Peter Buckner

Source:
https://github.com/TwinFan/XPMP2/blob/5d990be4401698ef88fc1b10dbab7f7040c54ff8/src/2D.cpp

/// @copyright  Permission is hereby granted, free of charge, to any person obtaining a
///             copy of this software and associated documentation files (the "Software"),
///             to deal in the Software without restriction, including without limitation
///             the rights to use, copy, modify, merge, publish, distribute, sublicense,
///             and/or sell copies of the Software, and to permit persons to whom the
///             Software is furnished to do so, subject to the following conditions:\n
///             The above copyright notice and this permission notice shall be included in
///             all copies or substantial portions of the Software.\n
///             THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
///             IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
///             FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
///             AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
///             LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
///             OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
///             THE SOFTWARE.

and


'''
'''
MODULES
'''
import xp
from math import sqrt
from .Movement import Labels_Objects,Labels_Waypoint_1,Labels_Waypoint_2
# from PI_DynamicObjects import Draw_Labels
'''
VARIABLES
'''
# XP dataref declarators
DR_World_Matrix = None
DR_Proj_Matrix = None
DR_Screen_Width = None
DR_Screen_Height = None
DR_Visibility = None
DR_Field_Of_View = None

# World and Projection matrices
GL_World_Matrix = [None, ] * 16
GL_Proj_Matrix = [None, ] * 16

# Helpers
Screen_Width = None
Screen_Height = None
Visibility = None
MaxLabelDist = None
Label_Switch = 0
# Font information
Font = xp.Font_Basic
Font_W,Font_H,digitsOnly = xp.getFontDimensions(Font)
'''
FUNCTIONS
'''
# 4x4 matrix transform of an XYZW coordinate - this matches OpenGL matrix conventions.
def mult_matrix_vec(dst, m, v):
    dst[0] = v[0] * m[0] + v[1] * m[4] + v[2] * m[8] + v[3] * m[12]
    dst[1] = v[0] * m[1] + v[1] * m[5] + v[2] * m[9] + v[3] * m[13]
    dst[2] = v[0] * m[2] + v[1] * m[6] + v[2] * m[10] + v[3] * m[14]
    dst[3] = v[0] * m[3] + v[1] * m[7] + v[2] * m[11] + v[3] * m[15]

# Read world and projection matrices from X-Plane
def Read_Datarefs():
        global Screen_Width, Screen_Height, Visibility
        # Read the model view and projection matrices from this frame
        xp.getDatavf(DR_World_Matrix, GL_World_Matrix, 0, 16)
        xp.getDatavf(DR_Proj_Matrix, GL_Proj_Matrix, 0, 16)

        # Read screen size for when use changes the XP window size
        Screen_Width = xp.getDatai(DR_Screen_Width)
        Screen_Height = xp.getDatai(DR_Screen_Height)

        # Read visibility
        Visibility = xp.getDataf(DR_Visibility)

        # Read field of view
        Field_Of_View = xp.getDataf(DR_Field_Of_View)

# This converts 3D OpenGL coordinates to 2D screen coordinates

def Convert3Dto2D(in_array):
    # Object x,y,z is provided as an array
    # Eyepoint coordinates
    acf_eye = [None, ] * 4
    # Normalized device coordinates for transformation by the rasterizer
    acf_ndc = [None, ] * 4

    # OpenGL matrix conversion into screen coordinates
    mult_matrix_vec(acf_eye, GL_World_Matrix,in_array)
    mult_matrix_vec(acf_ndc, GL_Proj_Matrix, acf_eye)

    acf_ndc[3] = 1.0 / acf_ndc[3]
    acf_ndc[0] *= acf_ndc[3]
    acf_ndc[1] *= acf_ndc[3]
    acf_ndc[2] *= acf_ndc[3]

    out_x = int(Screen_Width * (acf_ndc[0] * 0.5 + 0.5))
    out_y = int(Screen_Height * (acf_ndc[1] * 0.5 + 0.5))

    # Check the Z value to avoid drawing labels when not facing an object. Vulkan NDC is [0;1], OpenGL [-1,1]
    if acf_ndc[2] > 0 and acf_ndc[2] < 1:
        visible = 1
    else:
        visible = 0

    return out_x,out_y,visible

# Gets the distance between two points
def Dist_OGL(in_array1,in_array2):
    dist = sqrt(((in_array1[0] - in_array2[0])**2)+((in_array1[1] - in_array2[1])**2)+((in_array1[2] - in_array2[2])**2))
    return dist




# Draw the labels on objects
def Labels2DDraw(label_array):
    # Read datarefs
    Read_Datarefs()
    # Read the camera position and visibility
    Camera_Pos = xp.readCameraPosition()
    MaxLabelDist = 5000 # 500 km
    # Check if visibility is below maximum permitted
    if xp.getDataf(DR_Visibility) < MaxLabelDist:
        MaxLabelDist = xp.getDataf(DR_Visibility)
    # Account for camera zoom
    MaxLabelDist = MaxLabelDist * Camera_Pos[6]
    # Loop through table of labels
    for n in range(len(label_array)):
        # Account for object distance to user
        if Dist_OGL(label_array[n][1],Camera_Pos) < MaxLabelDist:
            # Vertical label offset
            if label_array[n][0] == "Object":
                Offset_Z = 25
            else:
                Offset_Z = 0
            # Build input array for 2D screen space conversion
            Use_Label = [label_array[n][1][0],label_array[n][1][1]+Offset_Z,label_array[n][1][2],1.0]
            # Transform the object's 3D OpenGL coordinates to 2D screen coordinates and check if the label shall be visible
            Label_x,Label_y,Is_Visible = -1, -1,0
            Label_x,Label_y,Is_Visible = Convert3Dto2D(Use_Label)
            # Only draw labels when they're supposed to be visible.
            if Is_Visible == 1:
                # Measure string length to size up the dark box
                Str_Len = xp.measureString(Font,str(label_array[n][2]))
                # Draw a dark box for better contrast
                xp.drawTranslucentDarkBox(int(Label_x - 5),int(Label_y + Font_H),int(Label_x + Str_Len),int(Label_y - (Font_H * 0.5)))
                if label_array[n][0] == "Object":
                    # Implement label colors later
                    Label_Color = [1.0, ] * 3
                else:
                    Label_Color = [207,0,249] # Violet for waypoints
                # Draw the label
                xp.drawString(Label_Color, Label_x, Label_y,str(label_array[n][2]),None, Font)
'''

INITIALIZATION

'''
def Init_Labels():
        global DR_World_Matrix, DR_Proj_Matrix, DR_Screen_Width, DR_Screen_Height, DR_Field_Of_View, DR_Visibility
        # These datarefs are valid to read from a 2-d drawing callback and describe the state
        # of the underlying 3-d drawing environment the 2-d drawing is layered on top of.
        DR_World_Matrix = xp.findDataRef("sim/graphics/view/world_matrix")
        DR_Proj_Matrix = xp.findDataRef("sim/graphics/view/projection_matrix_3d")

        # This describes the size of the current monitor at the time we draw.
        DR_Screen_Width = xp.findDataRef("sim/graphics/view/window_width")
        DR_Screen_Height = xp.findDataRef("sim/graphics/view/window_height")

        # Get current visbility
        DR_Visibility = xp.findDataRef("sim/graphics/view/visibility_effective_m")

        # Get field of view
        DR_Field_Of_View = xp.findDataRef("sim/graphics/view/field_of_view_deg")


def Init_Label_Callback(inRefcon):
    xp.registerDrawCallback(LabelDrawCallback,xp.Phase_Window,1,inRefcon)

def Uninit_Label_Callback(inRefcon):
    xp.unregisterDrawCallback(LabelDrawCallback,xp.Phase_Window,1,inRefcon)

'''

CALLBACKS

'''
def LabelDrawCallback(inPhase,inIsBefore,inRefcon):
    global Label_Switch
    if Label_Switch != inRefcon.Draw_Labels:
        print("DynObjXP: Changing label state to "+str(inRefcon.Draw_Labels))
    Label_Switch = inRefcon.Draw_Labels
    if Label_Switch == 1:
        # Call the label draw function, order matters!
        Labels2DDraw(Labels_Waypoint_1)
        Labels2DDraw(Labels_Waypoint_2)
        Labels2DDraw(Labels_Objects)


    return 1
