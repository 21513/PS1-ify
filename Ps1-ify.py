import bpy
from bpy.props import EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup, Scene
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "PS1-ify",
    "author": "baeac",
    "version" : (1, 1),
    "blender" : (3, 4, 0),
    "location" : "View3D > PS1",
    "category" : "Import Settings",
    "description" : "Easily import all the settings needed to make your renders look like a PS1 game",
}

# adding a panel
class PS1_PT_panel(Panel):
    bl_idname = 'PS1_PT_panel'
    bl_label = 'PS1-ify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PS1'
 
    def draw(self, context):      
        layout = self.layout
        placeholder = context.scene.placeholder
        layout.operator('ps1.op', text='PS1-ify').action = 'PS1' #it has to be named ps1.op bcs of the _OT_, also no caps
        col = layout.column()
        col.prop(placeholder, "dropdown_box", text="Resolution") #adding the dropdown place for presets

# adding the dropdown with presets
class PS1Properties(PropertyGroup):
    dropdown_box: EnumProperty(
        items=(
            ("PS1_min", "PS1: 256x224", "Min resolution for the PS Link Cable"),
            ("PS1_max", "PS1: 640x480", "Max resolution for the PS Link Cable"),
            ("PS2_max", "PS2: 720x480", "Preset for the PS2"),
            ("PS3_max", "PS3: 1920x1080", "Preset for the PS3"),
        ),
        name="Resolution",
        default="PS1_max",
        description="Presets for game console resolutions",
    )

class PS1_OT_op(Operator):
    bl_idname = 'ps1.op'
    bl_label = 'PS1-ify'
    bl_description = 'PS1'
    bl_options = {'REGISTER', 'UNDO'}
 
    action: EnumProperty(
        items=[
            ('PS1', 'ps1-ify', 'ps1 ify'),
        ]
    )
 
    def execute(self, context):
        if self.action == 'PS1':
            self.ps1_ify(context=context)
        return {'FINISHED'}

    # composite nodetree setup
    @staticmethod
    def ps1_ify(context):
        bpy.context.area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        nodetree = bpy.context.scene.node_tree
        
        # clear default nodes
        for node in nodetree.nodes:
            nodetree.nodes.remove(node)
        
        # adding image
        node1 = nodetree.nodes.new("CompositorNodeRLayers")
        node1.location = (-100,0)

        # adding scale 1
        node2 = nodetree.nodes.new("CompositorNodeScale")
        node2.location = (200,0)
        node2.inputs[1].default_value = 0.500
        node2.inputs[2].default_value = 0.500

        # adding pixelate
        node3 = nodetree.nodes.new("CompositorNodePixelate")
        node3.location = (400,0)
        
        # adding posterize
        node4 = nodetree.nodes.new("CompositorNodePosterize")
        node4.inputs[1].default_value = 256.000
        node4.location = (600,0)

        # adding scale 2
        node5 = nodetree.nodes.new("CompositorNodeScale")
        node5.location = (800,0)
        node5.inputs[1].default_value = 2.000
        node5.inputs[2].default_value = 2.000

        # adding compositor node
        node6 = nodetree.nodes.new("CompositorNodeComposite")
        node6.location = (1000,0)

        # connecting nodes
        nodetree.links.new(node1.outputs["Image"],node2.inputs[0])
        nodetree.links.new(node2.outputs["Image"],node3.inputs[0])
        nodetree.links.new(node3.outputs["Color"],node4.inputs[0])
        nodetree.links.new(node4.outputs["Image"],node5.inputs[0])
        nodetree.links.new(node5.outputs["Image"],node6.inputs[0])
        
        # return to 3d viewport
        bpy.context.area.ui_type = 'VIEW_3D'
        
        # set render settings
        for scene in bpy.data.scenes:
            scene.render.resolution_percentage = 100
            scene.render.use_border = False
            scene.render.filter_size = 0.0
            # eevee settings
            scene.eevee.taa_render_samples = 1
            scene.eevee.taa_samples = 1
            scene.eevee.use_taa_reprojection = False
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 100
            scene.eevee.use_gtao_bounce = False
            scene.eevee.use_bloom = True
            scene.eevee.use_ssr = True
            scene.eevee.use_ssr_refraction = True
            # shadow settings
            scene.eevee.shadow_cascade_size = '64'
            # color management settings
            scene.view_settings.view_transform = 'Standard'
            
            # render settings depending on dropdown selection
            # i have no idea if this is optimized
            # it works so dont touch!!
            if scene.placeholder.dropdown_box == 'PS1_min':
                scene.render.resolution_x = 256
                scene.render.resolution_y = 224
                scene.view_settings.look = 'Very Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS1_max':
                scene.render.resolution_x = 640
                scene.render.resolution_y = 480
                scene.view_settings.look = 'Very Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS2_max':
                scene.render.resolution_x = 720
                scene.render.resolution_y = 480
                scene.eevee.shadow_cascade_size = '128'
                scene.view_settings.look = 'Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS3_max':
                scene.render.resolution_x = 1920
                scene.render.resolution_y = 1080
                scene.render.filter_size = 1.50
                scene.eevee.taa_render_samples = 32
                scene.eevee.taa_samples = 32
                node4.inputs[1].default_value = 512.000 # you can still access the composite nodes here!! cool!!
                scene.eevee.shadow_cascade_size = '512'
                scene.view_settings.look = 'Medium Contrast'
 
def register():
    bpy.utils.register_class(PS1_PT_panel)
    bpy.utils.register_class(PS1Properties)
    bpy.utils.register_class(PS1_OT_op)
    
    Scene.placeholder = PointerProperty(type=PS1Properties)
 
def unregister():
    bpy.utils.unregister_class(PS1_OT_op)
    bpy.utils.unregister_class(PS1Properties)
    bpy.utils.unregister_class(PS1_PT_panel)
    
    del Scene.placeholder
 
 
if __name__ == '__main__':
    register()