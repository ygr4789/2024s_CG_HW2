
## Requirements
This is a programming assignmet for **SNU Computer Graphics (4190.410)**.
This code uses [Pyglet](https://github.com/pyglet/pyglet) which is a cross-platform windowing library under Python 3.8+. 
Supported platforms are:

* Windows 7 or later
* Mac OS X 10.3 or later
* Linux, with the following libraries (most recent distributions will have these in a default installation):

This program has been implemented and tested in the Ubuntu 20.04 environment.

## Installation
Pyglet is installable from PyPI:

    pip install --upgrade --user pyglet

You can run the code easily by:

    python3 main.py
    
If necessary, install packages by:

    pip install -r requirements.txt
    
## Instruction
### Common
- Camera Controls
    - Left-Click + Drag : Rotate camera direction
    - Right-Click + Drag : Translate camera position
    - Scroll Up/Down : Camera zoom-in/out
- Control Points
    - Select and move control points with mouse
- Reset
    - Set control points to initial state
- Export
    - Save mesh as ```*.obj``` format file
- Color Edit
    - Change mesh color with color picker
- Wireframe
    - Draw edges with constant color
- Grid Helper
### Curve Mode
- Type
    - Choose between Bezier and B-Spline
- Steps
    - Determine width/height of surface's grid
### Subdiv Mode
- Import
    - Load ```*.obj``` format file
- Steps
    - Iterate subdivision with Catmull-Clark algorithm