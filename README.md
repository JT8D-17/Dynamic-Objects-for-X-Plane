# Dynamic Objects for X-Plane


<a name="toc"></a>
## Table of Contents
1. [Goal](#1.0)   
1. [Features](#2.0)   
2.1 [Implemented](#2.1)   
2.2 [Work in Progress](#2.2)   
2.3 [To Do](#2.3)   
2.4 [Under Consideration](#2.4)   
2.5 [Outside of Scope](#2.5)
1. [Requirements](#3.0)
1. [Installation](#4.0)    
1. [Uninstallation](#5.0)   
1. [Usage](#6.0)    
1. [Known Issues](#7.0)
1. [Credits](#8.0)      
1. [License](#9.0)

&nbsp;

<a name="1.0"></a>
## 1 - Goal

"Dynamic Objects for X-Plane" (abbreviated "DynObjXP") is an XPPython3 plugin intended as a spiritual successor for Marginal's [SeaTraffic](https://github.com/Marginal/SeaTraffic) (and its [fork for X-Plane 11.50+](https://github.com/nst0022/SeaTraffic)), without its limitation of predefined objects and without the (in my eyes) unnecessary drawing of objects on X-Plane's map.   
Since routing objects along defined paths works much the same on water, on ground or in the air (except for elevation considerations), "Dynamic Objects for X-Plane" tries to accomodate as many different object types as is feasible for me (except trains).     
For trains and dynamic scenery objects (including trains) in limited areas, use [Living Scenery Technology](https://forums.x-plane.org/index.php?/files/file/82876-living-scenery-technology/) instead.

&nbsp;

[Back to top](#toc)

&nbsp;

<a name="2.0"></a>
## 2 - Features

### 2.1 - Implemented

- Text based route files, as many as desired (and possible for performance reasons).
- Some commmon error checks for input route files.
- Draws any (valid) object defined in route files.
- Supports multiple objects per route and object datarefs.
- Acceleration and deceleration for objects.
- Gradual turns with turn anticipation.  
- Waypoint velocity limits.

### 2.2 Work In Progress

...

### 2.3 To Do

- Banking for aircraft objects
- Pitching for aircraft objects
- 

### 2.4 Under Consideration

- Object offsets
- Better support for cars (continuous terrain probing)

### 2.5 Outside of scope

- Trains (multiple objects on a string) due to offset and terrain probing headaches

&nbsp;

[Back to top](#toc)

&nbsp;

<a name="3.0"></a>
## 3 - Requirements

- X-Plane >11.50 or >12.00
- [XPPython3](https://xppython3.readthedocs.io/en/latest/)
- Pyopengl installed from XPPython3's PIP installer or as a system package

&nbsp;

[Back to top](#toc)

&nbsp;

<a name="4.0"></a>
## 4 - Installation

- Start X-Plane
- Open the Pip Package Installer with _"Plugins --> XPPython3 --> Pip Package Installer"_, enter ```pyopengl```, then click "Install"   
- Copy the _"PI_DynamicObjects"_ folder into _"[X-Plane 11/12 main folder]/Resources/plugins/PythonPlugins"_

&nbsp;

[Back to top](#toc)

&nbsp;


<a name="5.0"></a>
## 5 - Uninstallation

- Delete the _"PI_DynamicObjects"_ folder from _"[X-Plane 11/12 main folder]/Resources/plugins/PythonPlugins"_

&nbsp;

[Back to top](#toc)

&nbsp;


<a name="6.0"></a>
## 6 - Usage

### 6.1 - Route File Format

#### General

- Route files are simple text files, with comma separated values (except for dataref information; see below).
- Each route file name **must be prefixed with "Route_"** (e.g. "Route_MyRoute1.txt") to be read by the route parser. Otherwise it will be ignored.
- In route files, only lines beginning with an ```OBJECT```, ```PERFORMANCE```, ```POINT``` or valid route terminator are parsed. All other lines are interpreted as comments.
- See _"PI_DynamicObjects/Routes/Template.txt"_ for a template with a header containing line format information.

#### OBJECT lines

- ```OBJECT``` lines **must** always be the first elements of a route definition!

&nbsp;

#### PERFORMANCE lines

- A ```PERFORMANCE``` line per object is optional to override the default values. It must always follow an ```OBJECT``` line, otherwise it will be ignored!

&nbsp;

#### POINT lines

- A route must be composed of a minimum of **two** ```POINT``` lines, i.e. two waypoints!   
- The first ```POINT``` line must always follow an ```OBJECT``` line (but may be separated by one or more blank lines between)!


#### Route Termination lines

- A route termination line is optional and governs the object's behavior at the last waypoint.

&nbsp;

### 6.2  - Creating routes

Use something like [GPS Visualizer](https://www.gpsvisualizer.com/draw/) to draw tracks on a map, then export them in a text file.   
Only the point coordinates can be used and will have to be converted into a format suitable for DynObjXP (see above).  
Using the "Find and Replace" function of your text editor should make converting the coordinate blocks from a tracks file quite fast and easy. Use a powerful text editor like [Notepad++](https://notepad-plus-plus.org/), [Notepad2](https://www.flos-freeware.ch/notepad2.html) or [Kate](https://kate-editor.org/de/) for this.   
Make sure to delete the ```,,Length: n km (n mi)``` string from the first coordinate pair as well.  
Add any limitations to the waypoints, then add the OBJECT line and all its required elements


&nbsp;

[Back to top](#toc)

&nbsp;


<a name="7.0"></a>
## 7 - Known Issues

...

&nbsp;

[Back to top](#toc)

&nbsp;


<a name="8.0"></a>
## 8 - Credits

- Laminar Research - Models and Textures in "Ships"
- Various Stackoverflow contributors for code examples (see various code comments)

&nbsp;

[Back to top](#toc)

&nbsp;


<a name="9.0"></a>
## 9 - License

"Dynamic Objects for X-Plane" is licensed under the European Union Public License v1.2 (see _EUPL-1.2-license.txt_). Compatible licenses (e.g. GPLv3) are listed  in the section "Appendix" in the license file.

&nbsp;

[Back to top](#toc)

&nbsp;
