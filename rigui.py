import bpy

from bpy.utils import register_class, unregister_class
from dataclasses import dataclass

classes = []#this is for registering classes add the bl idname of new classes to this when you make them.



class Rig_UI_Mia(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_label = "Rig UI"
    bl_idname = "Rig_UI_Mia"

    @classmethod
    def poll(self, context):
        try:
            return (context.active_object.data.get("rig_id") == "MIA")
        except (AttributeError, KeyError, TypeError):
            return False
        
    @dataclass
    class Button_Props:
        """ 
            Button Properties per row 
            Importatntly amount can either be Single or Multi
        """
        names:list
        size:float = 1.0
        amount:str = "single"
        def __init__(self, names:list[str], size:list[float] = None, amount:str = "Multi") -> None:
            self.names = names
            self.size = size
            if size == None:
                self.size = [1.0 for i in names]            
            if len(self.names) == 1:
                amount = "Single"
            self.amount = amount
            

    def draw(self, context):
        #Layer Manager
        cntx_actv_obj = context.active_object.data
        bone_colctns = cntx_actv_obj.collections
        layout = self.layout
        col = layout.column()

        def __single(name:list[str], size:list[float]) -> None:
                row = col.row(align=True)
                slot = row.row(align=True)
                button = slot.row(align=True)
                button.prop(bone_colctns[name[0]], "is_visible", toggle=True, text=name[0])
                if size[0] < 1.0:
                    button.scale_x = size[0]
                __build_picker(name[0],slot)
        def __multi(L:list[str], S:list[float]) -> None:
                row = col.row(align=True)
                LS = zip(L,S)
                for name,size in LS:                     
                    slot = row.row(align=True)
                    button = slot.row(align=True)
                    button.prop(bone_colctns[name], "is_visible", toggle=True, text=name)
                    if size < 1.0:
                        button.scale_x = size
                    __build_picker(name,slot)
        def __build_picker(Name:str,slot):
            picker = slot.row(align=True)
            op = picker.operator("select.colection", text="", icon="RESTRICT_SELECT_OFF")
            op.bcoll_name = Name
            op.arm_name = context.active_object.name
        __do = {"Single":__single, "Multi":__multi}
        bp = Rig_UI_Mia.Button_Props# ffs 

        order = [
                bp(["Root"]),
                bp(["Face Master","Face Ctrls","Face Tweaks"]),
                bp(["Spine","Spine Tweaks","Torso Tweak"],size = [1.0,1.0,.5]),
                bp(["Ik Arm","Arm Tweak","Fk Arm"],size = [1.0,.5,1.0]),
                bp(["Arm Tweak"]),
                bp(["FK Finger Master","Fk Finger","Fk Finger Tweak"],size = [1.0,1.0,.5]),
                bp(["Leg Ik","Leg Tweaks","Leg Fk"],size = [1.0,.5,1.0]),
                bp(["Weapon"]),
                bp(["Skirt","BoneDynamcis"],size = [1.0,.25]),
                ]

        for r in order:
            __do[r.amount](r.names,r.size)



        #LayerManagerEnd
    ###End of Rig_UI_MIA
classes.append(Rig_UI_Mia)

class Select_Colectionn(bpy.types.Operator):
    bl_idname = "select.colection"
    bl_label = ""
    bl_description = "Select all Bones in Collection.\nShift to add to selection. \nAlt to remove from selection"

    bcoll_name : bpy.props.StringProperty(name="Collection name", description="Name of bone collection", default="",)
    arm_name : bpy.props.StringProperty(name="Armature name", description="Name of armature", default="",)

    @classmethod
    def poll(self, context):

        return context.mode == "POSE"

    def __init__(self):
        self.shift = False
        self.alt = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)

    def execute(self, context):
        ob = context.active_object
        arm = ob.data
        bcoll = arm.collections[self.bcoll_name]

        if self.alt:
            bones = self.get_bones(arm, bcoll, True)
            for bone in bones:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        else:
           
            bones = self.get_bones(arm, bcoll, False)
            if not self.shift:
                bpy.ops.pose.select_all(action="DESELECT")

            for bone in bones:
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
        return {"FINISHED"}
                    
    def get_bones(self,arm, collection, selected):
        if collection:
            bones = arm.collections[collection.name].bones
            if selected:
                try:
                    bones = [bone for bone in bones if bone.select is True]
                except TypeError:
                    return []
        elif selected and not collection:
            try:
                bones = [bone for bone in arm.bones if bone.select is True]
            except TypeError:
                return []
        else:
            bones = arm.bones
        return bones
    #end of select colections operator
