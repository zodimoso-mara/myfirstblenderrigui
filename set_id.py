import bpy

def execute(self, context):
    ac_ob = ac_ob = bpy.context.active_object

    set_rig_id = ac_ob.data.get('rig_id', "MIA")
    ac_ob.data['rig_id'] = set_rig_id
    print(ac_ob.data['rig_id'])
