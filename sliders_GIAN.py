import bpy
from mathutils import Vector

"""
FUNCTIONS
"""

def rectangle_vert_widget(bname, width, height, offset, fill):

    # Create mesh and object
    mesh = bpy.data.meshes.new(f'{bname}_WGT')
    obj = bpy.data.objects.new(f'{bname}_WGT', object_data=mesh)
    
    col = ''
    
    if bpy.data.collections.get('sliders_custom_WGTS'):
        col = bpy.data.collections.get('sliders_custom_WGTS')
    else:
        col = bpy.data.collections.new('sliders_custom_WGTS')
        bpy.context.scene.collection.children.link(col)
    
    col.objects.link(obj)
    col.hide_viewport = True
    
    verts = []
    
    altezza = height/2
    larghezza = width/2
    
    lower_offset = width/4 if offset != 0 else 0
    upper_offset = width if offset != 0 else 0
    
    verts = [
        Vector((-larghezza, 0, -altezza + height/2 - lower_offset)), #in basso a sinistra
        Vector(( larghezza, 0, -altezza + height/2 - lower_offset)), #in basso a destra
        Vector(( larghezza,  0, altezza + height/2 + upper_offset)), #in alto a sinistra
        Vector((-larghezza,  0, altezza + height/2 + upper_offset)), #in alto a destra
    ]
    
    # Define edges (connect in a loop)
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
    ]
    
    faces = []
    
    if fill:
        faces=[(0,1,2,3)]

    # Create mesh data
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    
    return obj

def rectangle_oriz_widget(bname, width, height, offset):

    pass

def rectangle_slider(obj, name, scale, up=True, cursor=False):
    
    if not obj:
        return False
       
    arm = obj.data
    
    cursor_loc = (0,0,0)
    
    master_dim = ''
    
    #Get cursor  location
    if cursor:
        cursor_loc = bpy.context.scene.cursor.location 

    bpy.ops.object.mode_set(mode='EDIT')
    
    element_list = []
    
    for element in ['master', 'control']:
        new_bone = arm.edit_bones.new(f'{element}_{name}')
        
        new_bone.head = cursor_loc
        new_bone.tail = cursor_loc
        
        element_list.append(new_bone)
    
    if not element_list:
        return False

    master, control = element_list
    
    if up:
        setattr(master.tail, 'z', getattr(master.head, 'z') + scale)
        setattr(control.tail, 'z', getattr(master.head, 'z') + scale/4)
    else:
        setattr(master.tail, 'x', getattr(master.head, 'x') + scale)
        setattr(control.tail, 'x', getattr(master.head, 'x') + scale/4)
    
    control.parent = master
    
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_list = []
    
    for element in ['master', 'control']:
        new_pose = obj.pose.bones.get(f'{element}_{name}')
        new_pose.rigify_type = 'basic.raw_copy'
        
        pose_list.append(new_pose)
    
    if not pose_list:
        return False
    
    master_pose, control_pose = pose_list
    
    master_pose.rigify_parameters.optional_widget_type = 'circle'
    control_pose.rigify_parameters.optional_widget_type = 'circle'
    
    element_collections = []
    
    for element in ['master', 'control']:
        
        if not arm.collections_all.get(f'Slider {element.title()}'):
            bone_col = arm.collections.new(f'Slider {element.title()}')
            element_collections.append(bone_col)
    
    if element_collections:
        master_col, slider_col = element_collections
        
        master_col.assign(master_pose)
        slider_col.assign(control_pose)
    
    #Setup Limit Distance Constraint
    limit_location = control_pose.constraints.new('LIMIT_LOCATION')
    limit_location.name = f'Limit Location - {control_pose.name}'
        
    limit_location.use_min_x = True
    limit_location.use_min_y = True
    limit_location.use_min_z = True
    
    limit_location.min_x = 0
    limit_location.min_y = 0
    limit_location.min_z = 0
    
    limit_location.use_max_x = True
    limit_location.use_max_y = True
    limit_location.use_max_z = True
    
    limit_location.max_x = 0
    limit_location.max_y = scale
    limit_location.max_z = 0
    
    limit_location.use_transform_limit = True
    limit_location.owner_space = 'LOCAL'
    
    #GET DIMENSIONS
    master_dim = master_pose.length
    control_dim = control_pose.length
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    master_widget = ''
    control_widget = ''
    
    if up:
        master_widget = rectangle_vert_widget(f'master_{name}', control_dim, master_dim, scale, False)
        control_widget = rectangle_vert_widget(f'control_{name}', control_dim, control_dim/4, 0, True)
        
        bpy.ops.object.mode_set(mode='POSE')
    
        pose_list = []
        
        for element in ['master', 'control']:
            new_pose = obj.pose.bones.get(f'{element}_{name}')
            new_pose.rigify_type = 'basic.raw_copy'
            
            pose_list.append(new_pose)
        
        if not pose_list:
            return False
        
        master_pose, control_pose = pose_list
        
        master_pose.custom_shape = master_widget
        control_pose.custom_shape = control_widget
        
        master_pose.use_custom_shape_bone_size = False
        control_pose.use_custom_shape_bone_size = False
        
        master_pose.custom_shape_rotation_euler[0] = -90
        control_pose.custom_shape_rotation_euler[0] = -90
    else:
        pass
        
    return True

