import bpy
from ps1-ify import ps1_ify

bl_info = {
    "name": "PS1-ify",
    "author": "baeac",
    "version" : (1, 3),
    "blender" : (4, 0, 2),
    "location" : "View3D > PS1",
    "category" : "Import Settings",
    "description" : "Easily import all the settings needed to make your renders look like a PS1 game",
}

def register():
    ps1_ify.register()

def unregister():
    ps1_ify.unregister()
 
if __name__ == "__main__":
    register()
