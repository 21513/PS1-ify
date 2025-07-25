import bpy
from bpy.props import EnumProperty, PointerProperty, BoolProperty
from bpy.types import Operator, Panel, PropertyGroup, Scene
from bpy.utils import register_class, unregister_class

class PS1_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PS1"

# Primary panel (no parents)
class PS1_PT_Panel_Main(PS1_Panel_Base, bpy.types.Panel):
    bl_idname = "PS1_PT_panel_main"
    bl_label = "PS1-ify"

    def draw(self, context):
        layout = self.layout
        placeholder = context.scene.placeholder

        layout.operator('ps1.op', text='PS1-ify').action = 'PS1'
        
        col = layout.column()
        col.prop(placeholder, "dropdown_box", text="Presets")
        
        layout.operator('xbox.op', text='Xbox-Ify').action = 'XBOX'
        
        col = layout.column()
        col.prop(placeholder, "dropdown_xbox", text="Presets")
        
        layout.prop(placeholder, "enable_wobble", text="Enable Wobble")

# Subpanel (grouping of child panels, appears only when enable_wobble is True)
class PS1_PT_Panel_Wobble(PS1_Panel_Base, bpy.types.Panel):
    bl_parent_id = "PS1_PT_panel_main"
    bl_label = "Wobble Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        placeholder = context.scene.placeholder
        
        layout.enabled = placeholder.enable_wobble
        layout.prop(placeholder, "speed", text="Speed")
        layout.prop(placeholder, "strength", text="Strength")
        layout.prop(placeholder, "grid_size", text="Grid Size")


# adding the dropdown with presets
class PS1Properties(PropertyGroup):
    dropdown_box: EnumProperty(
        items=(
            ("PS1_min", "PS1: 256x224", "Min resolution for the PS Link Cable"),
            ("PS1_max", "PS1: 640x480", "Max resolution for the PS Link Cable"),
            ("PS2", "PS2: 720x480", "Released March 4th, 2000"),
            ("PSP", "PSP: 480x272", "Released December 12th, 2004"),
            ("PS3", "PS3: 1920x1080", "Released November 11th, 2006"),
            ("PS_Vita", "PS Vita: 960x544", "Released December 17th, 2011"),
            ("PS4", "PS4: 1920x1080", "Released November 10th, 2016"),
            ("PS5", "PS5: 3840x2160", "Released November 12th, 2020"),
        ),
        name="Presets",
        default="PS1_max",
        description="Presets for game console resolutions",
    )

    dropdown_xbox: EnumProperty(
        items=(
            ("Xbox", "Xbox: 640x480", "Released November 15th, 2001"),
            ("Xbox_360", "Xbox 360: 1280x720", "Released November 22nd, 2005"),
            ("Xbox_One", "Xbox One: 1920x1080", "Released November 22nd, 2013"),
            ("Xbox_Series_S", "Xbox Series S: 3840x2160", "Released November 10th, 2020"),
            ("Xbox_Series_X", "Xbox Series X: 3840x2160", "Released November 10th, 2020"),
        ),
        name="Presets2",
        default="Xbox",
        description="Presets for game console resolutions",
    )
    
    def update_wobble(self, context):
        if not self.enable_wobble:
            # Remove the "Wobble" modifiers from all mesh objects
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES' and modifier.node_group:
                            if modifier.node_group.name == "Wobble":
                                obj.modifiers.remove(modifier)
        elif self.enable_wobble:
            # Execute the wobble setup function
            bpy.ops.wobble.op('INVOKE_DEFAULT', action='WOBBLE')

    enable_wobble: bpy.props.BoolProperty(
        name="Enable Wobble",
        default=False,
        description="Enable Wobble",
        update=update_wobble
    )
    
    def update_wobble_settings(self, context):
        if self.enable_wobble:
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES' and modifier.node_group:
                            if modifier.node_group.name == "Wobble":
                                # Update the values in the wobble node group
                                for node in modifier.node_group.nodes:
                                    if node.type == 'VALUE':
                                        if node.name == "Speed":
                                            node.outputs[0].default_value = self.speed
                                        elif node.name == "Strength":
                                            node.outputs[0].default_value = self.strength
                                        elif node.name == "Grid Size":
                                            node.outputs[0].default_value = self.grid_size
        
    
    speed: bpy.props.FloatProperty(
        name="Speed",
        default=2.0,
        min=0.1,
        max=10.0,
        update=update_wobble_settings
    )
    
    strength: bpy.props.FloatProperty(
        name="Strength",
        default=0.2,
        min=0.0,
        max=10.0,
        update=update_wobble_settings
    )
    
    grid_size: bpy.props.FloatProperty(
        name="Grid Size",
        default=0.1,
        min=0.01,
        max=1.0,
        update=update_wobble_settings
    )
    
