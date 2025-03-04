bl_info = {
    "name": "ColorRamp 生成器",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Shader Editor > 侧边栏 > 工具",
    "description": "通过输入提示词生成 ColorRamp 节点，并均分提示词中的颜色",
    "warning": "",
    "wiki_url": "",
    "category": "Material",
}

import bpy
import re
from bpy.props import StringProperty

def hex_to_rgba(hex_str):
    """将3位或6位十六进制颜色转换为RGBA"""
    try:
        hex_str = hex_str.lstrip('#').lstrip('＃')
        # 处理3位简写格式（如#FFF）
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        return (
            int(hex_str[0:2], 16)/255.0,
            int(hex_str[2:4], 16)/255.0,
            int(hex_str[4:6], 16)/255.0,
            1.0
        )
    except:
        return (1, 1, 1, 1)

def create_colorramp(material, colors):
    """安全创建/更新 ColorRamp 节点"""
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # 查找或创建节点
    ramp_node = next((n for n in nodes if n.type == 'VALTORGB'), None)
    if not ramp_node:
        ramp_node = nodes.new('ShaderNodeValToRGB')
        ramp_node.location = (200, 300)
    else:
        # 安全清空颜色点（关键修复部分）
        elements = ramp_node.color_ramp.elements
        while elements:
            elements.remove(elements[0])

    # 添加新颜色（修复缩进）
    elements = ramp_node.color_ramp.elements
    count = max(len(colors), 1)
    for i, col in enumerate(colors):
        pos = i / (count - 1) if count > 1 else 0.5
        elem = elements.new(pos)
        elem.color = hex_to_rgba(col)
    return ramp_node

class NODE_OT_CreateColorRamp(bpy.types.Operator):
    """操作符类（注意冒号和缩进）"""
    bl_idname = "node.create_colorramp"
    bl_label = "生成 ColorRamp 节点"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 确保以下代码正确缩进（关键）
        prompt = context.scene.colorramp_prompt
        colors = re.findall(r'[#＃]([0-9a-fA-F]{6}|[0-9a-fA-F]{3})[）)]?', prompt)
        colors = [c for c in colors if len(c) in (3,6)]
        if not colors:
            self.report({'WARNING'}, "未找到有效的十六进制颜色")
            return {'CANCELLED'}
        
        mat = context.space_data.id
        if mat is None:
            self.report({'WARNING'}, "请确保当前 Shader Editor 中激活了材质")
            return {'CANCELLED'}
        
        create_colorramp(mat, colors)
        self.report({'INFO'}, f"生成 ColorRamp 节点，包含 {len(colors)} 个颜色")
        return {'FINISHED'}

class NODE_PT_ColorRampPanel(bpy.types.Panel):
    """面板类（注意缩进层级）"""
    bl_label = "ColorRamp 生成器"
    bl_idname = "NODE_PT_colorramp_generator"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = '工具'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "colorramp_prompt", text="提示词")
        layout.operator("node.create_colorramp")

def register():
    bpy.utils.register_class(NODE_OT_CreateColorRamp)
    bpy.utils.register_class(NODE_PT_ColorRampPanel)
    bpy.types.Scene.colorramp_prompt = StringProperty(
        name="提示词",
        description="输入示例：天空蓝（#87CEEB） + 草地绿（#7CFC00）",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(NODE_OT_CreateColorRamp)
    bpy.utils.unregister_class(NODE_PT_ColorRampPanel)
    del bpy.types.Scene.colorramp_prompt

if __name__ == "__main__":
    register()
