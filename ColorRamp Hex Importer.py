import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty

bl_info = {
    "name": "ColorRamp HEX Importer",
    "author": "tolozine ",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "Node Editor > Sidebar > ColorRamp Tools",
    "description": "Apply HEX colors to ColorRamp nodes",
    "category": "Node",
}

class COLORRAMP_HEX_OT_apply(Operator):
    """Apply HEX colors to selected ColorRamp node"""
    bl_idname = "colorramp_hex.apply"
    bl_label = "Apply HEX Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        hex_tool = scene.hex_tool
        
        # 获取选中的ColorRamp节点
        active_node = context.active_node
        if not active_node or active_node.type != 'VALTORGB':
            self.report({'ERROR'}, "No active ColorRamp node selected")
            return {'CANCELLED'}
        
        ramp_node = active_node
        ramp = ramp_node.color_ramp
        
        # 清理输入字符串
        hex_string = hex_tool.hex_colors.replace('#', '').strip()
        if not hex_string:
            self.report({'ERROR'}, "No HEX colors provided")
            return {'CANCELLED'}
        
        # 分割HEX值
        hex_list = []
        separators = [',', ';', ' ', '\n', '\t']
        for sep in separators:
            if sep in hex_string:
                hex_list = [c.strip() for c in hex_string.split(sep) if c.strip()]
                break
        else:
            hex_list = [hex_string]  # 单个颜色
        
        # 验证并处理HEX值
        valid_hex_colors = []
        for hex_color in hex_list:
            hex_color = hex_color.upper()
            # 处理3位简写HEX
            if len(hex_color) == 3:
                hex_color = f"{hex_color[0]}{hex_color[0]}{hex_color[1]}{hex_color[1]}{hex_color[2]}{hex_color[2]}"
            # 验证6位HEX
            if len(hex_color) != 6:
                self.report({'WARNING'}, f"Skipping invalid HEX: {hex_color}")
                continue
            # 验证字符
            valid_chars = "0123456789ABCDEF"
            if all(c in valid_chars for c in hex_color):
                valid_hex_colors.append(hex_color)
        
        if not valid_hex_colors:
            self.report({'ERROR'}, "No valid HEX colors found")
            return {'CANCELLED'}
        
        # 安全清空现有色标（使用Blender推荐方法）
        # 1. 保留第一个元素
        # 2. 删除所有其他元素
        # 3. 然后修改第一个元素或添加新元素
        
        num_colors = len(valid_hex_colors)
        
        # 确保至少有一个元素
        if not ramp.elements:
            ramp.elements.new(position=0.0)
        
        # 保留第一个元素，删除其他所有元素
        while len(ramp.elements) > 1:
            ramp.elements.remove(ramp.elements[1])
        
        # 设置第一个元素
        elem = ramp.elements[0]
        hex_color = valid_hex_colors[0]
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        elem.color = (r, g, b, 1)
        elem.position = 0.0
        
        # 添加剩余颜色
        if num_colors > 1:
            for i in range(1, num_colors):
                pos = i / (num_colors - 1)  # 均匀分布位置
                elem = ramp.elements.new(position=pos)
                
                hex_color = valid_hex_colors[i]
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                elem.color = (r, g, b, 1)
        
        self.report({'INFO'}, f"Applied {num_colors} colors to ColorRamp")
        return {'FINISHED'}

class ColorRampHexProperties(PropertyGroup):
    hex_colors: StringProperty(
        name="HEX Colors",
        description="Enter HEX colors separated by commas, spaces or new lines",
        default="#264653, #2a9d8f, #e9c46a, #f4a261, #e76f51"
    )

class COLORRAMP_HEX_PT_panel(Panel):
    """Creates a Panel in the Node Editor sidebar"""
    bl_label = "ColorRamp HEX Tools"
    bl_idname = "COLORRAMP_HEX_PT_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "ColorRamp Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hex_tool = scene.hex_tool
        
        # 当前活动节点信息
        active_node = context.active_node
        if active_node and active_node.type == 'VALTORGB':
            layout.label(text=f"Active: {active_node.name}", icon='NODE')
        else:
            layout.label(text="No ColorRamp selected", icon='ERROR')
        
        # HEX输入框
        layout.prop(hex_tool, "hex_colors", text="")
        
        # 操作按钮
        row = layout.row()
        row.operator("colorramp_hex.apply", icon='NODETREE')
        
        # 使用说明
        box = layout.box()
        box.label(text="Instructions:", icon='INFO')
        box.label(text="1. 在节点编辑器中选择ColorRamp节点")
        box.label(text="2. 输入HEX颜色（用逗号、空格或换行分隔）")
        box.label(text="3. 点击Apply按钮应用")
        box.label(text="示例: #FF0000 #00FF00 #0000FF")
        box.label(text="或: FF0000, 00FF00, 0000FF")

def register():
    bpy.utils.register_class(COLORRAMP_HEX_OT_apply)
    bpy.utils.register_class(ColorRampHexProperties)
    bpy.utils.register_class(COLORRAMP_HEX_PT_panel)
    bpy.types.Scene.hex_tool = PointerProperty(type=ColorRampHexProperties)

def unregister():
    bpy.utils.unregister_class(COLORRAMP_HEX_OT_apply)
    bpy.utils.unregister_class(ColorRampHexProperties)
    bpy.utils.unregister_class(COLORRAMP_HEX_PT_panel)
    del bpy.types.Scene.hex_tool

if __name__ == "__main__":
    register()