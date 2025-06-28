bl_info = {
    "name": "Text Value Controller (Multi)",
    "author": "ChatGPT",
    "version": (1, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > TextValue",
    "description": "Use multiple custom properties to drive text display",
    "category": "Animation",
}

import bpy
from bpy.props import (
    PointerProperty,
    StringProperty,
    FloatProperty,
    CollectionProperty,
    IntProperty
)
from bpy.types import (
    Panel,
    PropertyGroup,
    Operator
)


class TVCItem(PropertyGroup):
    controller: PointerProperty(
        name="Controller",
        type=bpy.types.Object,
        description="Object with custom property (e.g., Empty)"
    )
    property_name: StringProperty(
        name="Property Name",
        default="value"
    )
    text_object: PointerProperty(
        name="Text Object",
        type=bpy.types.Object,
        description="Text object to update"
    )
    value_min: FloatProperty(name="Min", default=0.0)
    value_max: FloatProperty(name="Max", default=100.0)
    suffix: StringProperty(name="Suffix", default="%")

class TVCSettings(PropertyGroup):
    items: CollectionProperty(type=TVCItem)
    active_index: IntProperty(default=0)


class TVC_OT_AddItem(Operator):
    bl_idname = "tvc.add_item"
    bl_label = "Add Controller Entry"
    def execute(self, context):
        context.scene.tvc_settings.items.add()
        return {'FINISHED'}


class TVC_OT_RemoveItem(Operator):
    bl_idname = "tvc.remove_item"
    bl_label = "Remove Controller Entry"
    def execute(self, context):
        settings = context.scene.tvc_settings
        if settings.items:
            settings.items.remove(settings.active_index)
            settings.active_index = max(0, settings.active_index - 1)
        return {'FINISHED'}


class TVC_PT_MainPanel(Panel):
    bl_label = "Text Value Controller"
    bl_idname = "TVC_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TextValue'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tvc_settings

        row = layout.row()
        row.operator("tvc.add_item", icon='ADD')
        row.operator("tvc.remove_item", icon='REMOVE')

        layout.separator()

        for i, item in enumerate(settings.items):
            box = layout.box()
            row = box.row()
            row.label(text=f"Controller {i+1}")
            box.prop(item, "controller")
            box.prop(item, "property_name")
            box.prop(item, "text_object")
            box.prop(item, "value_min")
            box.prop(item, "value_max")
            box.prop(item, "suffix")


def tvc_update_text(scene):
    for scn in bpy.data.scenes:
        if not hasattr(scn, "tvc_settings"):
            continue
        settings = scn.tvc_settings
        for item in settings.items:
            ctrl = item.controller
            txt = item.text_object
            prop = item.property_name

            if ctrl and txt and prop in ctrl:
                raw_val = ctrl[prop]
                mapped_val = item.value_min + (item.value_max - item.value_min) * raw_val
                txt.data.body = f"{mapped_val:.0f}{item.suffix}"


classes = [
    TVCItem,
    TVCSettings,
    TVC_OT_AddItem,
    TVC_OT_RemoveItem,
    TVC_PT_MainPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.tvc_settings = PointerProperty(type=TVCSettings)

    if tvc_update_text not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(tvc_update_text)

def unregister():
    if tvc_update_text in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(tvc_update_text)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.tvc_settings

if __name__ == "__main__":
    register()