class WOBBLE_OT_op(Operator):
    bl_idname = 'wobble.op'
    bl_label = 'Use Wobble'
    bl_description = 'Enable vertex snapping'
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=[
            ('WOBBLE', 'wobble', 'wobble'),
        ]
    )

    def execute(self, context):
        self.wobble(context=context)
        return {'FINISHED'}

    # geometry nodetree setup
    @staticmethod
    def wobble(context):
        geonodetree = None

        if bpy.context.scene.placeholder.enable_wobble:
            all_node_groups = bpy.data.node_groups

            # Check if any node group is a Geometry Nodes tree named "Wobble"
            for node_group in all_node_groups:
                if node_group.bl_idname == 'GeometryNodeTree' and node_group.name == "Wobble":
                    geonodetree = node_group
                    break
            else:
                # Add the modifier only if "Wobble" node group doesn't exist
                bpy.ops.object.modifier_add(type='NODES')
                bpy.context.area.ui_type = 'GeometryNodeTree'
                bpy.ops.node.new_geometry_node_group_assign()

                geonodetree = bpy.context.object.modifiers[-1].node_group
                geonodetree.name = "Wobble"

                for node in geonodetree.nodes:
                    geonodetree.nodes.remove(node)
                    
                geonode0 = geonodetree.nodes.new(type='ShaderNodeMath')
                geonode0.location = (-400, 0)
                
                geonode0.operation = 'MULTIPLY'
                geonode0.inputs[1].default_value = 1.000
                
                driver = geonode0.inputs[0].driver_add("default_value")
                driver.driver.expression = 'frame/10'

                geonode1 = geonodetree.nodes.new(type='ShaderNodeTexNoise')
                geonode1.location = (-200, 0)
                geonode1.noise_dimensions = '4D'

                geonode1.inputs[2].default_value = 0.100
                geonode1.inputs[3].default_value = 15.000
                geonode1.inputs[4].default_value = 0.000

                geonode2 = geonodetree.nodes.new(type='ShaderNodeMath')
                geonode2.location = (0, 0)

                geonode2.operation = 'MULTIPLY'
                geonode2.inputs[1].default_value = 0.010
                
                geonode3 = geonodetree.nodes.new(type='ShaderNodeMath')
                geonode3.location = (200, 0)
                
                geonode3.operation = 'SNAP'
                geonode3.inputs[1].default_value = 0.02
                
                geonode4 = geonodetree.nodes.new(type='ShaderNodeVectorMath')
                geonode4.location = (400, 0)
                
                geonode4.operation = 'SUBTRACT'
                
                geonode5 = geonodetree.nodes.new(type='ShaderNodeMath')
                geonode5.location = (0, -175)
                geonode5.operation = 'MULTIPLY'
                
                geonode5.inputs[0].default_value = 0.5

                geonode6 = geonodetree.nodes.new(type='GeometryNodeSetPosition')
                geonode6.location = (600, 150)

                geonode7 = geonodetree.nodes.new(type='NodeGroupOutput')
                geonode7.location = (800, 150)

                geonode8 = geonodetree.nodes.new(type='NodeGroupInput')
                geonode8.location = (-600, 150)
                
                speed = geonodetree.nodes.new(type='ShaderNodeValue')
                speed.name = "Speed"
                speed.location = (-600, 50)
                
                speed.outputs[0].default_value = context.scene.placeholder.speed
                
                strength = geonodetree.nodes.new(type='ShaderNodeValue')
                strength.name = "Strength"
                strength.location = (-600, -50)
                
                strength.outputs[0].default_value = context.scene.placeholder.strength
                
                grid_size = geonodetree.nodes.new(type='ShaderNodeValue')
                grid_size.name = "Grid Size"
                grid_size.location = (-600, -150)
                
                grid_size.outputs[0].default_value = context.scene.placeholder.grid_size

                # connecting nodes
                geonodetree.links.new(geonode0.outputs[0], geonode1.inputs[1])
                geonodetree.links.new(geonode1.outputs[0], geonode2.inputs[0])
                geonodetree.links.new(geonode2.outputs[0], geonode3.inputs[0])
                geonodetree.links.new(geonode3.outputs[0], geonode4.inputs[0])
                geonodetree.links.new(geonode4.outputs[0], geonode6.inputs[3])
                geonodetree.links.new(geonode5.outputs[0], geonode4.inputs[1])
                geonodetree.links.new(geonode6.outputs[0], geonode7.inputs[0])
                geonodetree.links.new(geonode8.outputs[0], geonode6.inputs[0])
                
                geonodetree.links.new(speed.outputs[0], geonode0.inputs[1])
                geonodetree.links.new(strength.outputs[0], geonode2.inputs[1])
                geonodetree.links.new(strength.outputs[0], geonode5.inputs[0])
                geonodetree.links.new(grid_size.outputs[0], geonode3.inputs[1])
                
                bpy.context.area.ui_type = 'VIEW_3D'

            # Add the modifier to objects that don't have it and set default values
            for obj in bpy.data.objects:
                if obj.type == 'MESH' and not any(mod.type == 'NODES' and mod.node_group.name == "Wobble" for mod in obj.modifiers):
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_add(type='NODES')
                    
                    if geonodetree:
                        obj.modifiers[-1].node_group = geonodetree
                    else:
                        print("Error: 'Wobble' node group not found.")

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
        bpy.context.space_data.shading.use_compositor = 'ALWAYS'
        bpy.context.area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
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
            # scene.eevee.use_gtao_bounce = False
            scene.eevee.use_bloom = True
            scene.eevee.use_ssr = True
            scene.eevee.use_ssr_refraction = True
            # shadow settings
            scene.eevee.shadow_cascade_size = '128'
            # color management settings
            scene.view_settings.view_transform = 'Standard'
            
            # render settings depending on dropdown selection
            # i have no idea if this is optimized
            # it works so dont touch!!
            if scene.placeholder.dropdown_box == 'PS1_min':
                scene.render.resolution_x = 256
                scene.render.resolution_y = 224
                node4.inputs[1].default_value = 32.000
                scene.view_settings.look = 'Very Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS1_max':
                scene.render.resolution_x = 640
                scene.render.resolution_y = 480
                node4.inputs[1].default_value = 32.000
                scene.view_settings.look = 'Very Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS2':
                scene.render.resolution_x = 720
                scene.render.resolution_y = 480
                node4.inputs[1].default_value = 256.000
                scene.eevee.shadow_cascade_size = '128'
                scene.view_settings.look = 'Low Contrast'
            elif scene.placeholder.dropdown_box == 'PSP':
                scene.render.resolution_x = 480
                scene.render.resolution_y = 272
                node4.inputs[1].default_value = 64
                scene.view_settings.look = 'Low Contrast'
            elif scene.placeholder.dropdown_box == 'PS_Vita':
                scene.render.resolution_x = 960
                scene.render.resolution_y = 544
                node4.inputs[1].default_value = 64
                scene.view_settings.look = 'Medium Contrast'
            elif scene.placeholder.dropdown_box == 'PS3':
                scene.render.resolution_x = 1920
                scene.render.resolution_y = 1080
                scene.render.filter_size = 1.50
                scene.eevee.taa_render_samples = 64
                scene.eevee.taa_samples = 64
                node4.inputs[1].default_value = 512.000 # you can still access the composite nodes here!! cool!!
                scene.eevee.shadow_cascade_size = '512'
                scene.view_settings.look = 'Medium Contrast'
            elif scene.placeholder.dropdown_box == 'PS4':
                scene.render.resolution_x = 1920
                scene.render.resolution_y = 1080
                scene.render.filter_size = 1.50
                scene.eevee.taa_render_samples = 128
                scene.eevee.taa_samples = 128
                node4.inputs[1].default_value = 1024.000
                node2.mute = True
                node3.mute = True
                node5.mute = True
                scene.eevee.shadow_cascade_size = '1024'
                scene.view_settings.look = 'Medium High Contrast'
                scene.view_settings.view_transform = 'AgX'
            elif scene.placeholder.dropdown_box == 'PS5':
                scene.render.resolution_x = 3840
                scene.render.resolution_y = 2160
                scene.render.filter_size = 2
                node4.inputs[1].default_value = 1024.000
                
                scene.render.engine = 'CYCLES'
                scene.cycles.device = 'GPU'
                scene.cycles.use_preview_denoising = True
                scene.cycles.use_denoising = True
                scene.cycles.preview_samples = 256
                scene.cycles.samples = 256
                
                node2.mute = True
                node3.mute = True
                node4.mute = True
                node5.mute = True
                scene.eevee.shadow_cascade_size = '1024'
                scene.view_settings.look = 'Medium High Contrast'
                scene.view_settings.view_transform = 'AgX'

