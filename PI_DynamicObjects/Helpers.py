#!/usr/bin/python
'''
MODULES
'''
'''
FUNCTIONS
'''
# Handles terminal output
def info_output(instring):
    if Debug == 1:
        print(instring)
# Prints a list vertically
def print_list_vert(inlist):
    for n in range(len(inlist)):
        print(str(inlist[n]))
# Waits for keyboard input
def pause():
    programPause = input("\nPress the <ENTER> key to continue...")
