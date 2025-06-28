

🧩 一、插件安装
点击此链接下载插件：TextValueController.zip

打开 Blender，点击顶部菜单 Edit > Preferences > Add-ons

点击左上角 Install... 按钮，选择下载的 TextValueController.zip

勾选插件左边的复选框启用它

在 3D 视图中按 N 键打开右侧工具栏，切换到 TextValue 标签页

🧱 二、准备对象和属性
1. 创建控制器对象
Shift + A > Empty > Plain Axes

选中该空物体，按 F2 重命名，例如：BrightnessController

在右侧属性面板，点击最下方的「自定义属性 > Add」按钮

命名为 value，设置初始值为 0.0

2. 插入关键帧（实现随时间变化）
确保选中 BrightnessController

在 value 上右键 > Insert Keyframe（帧1）

将时间轴拉到帧60

改为 1.0，再右键 > Insert Keyframe

✅ 这样 value 会从 0.0 变化到 1.0，随时间轴自动更新

3. 创建文字对象
Shift + A > Text 添加文字对象

在右侧属性中修改名字为：BrightnessText

可旋转并放置于界面中可见位置

⚙️ 三、在插件中设置控制关系
打开 TextValue 面板（右侧工具栏 N 键）

点击 Add Controller Entry

设置以下参数：

参数	设置内容
Controller	选择你创建的 BrightnessController
Property Name	输入 value（与自定义属性名称一致）
Text Object	选择 BrightnessText
Min / Max	比如设置为 69 到 100
Suffix	输入 % 或 K 等你想显示的单位

▶️ 四、运行动画查看效果
点击播放（空格键）

或者用时间轴拖动帧数

观察 BrightnessText 文本将自动更新，例如：

shell
复制
编辑
69% ➜ 100%
