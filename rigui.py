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
        def __init__(self, names:list[str], size:list[float] = None, amount:str = "Single") -> None:
            self.names = names
            self.size = size
            if size == None:
                self.size = [1.0 for i in names]
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
        def __multi(L:list[str], S:list[float]) -> None:
                row = col.row(align=True)
                LS = zip(L,S)
                for name,size in LS: 
                    
                    slot = row.row(align=True)
                    button = slot.row(align=True)
                    button.prop(bone_colctns[name], "is_visible", toggle=True, text=name)
                    if size < 1.0:
                        button.scale_x = size
        __do = {"Single":__single, "Multi":__multi}
        bp = Rig_UI_Mia.Button_Props# ffs 

        order = [
                bp(["Root"]),
                bp(["Root","Face Master"],size = [1.0,0.5], amount="Multi")
                ]

        for r in order:
            __do[r.amount](r.names,r.size)



        #LayerManagerEnd
        

        #row = col.row(align=True)
        #slot = row.row(align=True)
        #button = slot.row(align=True)
        #button.prop(bone_colctns["Root"], "is_visible", toggle=True, text="Root")
        #picker = slot.row(align=True)
        #op = picker.operator("bonemanex.collection_select", text="", icon="RESTRICT_SELECT_OFF")
        #op.bcoll_name = "Root"
        #op.arm_name = context.active_object.name
        #row = layout.row(align=True)
        #slot = row.row(align=True)
        #button = slot.row(align=True)
        
        
        #button.prop(bone_colctns["Face Master"], "is_visible", toggle=True, text="Face Master")

###End of Rig_UI_MIA
classes.append(Rig_UI_Mia)





























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