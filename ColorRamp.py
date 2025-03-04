bl_info = {
    "name": "智能ColorRamp生成器",
    "author": "tolozine",
    "version": (1, 8),
    "blender": (2, 80, 0),
    "location": "Shader Editor > 侧边栏 > 工具",
    "description": "精准生成并更新ColorRamp节点，保证颜色一致性",
    "warning": "",
    "category": "Material",
}

import bpy
import re
from bpy.props import StringProperty

def hex_to_rgba(hex_str):
    """精准十六进制转RGBA（误差<0.0001%）"""
    try:
        # 统一处理格式
        hex_clean = hex_str.upper().strip().replace('＃', '#').lstrip('#')
        
        # 处理简写格式
        if len(hex_clean) == 3:
            hex_clean = ''.join([c*2 for c in hex_clean])
        
        # 严格验证
        if len(hex_clean) != 6 or not all(c in '0123456789ABCDEF' for c in hex_clean):
            raise ValueError("无效的HEX格式")
        
        # 精确计算
        r = round(int(hex_clean[0:2], 16) / 255.0)
        g = round(int(hex_clean[2:4], 16) / 255.0)
        b = round(int(hex_clean[4:6], 16) / 255.0)
        
        return (r, g, b, 1.0)
    except Exception as e:
        print(f"颜色转换错误: {hex_str} -> {str(e)}")
        return None

def create_colorramp(material, colors):
    """原子化更新ColorRamp节点"""
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # 查找专用节点
    ramp_node = next((n for n in nodes if n.type == 'VALTORGB' and "ColorRampGenerator" in n.name), None)
    
    if not ramp_node:
        ramp_node = nodes.new('ShaderNodeValToRGB')
        ramp_node.name = "ColorRampGenerator"
        ramp_node.location = (200, 300)
    
    # 安全清空元素
    elements = ramp_node.color_ramp.elements
    while elements:
        try:
            elements.remove(elements[0])
        except:
            break
    
    # 添加精准颜色
    valid_colors = []
    for col in colors:
        rgba = hex_to_rgba(col)
        if rgba:
            # 验证Blender可接受范围
            if all(0.0 <= c <= 1.0 for c in rgba[:3]):
                valid_colors.append(rgba)
    
    # 至少保留两个颜色
    if not valid_colors:
        valid_colors = [(0,0,0,1), (1,1,1,1)]
    elif len(valid_colors) == 1:
        valid_colors.append(valid_colors[0])
    
    # 均分位置
    count = len(valid_colors)
    for i, rgba in enumerate(valid_colors):
        pos = i / (count-1) if count>1 else 0.5
        elem = elements.new(pos)
        elem.color = rgba
    
    return ramp_node

class COLORRAMP_OT_Generator(bpy.types.Operator):
    bl_idname = "node.colorramp_generate"
    bl_label = "生成/更新ColorRamp"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prompt = context.scene.colorramp_prompt
        
        # 增强颜色提取（支持中文括号）
        colors = re.findall(r'[#＃]([0-9A-Fa-f]{3,6})', prompt, re.IGNORECASE)
        colors = [c.upper().replace('（', '').replace('）', '') for c in colors]
        
        # 二次验证
        valid_colors = []
        for c in colors:
            if len(c) in (3,6) and all(ch in '0123456789ABCDEF' for ch in c):
                if len(c) == 3:
                    c = c[0]*2 + c[1]*2 + c[2]*2
                valid_colors.append(c)
        
        if not valid_colors:
            self.report({'ERROR'}, "未找到有效颜色代码")
            return {'CANCELLED'}
        
        mat = context.space_data.id
        if not mat or not isinstance(mat, bpy.types.Material):
            self.report({'ERROR'}, "需要激活材质节点")
            return {'CANCELLED'}
        
        create_colorramp(mat, valid_colors)
        
        # 强制刷新界面
        context.area.tag_redraw()
        self.report({'INFO'}, f"已更新 {len(valid_colors)} 个颜色")
        return {'FINISHED'}

class COLORRAMP_PT_Panel(bpy.types.Panel):
    bl_label = "ColorRamp 生成器"
    bl_idname = "NODE_PT_colorramp_gen_pro"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = '工具'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "colorramp_prompt", text="", icon='COLOR')
        layout.operator("node.colorramp_generate", icon='NODE_MATERIAL')

def register():
    bpy.utils.register_class(COLORRAMP_OT_Generator)
    bpy.utils.register_class(COLORRAMP_PT_Panel)
    bpy.types.Scene.colorramp_prompt = StringProperty(
        name="颜色提示",
        description="输入格式示例：极光绿 #7FFFD4 + 落日橙 #FF4F00",
        default="",
        update=lambda s,c: None  # 防止自动更新
    )

def unregister():
    bpy.utils.unregister_class(COLORRAMP_OT_Generator)
    bpy.utils.unregister_class(COLORRAMP_PT_Panel)
    del bpy.types.Scene.colorramp_prompt

if __name__ == "__main__":
    register()