classes.append(Select_Colectionn)

class Mia_Rig_Props(bpy.types.Panel):
    bl_category = 'Item'
    bl_label = "Mia Rig Props"
    bl_idname = "Mia_Rig_Props"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        if context.active_object.data.get('rig_id'):
            pose_bones = context.selected_pose_bones
            props = None
            rna_properties = {prop.identifier for prop in bpy.types.PoseBone.bl_rna.properties if prop.is_runtime}
            if context.selected_pose_bones:                      #if pose mode
                bones = context.selected_pose_bones              # bones? is pose_bones(we already have this tf?)

            elif context.selected_editable_bones:       # else if edit mode                                                         
                objs = (*[o for o in {context.active_object}],*[o for o in context.selected_objects if (o != context.active_object and o.type == 'ARMATURE')])#if pose mode
                bones = [b for o in objs for b in getattr(o.pose, "bones", []) if o.data.edit_bones[f'{b.name}'].select]

            else:                                                  #else no show
                return False
            
            
            if bones:
                props = [[prop for prop in bone.items() if prop not in rna_properties] for bone in bones]

            if (len(props) != 1 or props[0]) and bones:
                return (context.active_object.data.get("rig_id") == "MIA")
            else:
                return False

        else:
            return False

    def draw(self, context):
        layout = self.layout
        if context.mode == 'POSE':
            bones = context.selected_pose_bones
        else:   
            objs = (*[o for o in {context.active_object}],*[o for o in context.selected_objects if (o != context.active_object and o.type == 'ARMATURE')])
            if context.mode == "EDIT_ARMATURE":
                bones = [b for o in objs for b in getattr(o.pose, "bones", []) if o.data.edit_bones[f'{b.name}'].select]
            else:
                bones = [b for o in objs for b in getattr(o.pose, 'bones',[]) if b.bone.select]
            

        for bone in bones:
            if bone.items():
                box = layout.box()
                box.label(text=(bone.name) , icon="BONE_DATA")
                
                for key in sorted(bone.keys()):
                    
                    row = box.row()
                    split = row.split(align=True, factor=0.7)
                    row = split.row(align=True)
                    row.label(text=key, translate=False)
                    row = split.row(align=True)
                    row.prop(bone, f'["{key}"]', text = "", slider=True)
classes.append(Mia_Rig_Props)    

class Catch_and_Throw(bpy.types.Operator):
    bl_idname = "catchthrow.switch"
    bl_label = ""
    bl_description = "Turns a child of constraint on or off and moves and keys the bone acordingly."
    """ 
    First grab the axe bone and the bone the constraint points to(step dad)
    first and a half get curent keyframe, and the const
    Second is const on or off rn?
    if on:
        on past keyframe hit constrant value and axe pos
        on this key frame aply visual transform set const to 0 
        key axe pos and const value
    if off # ima keep it real i have no fuckin clue how to do this one
        grab axe global?
        key frame on past
        turn on 
        move axe 
        key again
    """

    axe = "Ctrl_Axe_Root_Origin.X"
    @classmethod
    def poll(self, context):
        if bpy.context.selected_pose_bones and bpy.context.selected_pose_bones[0].name == self.axe:
            return context.mode == "POSE"
        return False
        

    def execute(self, context):
        
        bone = bpy.context.selected_pose_bones[0]
        for c in bone.constraints:
            if c.name == "Throw_Catch":
                const = c
        step_dad = const.subtarget #the bone acting as the parent when child of is on
        frame = bpy.data.scenes[0].frame_current

        bone.insert_keyframe(const.influence, frame = frame -1 )


classes.append(Catch_and_Throw)  

class Throw_Catch(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_label = "Special Props"
    bl_idname = "Throw_Catch"

    axe = "Ctrl_Axe_Root_Origin.X"
    @classmethod
    def poll(self, context):
        if bpy.context.selected_pose_bones and bpy.context.selected_pose_bones[0].name == self.axe:
            return context.mode == "POSE"
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        row = col.row(align=True)
        slot = row.row(align=True)
        button = slot.row(align=True)
        button.operator("catchthrow.switch", text = "Throw/Catch")


classes.append(Throw_Catch)


"""


"""




















def register():
    for cls in classes:
        try:
            register_class(cls)

        except RuntimeError:
            pass
def unregister():
    for cls in classes:
        try:
            unregister_class(cls)

        except RuntimeError:
            pass
        
if __name__ == "__main__":
    register()