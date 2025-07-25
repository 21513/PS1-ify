import bpy
from ps1_ify import ps1_ify

bl_info = {
    "name": "PS1-ify",
    "author": "baeac",
    "version" : (1, 5, 0),
    "blender" : (4, 5, 0),
    "location" : "View3D > PS1",
    "category" : "Import Settings",
    "description" : "Easily import all the settings needed to make your renders look like a PS1 game.",
}

def register():
    ps1_ify.register()

def unregister():
    ps1_ify.unregister()
 
if __name__ == "__main__":
    register()