class XBOX_OT_op(Operator):
    bl_idname = 'xbox.op'
    bl_label = 'XBOX-ify'
    bl_description = 'XBOX'
    bl_options = {'REGISTER', 'UNDO'}
 
    action: EnumProperty(
        items=[
            ('XBOX', 'xbox-ify', 'xbox ify'),
        ]
    )
 
    def execute(self, context):
        if self.action == 'XBOX':
            self.xbox_ify(context=context)
        return {'FINISHED'}

    # composite nodetree setup
    @staticmethod
    def xbox_ify(context):
        bpy.context.space_data.shading.use_compositor = 'ALWAYS'
        bpy.context.area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
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
            # scene.eevee.use_gtao_bounce = False
            scene.eevee.use_bloom = True
            scene.eevee.use_ssr = True
            scene.eevee.use_ssr_refraction = True
            # shadow settings
            scene.eevee.shadow_cascade_size = '128'
            # color management settings
            scene.view_settings.view_transform = 'Standard'
            
            if scene.placeholder.dropdown_xbox == 'Xbox':
                scene.render.resolution_x = 640
                scene.render.resolution_y = 480
                node4.inputs[1].default_value = 32.000
                scene.view_settings.look = 'Very Low Contrast'
            elif scene.placeholder.dropdown_xbox == 'Xbox_360':
                scene.render.resolution_x = 1280
                scene.render.resolution_y = 720
                node4.inputs[1].default_value = 128
                scene.view_settings.look = 'Low Contrast'
            elif scene.placeholder.dropdown_xbox == 'Xbox_One':
                scene.render.resolution_x = 1920
                scene.render.resolution_y = 1080
                node4.inputs[1].default_value = 256
                
                scene.view_settings.view_transform = 'AgX'
                scene.view_settings.look = 'AgX - Medium Low Contrast'
            elif scene.placeholder.dropdown_xbox == 'Xbox_Series_S':
                scene.render.resolution_x = 1920
                scene.render.resolution_y = 1080
                scene.render.engine = 'CYCLES'
                scene.cycles.device = 'GPU'
                scene.cycles.preview_samples = 64
                scene.cycles.samples = 128
                scene.cycles.use_preview_denoising = True
                scene.cycles.use_denoising = True
                
                node2.mute = True
                node3.mute = True
                node4.mute = True
                node5.mute = True
                
                scene.view_settings.view_transform = 'AgX'
                scene.view_settings.look = 'AgX - Medium High Contrast'
            elif scene.placeholder.dropdown_xbox == 'Xbox_Series_X':
                scene.render.resolution_x = 3840
                scene.render.resolution_y = 2160
                scene.render.engine = 'CYCLES'
                scene.cycles.device = 'GPU'
                scene.cycles.preview_samples = 256
                scene.cycles.samples = 256
                scene.cycles.use_preview_denoising = True
                scene.cycles.use_denoising = True
  
                node2.mute = True
                node3.mute = True
                node4.mute = True
                node5.mute = True
                
                scene.view_settings.view_transform = 'AgX'
                scene.view_settings.look = 'AgX - Punchy'

 
def register():
    bpy.utils.register_class(PS1_PT_Panel_Main)
    bpy.utils.register_class(PS1_PT_Panel_Wobble)
    bpy.utils.register_class(PS1Properties)
    bpy.utils.register_class(WOBBLE_OT_op)
    bpy.utils.register_class(PS1_OT_op)
    bpy.utils.register_class(XBOX_OT_op)
    
    Scene.placeholder = PointerProperty(type=PS1Properties)
 
def unregister():
    bpy.utils.unregister_class(XBOX_OT_op)
    bpy.utils.unregister_class(PS1_OT_op)
    bpy.utils.unregister_class(WOBBLE_OT_op)
    bpy.utils.unregister_class(PS1Properties)
    bpy.utils.unregister_class(PS1_PT_Panel_Wobble)
    bpy.utils.unregister_class(PS1_PT_Panel_Main)
    
    del Scene.placeholder
 
 
if __name__ == '__main__':
    register()
