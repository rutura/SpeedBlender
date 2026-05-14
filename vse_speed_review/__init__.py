import bpy
from bpy.app.handlers import persistent

bl_info = {
    "name": "VSE Speed Review",
    "author": "Jane Doe",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "Video Sequencer > Sidebar > Speed Review",
    "description": "Keyboard-driven playback speed control for VSE review via frame-skipping",
    "category": "Sequencer",
}

# Ordered list of speed enum values for cycling
_SPEED_ORDER = ["NORMAL", "FAST", "FASTER", "DOUBLE", "TRIPLE"]

# Keymap entries stored for clean unregistration
_keymap_items = []


class VSESpeedReviewProperties(bpy.types.PropertyGroup):
    playback_speed: bpy.props.EnumProperty(
        name="Playback Speed",
        description="Frame-skip speed for VSE review playback (never affects render output)",
        items=[
            ("NORMAL",  "1x",    "No frame skipping",               0),
            ("FAST",    "1.33x", "Skip: +1 every 3rd frame",        1),
            ("FASTER",  "1.5x",  "Skip: +1 every other frame",      2),
            ("DOUBLE",  "2x",    "Skip: +1 every frame",            3),
            ("TRIPLE",  "3x",    "Skip: +2 every frame",            4),
        ],
        default="NORMAL",
    )


@persistent
def vse_speed_frame_change(scene, depsgraph):
    # Guard: only run during active playback, not scrubbing
    screen = bpy.context.screen
    if screen is None or not screen.is_animation_playing:
        return

    # NOTE: We use the handler's `scene` argument (the active scene) rather than
    # context.workspace.sequencer_scene (introduced in 5.0+). This is intentional —
    # we want to piggyback on Blender's own playback tick for the active scene.
    # If the VSE is editing a different scene than the active one, the frame counter
    # may drift, but that is an acceptable trade-off for simplicity.
    speed = scene.vse_speed_review.playback_speed

    if speed == "NORMAL":
        return
    elif speed == "FAST":
        if scene.frame_current % 3 == 0:
            bpy.ops.screen.frame_offset(delta=1)
    elif speed == "FASTER":
        if scene.frame_current % 2 == 0:
            bpy.ops.screen.frame_offset(delta=1)
    elif speed == "DOUBLE":
        bpy.ops.screen.frame_offset(delta=1)
    elif speed == "TRIPLE":
        bpy.ops.screen.frame_offset(delta=2)


class SEQUENCER_OT_vse_speed_review_increase(bpy.types.Operator):
    bl_idname = "sequencer.vse_speed_review_increase"
    bl_label = "Increase VSE Playback Speed"
    bl_description = "Cycle playback speed up (. key)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.space_data is not None and context.space_data.type == "SEQUENCE_EDITOR"

    def execute(self, context):
        props = context.scene.vse_speed_review
        current = props.playback_speed
        idx = _SPEED_ORDER.index(current)
        new_idx = min(idx + 1, len(_SPEED_ORDER) - 1)
        new_value = _SPEED_ORDER[new_idx]
        props.playback_speed = new_value
        self.report({"INFO"}, f"Playback speed: {new_value}")
        return {"FINISHED"}


class SEQUENCER_OT_vse_speed_review_decrease(bpy.types.Operator):
    bl_idname = "sequencer.vse_speed_review_decrease"
    bl_label = "Decrease VSE Playback Speed"
    bl_description = "Cycle playback speed down (, key)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.space_data is not None and context.space_data.type == "SEQUENCE_EDITOR"

    def execute(self, context):
        props = context.scene.vse_speed_review
        current = props.playback_speed
        idx = _SPEED_ORDER.index(current)
        new_idx = max(idx - 1, 0)
        new_value = _SPEED_ORDER[new_idx]
        props.playback_speed = new_value
        self.report({"INFO"}, f"Playback speed: {new_value}")
        return {"FINISHED"}


class VSE_PT_speed_review(bpy.types.Panel):
    bl_label = "Speed Review"
    bl_idname = "VSE_PT_speed_review"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Speed Review"

    def draw(self, context):
        layout = self.layout
        props = context.scene.vse_speed_review
        render = context.scene.render

        # Speed control
        layout.label(text="Playback Speed")
        row = layout.row(align=True)
        row.operator("sequencer.vse_speed_review_decrease", text="", icon="TRIA_LEFT")
        row.prop(props, "playback_speed", text="")
        row.operator("sequencer.vse_speed_review_increase", text="", icon="TRIA_RIGHT")

        layout.separator()

        # Playback settings — these matter for frame-skipping to work correctly
        layout.label(text="Playback Settings")
        col = layout.column(align=True)
        col.prop(context.scene, "sync_mode", text="Sync")
        col.prop(render, "use_sequencer", text="Use Sequencer")

        layout.separator()

        # Hotkey reminder
        col = layout.column()
        col.scale_y = 0.7
        col.label(text=". = faster   , = slower", icon="INFO")
        col.label(text="Requires: Frame Dropping sync")


_classes = [
    VSESpeedReviewProperties,
    SEQUENCER_OT_vse_speed_review_increase,
    SEQUENCER_OT_vse_speed_review_decrease,
    VSE_PT_speed_review,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vse_speed_review = bpy.props.PointerProperty(
        type=VSESpeedReviewProperties
    )

    # Avoid duplicate handler entries if the add-on is reloaded
    handlers = bpy.app.handlers.frame_change_post
    if vse_speed_frame_change not in handlers:
        handlers.append(vse_speed_frame_change)

    # Register keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Sequencer", space_type="SEQUENCE_EDITOR", region_type="WINDOW")

        kmi_inc = km.keymap_items.new(
            "sequencer.vse_speed_review_increase",
            type="PERIOD",
            value="PRESS",
        )
        _keymap_items.append((km, kmi_inc))

        kmi_dec = km.keymap_items.new(
            "sequencer.vse_speed_review_decrease",
            type="COMMA",
            value="PRESS",
        )
        _keymap_items.append((km, kmi_dec))


def unregister():
    # Remove keymap entries
    for km, kmi in _keymap_items:
        km.keymap_items.remove(kmi)
    _keymap_items.clear()

    # Remove handler
    handlers = bpy.app.handlers.frame_change_post
    if vse_speed_frame_change in handlers:
        handlers.remove(vse_speed_frame_change)

    del bpy.types.Scene.vse_speed_review

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
