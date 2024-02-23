from pygame import Vector2

FPS = 60
TILESIZE = 64
OVERLAY_OFFSETS = {
    "tool": (50, -100),
    "seed": (150, -100),
}
ITEM_BOX_SIZE = 80
ITEM_BOX_BORDER_WIDTH = 5
UI_BG_COLOR = "white"
UI_BORDER_COLOR = "gold"
LAYERS = {
    "water": 0,
    "ground": 1,
    "soil": 2,
    "soil_water": 3,
    "rain_floor": 4,
    "house_bottom": 5,
    "ground_plant": 6,
    "main": 7,
    "fruit": 8,
    "rain_drops": 9,
}
FRUIT_POSITIONS = {
    "small": [(18, 17), (30, 37), (12, 50), (20, 30)],
    "large": [(30, 24), (60, 65), (50, 50), (16, 40)],
}
PLAYER_TOOL_OFFSET = {
    "left": Vector2(-50, 40),
    "right": Vector2(50, 40),
    "up": Vector2(0, -10),
    "down": Vector2(0, 50),
}
GROW_SPEED = {
    "corn": 1,
    "tomato": 0.7,
}
