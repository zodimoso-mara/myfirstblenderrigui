import mathutils, math, bpy
class RetrunToMonk(bpy.types.Operator):
    bl_idname = "wm.r2m"
    bl_label = "Return To Monke"
    def execute(self, context):
        print(math.pi)
        objects = bpy.context.scene.objects
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete() 
        bpy.ops.mesh.primitive_monkey_add()
        return {'FINISHED'}
    
class ObjectSelectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select"
    bl_label = "Select"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="My Select Panel")

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Selection Tools")
        box.operator("object.select_all").action = 'TOGGLE'
        row = box.row()
        row.operator("object.select_all").action = 'INVERT'
        row.operator("object.select_random")


bpy.utils.register_class(ObjectSelectPanel)

bpy.ops.wm.r2m()