def circle_slider(obj, name, scale, cursor=False):
    
    if not obj:
        return False
       
    arm = obj.data
    
    cursor_loc = (0,0,0)
    
    #Get cursor  location
    if cursor:
        cursor_loc = bpy.context.scene.cursor.location 

    bpy.ops.object.mode_set(mode='EDIT')
    
    element_list = []
    
    for element in ['master', 'control', 'distance']:
        new_bone = arm.edit_bones.new(f'{element}_{name}')
        
        new_bone.head = cursor_loc
        new_bone.tail = cursor_loc
        
        element_list.append(new_bone)
    
    if not element_list:
        return False

    master, control, distance = element_list
    
    setattr(master.tail, 'y', getattr(master.head, 'y') - scale)
    setattr(control.tail, 'y', getattr(master.head, 'y') - scale/4)
    setattr(distance.tail, 'x', getattr(master.head, 'x') + scale/2)
    
    control.parent = master
    distance.parent = master
    
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_list = []
    
    for element in ['master', 'control', 'distance']:
        new_pose = obj.pose.bones.get(f'{element}_{name}')
        new_pose.rigify_type = 'basic.raw_copy'
        
        pose_list.append(new_pose)
    
    if not pose_list:
        return False
    
    master_pose, control_pose, distance_pose = pose_list
    
    master_pose.rigify_parameters.optional_widget_type = 'circle'
    control_pose.rigify_parameters.optional_widget_type = 'circle'
    
    element_collections = []
    
    for element in ['master', 'control', 'distance']:
        
        if not arm.collections_all.get(f'Slider {element.title()}'):
            bone_col = arm.collections.new(f'Slider {element.title()}')
            element_collections.append(bone_col)
    
    if element_collections:
        master_col, slider_col, distance_col = element_collections
        
        master_col.assign(master_pose)
        slider_col.assign(control_pose)
        distance_col.assign(distance_pose)
    
    #Setup Limit Distance Constraint
    limit_distance = control_pose.constraints.new('LIMIT_DISTANCE')
    limit_distance.name = f'Limit Distance - {control_pose.name}'
    
    limit_distance.target = obj
    limit_distance.subtarget = distance_pose.name
    
    limit_distance.distance = 0.35 *scale
    limit_distance.use_transform_limit = True
    
    limit_distance.target_space = 'LOCAL'
    limit_distance.owner_space = 'LOCAL' 
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return True

"""
PANELS
"""

class SLIDER_RIG_PANEL(bpy.types.Panel):
    bl_label = "Slider Rig v. "
    bl_idname = "RIGGING_PT_SliderRig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GIAN"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        winman = context.window_manager
        
        
        box = layout.box()
        
        row = box.row(align=True)
        row.prop(winman, 'slider_type', text='')
        
        row = box.row(align=True)
        row.prop(winman, 'slider_name', text='', icon='ITALIC', placeholder='Slider Name')
        
        row = box.row()
        
        col_01 = row.column(align=True)
        col_01.prop(winman, 'slider_scale', text='Scale')
        
        col_02 = row.column(align=True)
        col_02.prop(winman, 'slider_cursor', text='To Cursor', expand=True)
        
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("sl.addcircleslider", text='Circle Slider')
        
        
"""
OPERATORS
"""

class SL_Add_Circle_Slider_OPS(bpy.types.Operator):
    """Add circle slider in selected metarig"""
    bl_idname = "sl.addcircleslider"
    bl_label = "Add circle slider in selected metarig"

    def execute(self, context):
        
        winman = context.window_manager
        
        boneType = winman.slider_type
        
        boneName = winman.slider_name
        boneScale = winman.slider_scale
        boneCursor = winman.slider_cursor
        
        ob = context.object
        
        if ob and ob.type == 'ARMATURE':
            
            check = False
            
            if boneType == 'circle':
                check = circle_slider(ob, boneName, boneScale, boneCursor)
            elif boneType == 'rectangle_vert': 
                pass
            elif boneType == 'rectangle_horiz':
                pass
            else:
                check = False
            
            #REPORT MESSAGE AFTER OPERATOR
            if check:    
                self.report(type={'INFO'}, message='Slider Created!')
            else:
                self.report(type={'ERROR'}, message="Something didn't work!")
               
        else:
            self.report(type={'ERROR'}, message="Something didn't work!")
    
        return {'FINISHED'}

"""
REGISTER & UNREGISTER
"""

def register():
    
    #PANELS
    bpy.utils.register_class(SLIDER_RIG_PANEL)
    
    #OPERATORS
    bpy.utils.register_class(SL_Add_Circle_Slider_OPS)
    
    #PROPERTY
    bpy.types.WindowManager.slider_name = bpy.props.StringProperty(name='Slider Name')
    bpy.types.WindowManager.slider_scale = bpy.props.FloatProperty(name='Slider Scale', default=1.0, min=0.1, max=100.0)
    bpy.types.WindowManager.slider_cursor = bpy.props.BoolProperty(name='Slider Cursor', default=False)
    bpy.types.WindowManager.slider_type = bpy.props.EnumProperty(name='Slider Type', default='circle', items={('circle', 'Circle', ''), ('rectangle_vert', 'Rectangle Vertical', ''), ('rectangle_horiz', 'Rectangle horizontal', '')})
    
def unregister():
    
    #PANELS
    bpy.utils.unregister_class(SLIDER_RIG_PANEL)
    
    #OPERATORS
    bpy.utils.unregister_class(SL_Add_Circle_Slider_OPS)
    
    #PROPERTY
    del bpy.types.WindowManager.slider_name
    del bpy.types.WindowManager.slider_scale
    del bpy.types.WindowManager.slider_cursor
    del bpy.types.WindowManager.slider_type

if __name__ == "__main__":
    register()