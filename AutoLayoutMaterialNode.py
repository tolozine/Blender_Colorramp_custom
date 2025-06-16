bl_info = {
    "name": "Auto Layout Material Nodes",
    "author": "ChatGPT",
    "version": (1, 6),
    "blender": (2, 93, 0),
    "location": "Shader Editor > Sidebar > Node Layout",
    "description": "Arrange material nodes: full layout or selected node's upstream only",
    "category": "Node",
}

import bpy
from collections import defaultdict

def walk_upstream(node, level=0, levels=None, visited=None):
    if levels is None:
        levels = {}
    if visited is None:
        visited = set()

    if node in visited:
        return levels
    visited.add(node)

    levels[node] = max(levels.get(node, 0), level)
    for input in node.inputs:
        for link in input.links:
            walk_upstream(link.from_node, level + 1, levels, visited)

    return levels


def arrange_nodes(levels, x_gap=300, y_gap=200):
    level_dict = defaultdict(list)
    for node, level in levels.items():
        level_dict[level].append(node)

    for level in sorted(level_dict):
        row = level_dict[level]
        for i, node in enumerate(row):
            node.location.x = -level * x_gap
            node.location.y = -i * y_gap


class NODE_OT_auto_layout_all(bpy.types.Operator):
    bl_idname = "node.auto_layout_material"
    bl_label = "Layout All Nodes"
    bl_description = "Auto arrange all material nodes from output"

    def execute(self, context):
        space = context.space_data
        if space.type != 'NODE_EDITOR' or space.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "Run in Shader Editor with material nodes.")
            return {'CANCELLED'}

        tree = space.edit_tree
        if not tree or not tree.nodes:
            self.report({'WARNING'}, "No node tree or nodes found.")
            return {'CANCELLED'}

        levels = {}
        visited = set()

        def walk(node, level=0):
            if node in visited:
                return
            visited.add(node)
            levels[node] = max(levels.get(node, 0), level)
            for output in node.outputs:
                for link in output.links:
                    walk(link.to_node, level + 1)

        output_nodes = [n for n in tree.nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)]
        for out in output_nodes:
            walk(out, 0)

        for node in tree.nodes:
            if node not in levels:
                levels[node] = 0

        arrange_nodes(levels)
        return {'FINISHED'}


class NODE_OT_auto_layout_selected(bpy.types.Operator):
    bl_idname = "node.auto_layout_from_selected"
    bl_label = "Layout From Selected"
    bl_description = "Auto layout only the nodes upstream of the selected node"

    def execute(self, context):
        space = context.space_data
        if space.type != 'NODE_EDITOR' or space.tree_type != 'ShaderNodeTree':
            self.report({'WARNING'}, "Run in Shader Editor with material nodes.")
            return {'CANCELLED'}

        tree = space.edit_tree
        selected_nodes = [n for n in tree.nodes if n.select]

        if len(selected_nodes) != 1:
            self.report({'WARNING'}, "Please select exactly one node.")
            return {'CANCELLED'}

        target_node = selected_nodes[0]
        levels = walk_upstream(target_node)

        arrange_nodes(levels)
        return {'FINISHED'}


class NODE_PT_layout_panel(bpy.types.Panel):
    bl_label = "Node Layout"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node Layout'

    def draw(self, context):
        layout = self.layout
        layout.operator("node.auto_layout_material", icon='NODETREE')
        layout.operator("node.auto_layout_from_selected", icon='NODE')

classes = [
    NODE_OT_auto_layout_all,
    NODE_OT_auto_layout_selected,
    NODE_PT_layout_panel,
]

# PIE MENU 操作
class NODE_MT_pie_layout_menu(bpy.types.Menu):
    bl_label = "Material Node Layout Pie Menu"
    bl_idname = "NODE_MT_pie_layout_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 左右上下顺序：left, right, bottom, top
        pie.operator("node.auto_layout_material", text="Layout All Nodes", icon="NODETREE")     # 上
        pie.operator("node.auto_layout_from_selected", text="Layout From Selected", icon="NODE") # 下

addon_keymaps = []

def register_shortcut():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new("wm.call_menu_pie", type='E', value='PRESS')
        kmi.properties.name = "NODE_MT_pie_layout_menu"
        addon_keymaps.append((km, kmi))

def unregister_shortcut():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(NODE_MT_pie_layout_menu)
    register_shortcut()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(NODE_MT_pie_layout_menu)
    unregister_shortcut()



if __name__ == "__main__":
    register()
