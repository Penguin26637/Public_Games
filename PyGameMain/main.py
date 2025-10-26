import pygame
import sys
import math
import asyncio

# Platform class for moving platforms
class MovingPlatform:
    def __init__(self, x, y, width, height, movement_axis, min_pos, max_pos, speed=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.movement_axis = movement_axis
        self.min_pos = min_pos
        self.max_pos = max_pos
        self.speed = speed
        self.direction = 1

    def update(self, dt):
        if self.movement_axis == "x":
            self.rect.x += self.speed * dt * self.direction
            if self.direction == 1 and self.rect.right >= self.max_pos:
                self.direction = -1
            elif self.direction == -1 and self.rect.left <= self.min_pos:
                self.direction = 1
        elif self.movement_axis == "y":
            self.rect.y += self.speed * dt * self.direction
            if self.direction == 1 and self.rect.bottom >= self.max_pos:
                self.direction = -1
            elif self.direction == -1 and self.rect.top <= self.min_pos:
                self.direction = 1

# Global game state
class GameState:
    def __init__(self):
        self.player_width, self.player_height = 49, 51
        self.player_pos = pygame.Vector2(-9425, 979)
        self.player_pos_reset = pygame.Vector2(-9425, 979)
        self.player_velocity = pygame.Vector2(0, 0)
        self.gravity = 1500
        self.move_speed = 300
        self.jump_strength = 800
        self.jump_count = 0
        self.max_jumps = 2
        self.deaths = 0
        self.end = False
        self.on_ground = False
        self.on_wall_left = False
        self.on_wall_right = False
        self.on_wall_bottom = False
        self.rotation = 0
        self.target_rotation = 0
        self.plat_move = 800
        self.plat_direction = 1
        self.camera_offset = pygame.Vector2(0, 0)
        self.jump_cooldown = 300
        self.last_jump_time = 0
        self.game_size = 10000
        self.speedrun_start_time = 0
        self.finish_time = 0
        self.finish_reached = False
        self.death_screen_enable = False
        self.speedrun_mode = False
        self.game_phase = "death_screen_prompt"  # Track which screen we're on

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
screen_height = 1080
screen_width = 1920
clock = pygame.time.Clock()

fps_font = pygame.font.Font(None, 30)
font = pygame.font.Font(None, 60)
checkpoint_font = pygame.font.Font(None, 40)

state = GameState()

# --- Finish line ---
finish_rect = pygame.Rect(9480, 830, 20, 200)

# --- Static Platforms ---
platforms = [
    pygame.Rect(20, 800, 100, 50),
    pygame.Rect(400, 600, 100, 50),
    pygame.Rect(1600, 100, 100, 50),
    pygame.Rect(state.plat_move, 300, 100, 50),
    pygame.Rect(1800, 300, 10, 50),
    pygame.Rect(2400, 300, 10, 50),
    pygame.Rect(3000, 300, 10, 50),
    pygame.Rect(3600, 300, 10, 50),
    pygame.Rect(4200, 300, 10, 50),
    pygame.Rect(4800, 300, 10, 50),
    pygame.Rect(5400, 300, 10, 50),
    pygame.Rect(6000, 300, 10, 50),
    pygame.Rect(6600, 300, 10, 50),
    pygame.Rect(-200, 0, 10, 800),
    pygame.Rect(-800, 115, 10, 915),
    pygame.Rect(-7298.5, 998.5, 10, 50),
    pygame.Rect(-1514, 0, 1325, 10),
    pygame.Rect(-1514, 0, 10, 800),
    pygame.Rect(-1492, 538, 40, 10),
    pygame.Rect(-1070, 896, 40, 10),
    pygame.Rect(-1330, 722, 40, 10),
    pygame.Rect(-1080, 276, 40, 10),
    pygame.Rect(-794, 224, 40, 10),
    pygame.Rect(-370, 508, 40, 10),
    pygame.Rect(-782, 630, 40, 10),
    pygame.Rect(-578, 900, 10, 40),
    pygame.Rect(-2854, 727, 1241, 10),
    pygame.Rect(-2854, 727, 10, 188),
    pygame.Rect(-3100.5, 423.5, 1590, 10),
    pygame.Rect(-3100.5, 423.5, 10, 550),
    pygame.Rect(-3005.5, 852.5, 75, 10),
    pygame.Rect(-4766, 423, 1671, 10),
    pygame.Rect(-4766, 426.5, 10, 553),
    pygame.Rect(-6800.5, 700.5, 50, 10),
    pygame.Rect(-7777, 370, 870, 10),
    pygame.Rect(8000, 300, 1200, 10),
    pygame.Rect(8000, 969, 1200, 10),
]

# --- Moving Platforms ---
moving_platforms = [
    MovingPlatform(-2834.5, 701.5, 50, 20, "y", 450, 700, 100),
    MovingPlatform(-2500, 400, 50, 20, "y", 450, 700, 60),
    MovingPlatform(-2182, 618, 50, 20, "y", 450, 700, 40),
    MovingPlatform(-1633, 618, 50, 20, "y", 450, 700, 100),
    MovingPlatform(-1998, 618, 50, 20, "y", 450, 700, 150),
    MovingPlatform(-2311, 618, 50, 20, "y", 450, 700, 90),
    MovingPlatform(-2647, 618, 50, 20, "y", 450, 700, 60),
    MovingPlatform(-2844.5, 500.5, 50, 20, "x", -2844.5, -1625.5, 60),
    MovingPlatform(-2844.5, 700, 50, 20, "x", -2844.5, -1625.5, 90),
    MovingPlatform(-2844.5, 534, 50, 20, "x", -2844.5, -1625.5, 170),
    MovingPlatform(-2844.5, 570, 50, 20, "x", -2844.5, -1625.5, 140),
    MovingPlatform(-2844.5, 810, 50, 20, "x", -2844.5, -1625.5, 80),
    MovingPlatform(-2844.5, 974, 50, 20, "x", -2844.5, -1625.5, 140),
    MovingPlatform(7300, 450, 10, 580, "y", 450, 850, 100),
]

safe_moving_platforms = [
    MovingPlatform(-8800, 800, 50, 20, "x", -8800, -8400, 100),
    MovingPlatform(-8300, 452.5, 50, 20, "x", -8300, -7950, 50),
    MovingPlatform(6700, 650, 50, 20, "x", 6700, 7100, 100),
    MovingPlatform(7900, 660, 50, 20, "x", 7500, 7900, 100),
]

# Simplified spike list (just a few for testing)
spikes = [
    [(6226, 104), (6201, 147), (6251, 147)],
    [(6154, 266), (6129, 309), (6179, 309)],
    [(6409, 319), (6384, 362), (6434, 362)],
    [(6386, 80), (6361, 123), (6411, 123)],
    [(6117, -43), (6092, 0), (6142, 0)],
    [(6247, 549), (6222, 592), (6272, 592)],
    [(6540, 411), (6515, 454), (6565, 454)],
    [(6579, 38), (6554, 81), (6604, 81)],
    [(6416, -20), (6391, 23), (6441, 23)],
    [(6004, 65), (5979, 108), (6029, 108)],
    [(6060, 466), (6035, 509), (6085, 509)],
    [(6198, 3), (6174, 46), (6224, 46)],
    [(-361, 987), (-386, 1031), (-336, 1031)],
    [(-503, 987), (-528, 1031), (-478, 1031)],
    [(-585, 984), (-610, 1028), (-560, 1028)],
    [(-660, 989), (-685, 1033), (-635, 1033)],
    [(-731, 984), (-756, 1028), (-706, 1028)],
    [(-448, 987), (-473, 1031), (-423, 1031)],
    [(-618, 51), (-644, 94), (-594, 94)],
    [(-358, 252), (-382, 295), (-332, 295)],
    [(-624, 397), (-648, 440), (-598, 440)],
    [(-690, 842), (-716, 885), (-666, 885)],
    [(92, 743), (68, 786), (118, 786)],
    [(408, 542), (382, 585), (432, 585)],
    [(2100, 281), (2076, 324), (2126, 324)],
    [(2290, 3), (2264, 46), (2314, 46)],
    [(2704, 93), (2678, 136), (2728, 136)],
    [(3326, 3), (3302, 46), (3352, 46)],
    [(3336, 302), (3312, 345), (3362, 345)],
    [(3924, 293), (3900, 336), (3950, 336)],
    [(4434, -91), (4410, -48), (4460, -48)],
    [(4454, 133), (4430, 176), (4480, 176)],
    [(4988, 306), (4962, 349), (5012, 349)],
    [(5226, 299), (5200, 342), (5250, 342)],
    [(5098, 41), (5074, 84), (5124, 84)],
    [(5666, 290), (5642, 333), (5692, 333)],
    [(5522, 73), (5498, 116), (5548, 116)],
    [(5830, 79), (5806, 122), (5856, 122)],
    [(-9478, 968), (-9504, 1011), (-9454, 1011)],
    [(-1132, 975), (-1158, 1018), (-1108, 1018)],
    [(-1470, 698), (-1496, 741), (-1446, 741)],
    [(-840, 986), (-866, 1029), (-816, 1029)],
    [(-1312, 805), (-1338, 848), (-1288, 848)],
    [(-1478, 278), (-1502, 321), (-1452, 321)],
    [(-1162, 476), (-1186, 519), (-1136, 519)],
    [(-836, 771), (-862, 814), (-812, 814)],
    [(-1012, 654), (-1036, 697), (-986, 697)],
    [(-938, 286), (-962, 329), (-912, 329)],
    [(-1402, 43), (-1428, 86), (-1378, 86)],
    [(-1214, 34), (-1238, 77), (-1188, 77)],
    [(-1054, 24), (-1080, 67), (-1030, 67)],
    [(-1062, 968), (-1086, 1011), (-1036, 1011)],
    [(-980, 966), (-1004, 1009), (-954, 1009)],
    [(-908, 961), (-932, 1004), (-882, 1004)],
    [(-974, 483), (-998, 526), (-948, 526)],
    [(-860, 606), (-886, 649), (-836, 649)],
    [(-858, 411), (-882, 454), (-832, 454)],
    [(-1080, 344), (-1104, 387), (-1054, 387)],
    [(-836, 290), (-860, 333), (-810, 333)],
    [(-1094, 591), (-1120, 634), (-1070, 634)],
    [(-1390, 762), (-1416, 805), (-1366, 805)],
    [(-1474, 101), (-1498, 144), (-1448, 144)],
    [(-1458, 176), (-1484, 219), (-1434, 219)],
    [(-1476, 606), (-1502, 649), (-1452, 649)],
    [(-1480, 338), (-1506, 381), (-1456, 381)],
    [(-766, 353), (-792, 396), (-742, 396)],
    [(-762, 706), (-788, 749), (-738, 749)],
    [(-214, 472), (-240, 515), (-190, 515)],
    [(-218, 756), (-242, 799), (-192, 799)],
    [(-298, 732), (-324, 775), (-274, 775)],
    [(-564, 559), (-590, 602), (-540, 602)],
    [(-494, 548), (-518, 591), (-468, 591)],
    [(-416, 554), (-440, 597), (-390, 597)],
    [(-224, 17), (-248, 60), (-198, 60)],
    [(-330, 567), (-356, 610), (-306, 610)],
    [(-264, 612), (-288, 655), (-238, 655)],
    [(-3050, 675), (-3076, 718), (-3026, 718)],
    [(-2912, 675), (-2936, 718), (-2886, 718)],
    [(-2984, 526), (-3008, 569), (-2958, 569)],
    [(-2596, 785), (-2622, 828), (-2572, 828)],
    [(-2444, 984), (-2468, 1027), (-2418, 1027)],
    [(-1936, 963), (-1962, 1006), (-1912, 1006)],
    [(-1730, 778), (-1756, 821), (-1706, 821)],
    [(-2300, 869), (-2324, 912), (-2274, 912)],
    [(-2138, 953), (-2162, 996), (-2112, 996)],
    [(-1590, 869), (-1614, 912), (-1564, 912)],
    [(-2758, 874), (-2784, 917), (-2734, 917)],
    [(-2216, 745), (-2242, 788), (-2192, 788)],
    [(-1866, 959), (-1890, 1002), (-1840, 1002)],
    [(-2028, 750), (-2054, 793), (-2004, 793)],
    [(-4602, 440), (-4626, 483), (-4576, 483)],
    [(-4386, 437), (-4412, 480), (-4362, 480)],
    [(-4216, 437), (-4242, 480), (-4192, 480)],
    [(-4294, 436), (-4318, 479), (-4268, 479)],
    [(-4496, 441), (-4522, 484), (-4472, 484)],
    [(-4132, 437), (-4158, 480), (-4108, 480)],
    [(-4070, 436), (-4096, 479), (-4046, 479)],
    [(-3998, 440), (-4022, 483), (-3972, 483)],
    [(-3922, 441), (-3946, 484), (-3896, 484)],
    [(-3830, 444), (-3854, 487), (-3804, 487)],
    [(-3748, 440), (-3774, 483), (-3724, 483)],
    [(-3666, 440), (-3692, 483), (-3642, 483)],
    [(-3594, 437), (-3620, 480), (-3570, 480)],
    [(-3516, 441), (-3542, 484), (-3492, 484)],
    [(-3440, 442), (-3466, 485), (-3416, 485)],
    [(-3368, 437), (-3392, 480), (-3342, 480)],
    [(-3296, 441), (-3320, 484), (-3270, 484)],
    [(-3218, 436), (-3244, 479), (-3194, 479)],
    [(-3150, 438), (-3174, 481), (-3124, 481)],
    [(-4550, 986), (-4576, 1029), (-4526, 1029)],
    [(-4608, 986), (-4632, 1029), (-4582, 1029)],
    [(-4658, 984), (-4684, 1027), (-4634, 1027)],
    [(-4664, 447), (-4690, 490), (-4640, 490)],
    [(-4422, 985), (-4446, 1028), (-4396, 1028)],
    [(-4360, 984), (-4386, 1027), (-4336, 1027)],
    [(-4306, 983), (-4330, 1026), (-4280, 1026)],
    [(-4186, 987), (-4212, 1030), (-4162, 1030)],
    [(-4136, 986), (-4160, 1029), (-4110, 1029)],
    [(-4084, 984), (-4110, 1027), (-4060, 1027)],
    [(-3970, 986), (-3994, 1029), (-3944, 1029)],
    [(-3908, 982), (-3932, 1025), (-3882, 1025)],
    [(-3854, 985), (-3878, 1028), (-3828, 1028)],
    [(-3740, 982), (-3766, 1025), (-3716, 1025)],
    [(-3682, 986), (-3708, 1029), (-3658, 1029)],
    [(-3628, 989), (-3652, 1032), (-3602, 1032)],
    [(-3522, 983), (-3546, 1026), (-3496, 1026)],
    [(-3470, 982), (-3494, 1025), (-3444, 1025)],
    [(-3420, 982), (-3446, 1025), (-3396, 1025)],
    [(-3314, 985), (-3338, 1028), (-3288, 1028)],
    [(-3262, 984), (-3288, 1027), (-3238, 1027)],
    [(-3208, 983), (-3234, 1026), (-3184, 1026)],
    [(-6208, 511), (-6234, 554), (-6184, 554)],
    [(-6192, 551), (-6216, 594), (-6166, 594)],
    [(-6160, 592), (-6184, 635), (-6134, 635)],
    [(-6136, 639), (-6162, 682), (-6112, 682)],
    [(-6114, 686), (-6140, 729), (-6090, 729)],
    [(-6090, 729), (-6114, 772), (-6064, 772)],
    [(-6074, 776), (-6100, 819), (-6050, 819)],
    [(-6056, 818), (-6082, 861), (-6032, 861)],
    [(-6044, 866), (-6068, 909), (-6018, 909)],
    [(-6024, 914), (-6050, 957), (-6000, 957)],
    [(-6004, 954), (-6030, 997), (-5980, 997)],
    [(-5984, 996), (-6010, 1039), (-5960, 1039)],
    [(-8530, 698), (-8554, 741), (-8504, 741)],
    [(-8118, 568), (-8142, 611), (-8092, 611)],
    [(-8406, 542), (-8430, 585), (-8380, 585)],
    [(-8198, 574), (-8224, 617), (-8174, 617)],
    [(-8602, 704), (-8628, 747), (-8578, 747)],
    [(-5048, 704), (-5074, 747), (-5024, 747)],
    [(-5148, 803), (-5172, 846), (-5122, 846)],
    [(-5226, 927), (-5252, 970), (-5202, 970)],
    [(-4946, 773), (-4972, 816), (-4922, 816)],
    [(-4790, 377), (-4816, 420), (-4766, 420)],
    [(-4850, 323), (-4876, 366), (-4826, 366)],
    [(-4916, 266), (-4940, 309), (-4890, 309)],
    [(-4974, 222), (-5000, 265), (-4950, 265)],
    [(-9308, 962), (-9334, 1005), (-9284, 1005)],
    [(-9260, 917), (-9286, 960), (-9236, 960)],
    [(-9208, 866), (-9234, 909), (-9184, 909)],
    [(-9164, 809), (-9190, 852), (-9140, 852)],
    [(-9116, 753), (-9142, 796), (-9092, 796)],
    [(-9052, 722), (-9076, 765), (-9026, 765)],
    [(-8996, 762), (-9020, 805), (-8970, 805)],
    [(-8946, 819), (-8972, 862), (-8922, 862)],
    [(-8918, 894), (-8942, 937), (-8892, 937)],
    [(-8876, 967), (-8902, 1010), (-8852, 1010)],
    [(7236, 401), (7210, 444), (7260, 444)],
    [(7368, 396), (7342, 439), (7392, 439)],
    [(7140, 256), (7116, 299), (7166, 299)],
    [(7454, 249), (7428, 292), (7478, 292)],
    [(7302, 402), (7278, 445), (7328, 445)],
    [(8018, 914), (7994, 957), (8044, 957)],
    [(8068, 884), (8042, 927), (8092, 927)],
    [(8102, 835), (8076, 878), (8126, 878)],
    [(8154, 811), (8130, 854), (8180, 854)],
    [(8194, 792), (8170, 835), (8220, 835)],
    [(8238, 764), (8214, 807), (8264, 807)],
    [(8314, 739), (8288, 782), (8338, 782)],
    [(8364, 727), (8338, 770), (8388, 770)],
    [(8420, 691), (8396, 734), (8446, 734)],
    [(8484, 720), (8458, 763), (8508, 763)],
    [(8504, 765), (8480, 808), (8530, 808)],
    [(8536, 797), (8512, 840), (8562, 840)],
    [(8570, 841), (8546, 884), (8596, 884)],
    [(8596, 885), (8570, 928), (8620, 928)],
    [(8618, 924), (8594, 967), (8644, 967)],
    [(8030, 313), (8006, 356), (8056, 356)],
    [(8078, 354), (8052, 397), (8102, 397)],
    [(8130, 394), (8106, 437), (8156, 437)],
    [(8194, 433), (8168, 476), (8218, 476)],
    [(8258, 466), (8234, 509), (8284, 509)],
    [(8334, 493), (8310, 536), (8360, 536)],
    [(8390, 486), (8366, 529), (8416, 529)],
    [(8426, 469), (8400, 512), (8450, 512)],
    [(8466, 432), (8442, 475), (8492, 475)],
    [(8484, 419), (8458, 462), (8508, 462)],
    [(8496, 409), (8472, 452), (8522, 452)],
    [(8518, 391), (8492, 434), (8542, 434)],
    [(8562, 342), (8536, 385), (8586, 385)],
    [(8604, 319), (8580, 362), (8630, 362)],
    [(8664, 348), (8640, 391), (8690, 391)],
    [(8702, 411), (8676, 454), (8726, 454)],
    [(8712, 436), (8688, 479), (8738, 479)],
    [(8750, 477), (8726, 520), (8776, 520)],
    [(8788, 524), (8764, 567), (8814, 567)],
    [(8834, 568), (8808, 611), (8858, 611)],
    [(8886, 602), (8862, 645), (8912, 645)],
    [(8968, 595), (8944, 638), (8994, 638)],
    [(9018, 570), (8994, 613), (9044, 613)],
    [(9044, 549), (9020, 592), (9070, 592)],
    [(9104, 473), (9080, 516), (9130, 516)],
    [(9120, 446), (9096, 489), (9146, 489)],
    [(9166, 387), (9140, 430), (9190, 430)],
    [(9186, 356), (9160, 399), (9210, 399)],
    [(9194, 327), (9168, 370), (9218, 370)],
    [(8684, 932), (8660, 975), (8710, 975)],
    [(8760, 933), (8736, 976), (8786, 976)],
    [(8836, 931), (8812, 974), (8862, 974)],
    [(8948, 929), (8922, 972), (8972, 972)],
    [(9008, 927), (8984, 970), (9034, 970)],
    [(9070, 931), (9044, 974), (9094, 974)],
    [(9120, 929), (9096, 972), (9146, 972)],
    [(9176, 924), (9150, 967), (9200, 967)],
    [(8896, 927), (8870, 970), (8920, 970)],
]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_surface = font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- Checkpoints ---
checkpoints = [
    {"rect": pygame.Rect(-2420.0, 672.0, 49, 51), "collected": False},
    {"rect": pygame.Rect(-2318, 964, 49, 51), "collected": False},
    {"rect": pygame.Rect(-1494, 979, 49, 51), "collected": False},
    {"rect": pygame.Rect(1631, 40, 49, 51), "collected": False},
    {"rect": pygame.Rect(4179, 249, 49, 51), "collected": False},
    {"rect": pygame.Rect(5968, 249, 49, 51), "collected": False},
    {"rect": pygame.Rect(6570, 249, 49, 51), "collected": False},
    {"rect": pygame.Rect(-376, 456, 49, 51), "collected": False},
    {"rect": pygame.Rect(-3000, 979, 49, 51), "collected": False},
    {"rect": pygame.Rect(-4050, 979, 49, 51), "collected": False},
    {"rect": pygame.Rect(-4840, 979, 49, 51), "collected": False},
    {"rect": pygame.Rect(-7360, 315, 49, 51), "collected": False},
    {"rect": pygame.Rect(7928, 972, 49, 51), "collected": False},
]

# --- Precompute spike masks ---
precomputed_spikes = []
for spike in spikes:
    min_x = min(p[0] for p in spike)
    min_y = min(p[1] for p in spike)
    max_x = max(p[0] for p in spike)
    max_y = max(p[1] for p in spike)
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    shifted_spike = [(int(x - min_x), int(y - min_y)) for x, y in spike]
    triangle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(triangle_surface, (255, 0, 0), shifted_spike)
    triangle_mask = pygame.mask.from_surface(triangle_surface)
    precomputed_spikes.append({
        "mask": triangle_mask,
        "offset": (min_x, min_y),
        "rect": pygame.Rect(min_x, min_y, width, height)
    })

def check_collision_with_spikes(player_rect):
    player_surface = pygame.Surface((player_rect.width, player_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, (255, 255, 255), (0, 0, player_rect.width, player_rect.height))
    player_mask = pygame.mask.from_surface(player_surface)
    for spike in precomputed_spikes:
        if player_rect.colliderect(spike["rect"]):
            offset = (int(player_rect.x - spike["offset"][0]), int(player_rect.y - spike["offset"][1]))
            if spike["mask"].overlap(player_mask, offset):
                return True
    return False

def player_deaths():
    state.deaths += 1

def player_reset():
    """Reset player to checkpoint position"""
    print(f"Player Died at: {state.player_pos}")
    state.player_velocity.update(0, 0)
    state.rotation = 0
    state.target_rotation = 0
    state.player_pos.update(state.player_pos_reset.x, state.player_pos_reset.y)
    state.jump_count = 0
    player_deaths()

ground_y = 1030
ground_rects = [pygame.Rect(x, ground_y, 200, 50) for x in range(-state.game_size, state.game_size, 200)]
wall_height = 2000
left_wall = pygame.Rect(-state.game_size, ground_y - wall_height, 500, wall_height)
right_wall = pygame.Rect(state.game_size - 500, ground_y - wall_height, 500, wall_height)

def resolve_collisions(rect, static_platforms, safe_moving_platforms, dt):
    all_platform_rects = []
    all_platform_rects.extend([p.rect for p in safe_moving_platforms if hasattr(p, 'rect')])
    all_platform_rects.extend([p.rect for p in static_platforms if hasattr(p, 'rect')])
    all_platform_rects.extend([p for p in safe_moving_platforms if isinstance(p, pygame.Rect)])
    all_platform_rects.extend([p for p in static_platforms if isinstance(p, pygame.Rect)])
    all_platform_rects.extend(ground_rects)
    all_platform_rects.append(left_wall)
    all_platform_rects.append(right_wall)

    state.on_ground = False
    state.on_wall_left = False
    state.on_wall_right = False
    state.on_wall_bottom = False

    rect.y += state.player_velocity.y * dt

    for plat_rect in all_platform_rects:
        if rect.colliderect(plat_rect):
            if state.player_velocity.y > 0:
                rect.bottom = plat_rect.top
                state.player_velocity.y = 0
                state.on_ground = True
            elif state.player_velocity.y < 0:
                rect.top = plat_rect.bottom
                state.player_velocity.y = 0
                state.on_wall_bottom = True
            if state.on_ground:
                state.jump_count = 0
    
    state.player_pos.y = rect.y

    rect.x += state.player_velocity.x * dt

    for plat_rect in all_platform_rects:
        if rect.colliderect(plat_rect):
            if state.player_velocity.x > 0:
                rect.right = plat_rect.left
                state.player_velocity.x = 0
                state.on_wall_right = True
            elif state.player_velocity.x < 0:
                rect.left = plat_rect.right
                state.player_velocity.x = 0
                state.on_wall_left = True
            if state.on_wall_left or state.on_wall_right:
                state.jump_count = 0

    state.player_pos.x = rect.x

# Main game loop
async def main():
    print("Game starting...")
    
    # Menu buttons
    button_yes_death = Button(screen_width // 2 - 150, screen_height // 2, 100, 50, "Yes", (80, 80, 80), (0, 200, 0))
    button_no_death = Button(screen_width // 2 + 50, screen_height // 2, 100, 50, "No", (80, 80, 80), (200, 0, 0))
    button_yes_speedrun = Button(screen_width // 2 - 150, screen_height // 2, 100, 50, "Yes", (80, 80, 80), (0, 200, 0))
    button_no_speedrun = Button(screen_width // 2 + 50, screen_height // 2, 100, 50, "No", (80, 80, 80), (200, 0, 0))
    
    running = True

    while running:
        dt = clock.tick(60) / 1000
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle menu clicks
            if state.game_phase == "death_screen_prompt":
                if button_yes_death.is_clicked(event):
                    state.death_screen_enable = True
                    state.game_phase = "speedrun_prompt"
                    print("Death screen enabled")
                elif button_no_death.is_clicked(event):
                    state.death_screen_enable = False
                    state.game_phase = "speedrun_prompt"
                    print("Death screen disabled")
                    
            elif state.game_phase == "speedrun_prompt":
                if button_yes_speedrun.is_clicked(event):
                    state.speedrun_mode = True
                    state.game_phase = "rules"
                    print("Speedrun mode enabled")
                elif button_no_speedrun.is_clicked(event):
                    state.speedrun_mode = False
                    state.game_phase = "rules"
                    print("Speedrun mode disabled")
        
        keys = pygame.key.get_pressed()
        
        # ===== RENDER MENU SCREENS =====
        if state.game_phase == "death_screen_prompt":
            screen.fill((30, 30, 30))
            prompt_text = font.render("Enable Death Screen?", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(screen_width // 2, screen_height // 3))
            screen.blit(prompt_text, prompt_rect)
            button_yes_death.draw(screen)
            button_no_death.draw(screen)
            
        elif state.game_phase == "speedrun_prompt":
            screen.fill((30, 30, 30))
            prompt_text = font.render("Enable Speedrun Mode?", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(screen_width // 2, screen_height // 3))
            screen.blit(prompt_text, prompt_rect)
            button_yes_speedrun.draw(screen)
            button_no_speedrun.draw(screen)
            
        elif state.game_phase == "rules":
            screen.fill((0, 0, 0))
            lines = [
                "Welcome to Platform Speedrun!",
                "Press SPACE to start",
                "WASD/Arrows to move, SPACE to jump",
                "R to reset, avoid red spikes!",
                "Collect checkpoints (purple/green)",
                "Reach cyan finish line"
            ]
            for i, line in enumerate(lines):
                text_surf = checkpoint_font.render(line, True, (255, 255, 255))
                screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, 200 + i * 60))
            
            if keys[pygame.K_SPACE]:
                state.game_phase = "playing"
                state.speedrun_start_time = pygame.time.get_ticks()
                print("Game started!")
                
        # ===== GAME LOOP =====
        elif state.game_phase == "playing":
            screen.fill((0, 0, 0))
            
            # Check for special collision zones
            if checkpoints[0]["collected"] or checkpoints[1]["collected"]:
                checkpoints[0]["collected"] = True
                checkpoints[1]["collected"] = True

            if (state.player_pos.x >= 2500 and state.player_pos.x <= 7700) and state.player_pos.y >= 979:
                player_reset()
            
            player_rect = pygame.Rect(int(state.player_pos.x), int(state.player_pos.y), state.player_width, state.player_height)

            # Update platforms
            for mp in moving_platforms:
                mp.update(dt)
            for mp in safe_moving_platforms:
                mp.update(dt)

            # Adjust physics based on position
            if player_rect.x >= 8000:
                state.max_jumps = 1000
                state.gravity = 3000
            else:
                state.max_jumps = 2
                state.gravity = 1500

            # Update moving platform
            if state.plat_move >= 1200:
                state.plat_direction = -1
            elif state.plat_move <= 800:
                state.plat_direction = 1
            state.plat_move += 50 * dt * state.plat_direction
            platforms[3].x = state.plat_move

            # Draw world
            for ground in ground_rects:
                pygame.draw.rect(screen, (255, 255, 255), ground.move(-state.camera_offset))
            pygame.draw.rect(screen, (100, 100, 255), left_wall.move(-state.camera_offset))
            pygame.draw.rect(screen, (100, 100, 255), right_wall.move(-state.camera_offset))

            for plat in platforms:
                pygame.draw.rect(screen, (0, 255, 0), plat.move(-state.camera_offset))

            for mp in moving_platforms:
                pygame.draw.rect(screen, (255, 0, 0), mp.rect.move(-state.camera_offset))

            for mp in safe_moving_platforms:
                pygame.draw.rect(screen, (0, 255, 0), mp.rect.move(-state.camera_offset))

            # Update camera
            state.camera_offset.x = state.player_pos.x - screen.get_width() / 2 + state.player_width / 2
            state.camera_offset.y = state.player_pos.y - screen.get_height() / 2 + state.player_height / 2

            # Physics
            resolve_collisions(player_rect, platforms, safe_moving_platforms, dt)
            if not state.on_wall_left and not state.on_wall_right and not state.on_wall_bottom and not state.on_ground:
                if not state.finish_reached:
                    state.player_velocity.y += state.gravity * dt
            else:
                if state.on_wall_left or state.on_wall_right or state.on_wall_bottom:
                    state.player_velocity.y = 0

            # Check moving platform collision
            for mp in moving_platforms:
                if player_rect.colliderect(mp.rect):
                    player_reset()
                    break

            # Check out of bounds
            if state.player_pos.x > state.game_size or state.player_pos.x < -state.game_size or state.player_pos.y > ground_y + 500:
                player_reset()
            
            # Movement
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                state.player_velocity.x = -state.move_speed
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                state.player_velocity.x = state.move_speed
            else:
                state.player_velocity.x = 0

            # Rotation
            if state.on_wall_left:
                state.target_rotation = -90
            elif state.on_wall_right:
                state.target_rotation = 90
            else:
                state.target_rotation = 0
            state.rotation += (state.target_rotation - state.rotation) * min(10 * dt, 1)

            # Jump
            jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
            if jump_pressed and current_time - state.last_jump_time >= state.jump_cooldown and state.jump_count < state.max_jumps:
                state.player_velocity.y = -state.jump_strength
                state.jump_count += 1
                state.last_jump_time = current_time
            
            # Reset
            if keys[pygame.K_r]:
                player_reset()

            # Draw spikes
            for spike in spikes:
                spike_screen = [(int(x - state.camera_offset.x), int(y - state.camera_offset.y)) for x, y in spike]
                pygame.draw.polygon(screen, (255, 0, 0), spike_screen)

            # Draw player
            rotated_player = pygame.Surface((state.player_width, state.player_height), pygame.SRCALPHA)
            rotated_player.fill((255, 0, 0))
            pygame.draw.rect(rotated_player, (255, 255, 255), (0, 0, state.player_width, 10))
            rotated_player = pygame.transform.rotate(rotated_player, -state.rotation)
            rect = rotated_player.get_rect(center=player_rect.move(-state.camera_offset).center)
            screen.blit(rotated_player, rect)

            # Check spike collision
            if check_collision_with_spikes(player_rect):
                player_reset()

            # Check checkpoints
            for cp in checkpoints:
                if not cp["collected"] and player_rect.colliderect(cp["rect"]):
                    cp["collected"] = True
                    state.player_pos_reset.update(cp["rect"].x, cp["rect"].y)
                    print(f"Checkpoint reached!")

            # Draw checkpoints
            for cp in checkpoints:
                color = (0, 255, 0) if cp["collected"] else (150, 50, 220)
                pygame.draw.rect(screen, color, cp["rect"].move(-state.camera_offset), 3)

            # Draw finish line
            pygame.draw.rect(screen, (0, 255, 255), finish_rect.move(-state.camera_offset))

            # Check finish
            if player_rect.colliderect(finish_rect) and not state.finish_reached and (all(cp["collected"] for cp in checkpoints) or state.speedrun_mode):
                state.finish_reached = True
                state.finish_time = pygame.time.get_ticks() - state.speedrun_start_time
                state.game_phase = "finished"
                print(f"FINISH! Time: {state.finish_time/1000:.2f}s, Deaths: {state.deaths}")

            # Draw UI
            cp_text = checkpoint_font.render(f"Checkpoints: {sum(cp['collected'] for cp in checkpoints)}/{len(checkpoints)}", True, (255, 255, 0))
            screen.blit(cp_text, (10, 10))

            fps = clock.get_fps()
            fps_text = fps_font.render(f"FPS: {int(fps)}", True, (255, 255, 0))
            screen.blit(fps_text, (10, 50))

            speedrun_time = (pygame.time.get_ticks() - state.speedrun_start_time) / 1000
            speed_text = checkpoint_font.render(f"Time: {speedrun_time:.2f}s", True, (255, 255, 0))
            screen.blit(speed_text, (10, 90))

            death_counter = checkpoint_font.render(f"Deaths: {state.deaths}", True, (255, 255, 0))
            screen.blit(death_counter, (10, 130))
            
        elif state.game_phase == "finished":
            screen.fill((0, 0, 0))
            minutes = state.finish_time // 60000
            seconds = (state.finish_time % 60000) // 1000
            milliseconds = (state.finish_time % 1000) // 10
            
            finish_text = font.render(
                f"FINISH! Time: {minutes:02}:{seconds:02}.{milliseconds:02}",
                True,
                (0, 255, 255)
            )
            screen.blit(finish_text, (
                screen.get_width() / 2 - finish_text.get_width() / 2,
                screen.get_height() / 2 - 50
            ))
            
            deaths_text = checkpoint_font.render(f"Deaths: {state.deaths}", True, (255, 255, 255))
            screen.blit(deaths_text, (
                screen.get_width() / 2 - deaths_text.get_width() / 2,
                screen.get_height() / 2 + 50
            ))

        pygame.display.flip()
        await asyncio.sleep(0)  # Critical for Pygbag!

    pygame.quit()

# Run the game
asyncio.run(main())