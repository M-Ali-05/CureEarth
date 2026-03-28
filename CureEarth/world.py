import random
import math
import pygame
from continent import Continent


class World:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty

        self.spread_multiplier = {
            "easy": 0.65,
            "normal": 1.0,
            "hard": 1.18
        }[difficulty]

        self.crisis_threshold = {
            "easy": 82,
            "normal": 70,
            "hard": 65
        }[difficulty]

        self.growth_multiplier = {
            "easy": 0.72,
            "normal": 1.0,
            "hard": 1.18
        }[difficulty]

        self.base_map_width = 1000
        self.base_map_height = 620

        self.base_continent_data = self.create_base_continent_data()
        self.base_air_routes = [
            ("North America", "Europe"),
            ("North America", "South America"),
            ("Europe", "Africa"),
            ("Europe", "Asia"),
            ("Africa", "Asia"),
            ("Asia", "Australia"),
        ]
        self.base_sea_routes = [
            ("North America", "South America"),
            ("Europe", "Africa"),
            ("Africa", "Asia"),
            ("Asia", "Australia"),
        ]

        self.continents = []
        self.air_routes = []
        self.sea_routes = []

        self.planes = []
        self.ships = []
        self.last_layout_signature = None

    def create_base_continent_data(self):
        return [
            {
                "name": "North America",
                "points": [
                    (60, 120), (110, 95), (180, 88), (260, 104), (302, 128),
                    (294, 194), (228, 208), (150, 220), (96, 202), (60, 174)
                ],
                "center": (180, 158),
                "cities": [("USA", (178, 152)), ("Canada", (152, 128)), ("Mexico", (192, 188))],
                "stats": dict(infection=15, ecology=72, economy=88, panic=20, medical=74, trust=60)
            },
            {
                "name": "South America",
                "points": [
                    (165, 290), (220, 305), (240, 390), (228, 470),
                    (210, 548), (170, 595), (142, 505), (136, 430), (145, 350)
                ],
                "center": (188, 440),
                "cities": [("Brazil", (188, 408)), ("Argentina", (178, 510))],
                "stats": dict(infection=8, ecology=84, economy=56, panic=16, medical=46, trust=63)
            },
            {
                "name": "Europe",
                "points": [
                    (410, 110), (462, 96), (522, 112), (560, 136),
                    (535, 178), (470, 174), (425, 160)
                ],
                "center": (485, 140),
                "cities": [("Germany", (482, 138)), ("France", (455, 152)), ("UK", (468, 122))],
                "stats": dict(infection=12, ecology=78, economy=82, panic=15, medical=82, trust=70)
            },
            {
                "name": "Africa",
                "points": [
                    (395, 220), (462, 214), (520, 224), (542, 312),
                    (520, 402), (490, 502), (432, 468), (388, 418), (366, 322)
                ],
                "center": (455, 344),
                "cities": [("Egypt", (448, 274)), ("Nigeria", (430, 366)), ("South Africa", (450, 456))],
                "stats": dict(infection=10, ecology=68, economy=40, panic=21, medical=38, trust=57)
            },
            {
                "name": "Asia",
                "points": [
                    (585, 88), (720, 82), (812, 86), (880, 144),
                    (864, 236), (838, 314), (720, 332), (642, 272),
                    (582, 210), (575, 150)
                ],
                "center": (724, 182),
                "cities": [("China", (712, 178)), ("India", (688, 210)), ("Japan", (760, 176))],
                "stats": dict(infection=22, ecology=58, economy=86, panic=25, medical=62, trust=56)
            },
            {
                "name": "Australia",
                "points": [
                    (708, 432), (804, 426), (850, 492), (818, 560),
                    (742, 546), (684, 482)
                ],
                "center": (768, 492),
                "cities": [("Australia", (768, 486)), ("NZ", (810, 500))],
                "stats": dict(infection=6, ecology=76, economy=62, panic=11, medical=68, trust=72)
            },
        ]

    def get_map_area(self, screen_width, screen_height):
        margin = 12
        top_h = 112
        bottom_h = 88
        right_w = 390
        return pygame.Rect(
            margin,
            top_h + 18,
            screen_width - right_w - margin * 3,
            screen_height - top_h - bottom_h - 38
        )

    def scale_point(self, point, map_rect, scale, offset_x, offset_y):
        px, py = point
        x = map_rect.x + offset_x + px * scale
        y = map_rect.y + offset_y + py * scale
        return int(x), int(y)

    def rebuild_layout_if_needed(self, screen_width, screen_height):
        signature = (screen_width, screen_height)
        if self.last_layout_signature == signature:
            return

        self.last_layout_signature = signature

        map_rect = self.get_map_area(screen_width, screen_height)

        scale_x = map_rect.width / self.base_map_width
        scale_y = map_rect.height / self.base_map_height
        scale = min(scale_x, scale_y) * 0.92

        content_w = self.base_map_width * scale
        content_h = self.base_map_height * scale

        offset_x = (map_rect.width - content_w) / 2
        offset_y = (map_rect.height - content_h) / 2

        old_state = {}
        for c in self.continents:
            old_state[c.name] = {
                "infection": c.infection,
                "ecology": c.ecology,
                "economy": c.economy,
                "panic": c.panic,
                "medical": c.medical,
                "trust": c.trust,
                "air_open": c.air_open,
                "sea_open": c.sea_open,
                "selected": c.selected,
                "crisis": c.crisis,
                "active_effects": [dict(e) for e in c.active_effects],
            }

        self.continents = []
        for data in self.base_continent_data:
            scaled_points = [
                self.scale_point(p, map_rect, scale, offset_x, offset_y)
                for p in data["points"]
            ]
            scaled_center = self.scale_point(data["center"], map_rect, scale, offset_x, offset_y)

            scaled_cities = []
            for city_name, city_pos in data["cities"]:
                scaled_cities.append({
                    "name": city_name,
                    "pos": self.scale_point(city_pos, map_rect, scale, offset_x, offset_y)
                })

            stats = data["stats"]
            continent = Continent(
                data["name"],
                scaled_points,
                scaled_center,
                infection=stats["infection"],
                ecology=stats["ecology"],
                economy=stats["economy"],
                panic=stats["panic"],
                medical=stats["medical"],
                trust=stats["trust"],
                crisis_threshold=self.crisis_threshold,
                growth_multiplier=self.growth_multiplier,
                cities=scaled_cities
            )

            if data["name"] in old_state:
                s = old_state[data["name"]]
                continent.infection = s["infection"]
                continent.ecology = s["ecology"]
                continent.economy = s["economy"]
                continent.panic = s["panic"]
                continent.medical = s["medical"]
                continent.trust = s["trust"]
                continent.air_open = s["air_open"]
                continent.sea_open = s["sea_open"]
                continent.selected = s["selected"]
                continent.crisis = s["crisis"]
                continent.active_effects = s["active_effects"]

            self.continents.append(continent)

        self.air_routes = self.base_air_routes[:]
        self.sea_routes = self.base_sea_routes[:]

    def ensure_layout(self, screen):
        self.rebuild_layout_if_needed(screen.get_width(), screen.get_height())

    def get_continent_by_name(self, name):
        for continent in self.continents:
            if continent.name == name:
                return continent
        return None

    def get_clicked_continent(self, pos):
        for continent in self.continents:
            if continent.contains_point(pos):
                return continent
        return None

    def apply_global_project(self, project_type):
        if project_type == "global_vaccine":
            for c in self.continents:
                c.add_effect("global_vaccine", 8, 1.2)
        elif project_type == "global_climate":
            for c in self.continents:
                c.add_effect("global_climate", 6, 1.4)
        elif project_type == "global_info":
            for c in self.continents:
                c.add_effect("global_info", 5, 2.4)

    def draw_routes(self, screen):
        for a_name, b_name in self.air_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if a and b:
                pygame.draw.line(screen, (175, 190, 235), a.center, b.center, 2)

        for a_name, b_name in self.sea_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if a and b:
                pygame.draw.line(screen, (70, 155, 235), a.center, b.center, 2)

    def spawn_planes(self):
        for a_name, b_name in self.air_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if a and b and a.air_open and b.air_open:
                chance = 0.015 * self.spread_multiplier
                if a.crisis or b.crisis:
                    chance += 0.012 * self.spread_multiplier
                if random.random() < chance:
                    self.planes.append({"from": a.center, "to": b.center, "progress": 0.0})

    def update_planes(self):
        for plane in self.planes:
            plane["progress"] += 0.015
        self.planes = [p for p in self.planes if p["progress"] < 1.0]

    def draw_plane_icon(self, screen, x, y, angle):
        size = 8
        pts = [
            (x + math.cos(angle) * size, y + math.sin(angle) * size),
            (x + math.cos(angle + 2.5) * size * 0.7, y + math.sin(angle + 2.5) * size * 0.7),
            (x + math.cos(angle + math.pi) * size * 0.4, y + math.sin(angle + math.pi) * size * 0.4),
            (x + math.cos(angle - 2.5) * size * 0.7, y + math.sin(angle - 2.5) * size * 0.7),
        ]
        pygame.draw.polygon(screen, (245, 245, 255), pts)
        pygame.draw.polygon(screen, (120, 150, 210), pts, 1)

    def draw_planes(self, screen):
        for plane in self.planes:
            x1, y1 = plane["from"]
            x2, y2 = plane["to"]
            p = plane["progress"]
            x = x1 + (x2 - x1) * p
            y = y1 + (y2 - y1) * p
            angle = math.atan2(y2 - y1, x2 - x1)
            self.draw_plane_icon(screen, x, y, angle)

    def spawn_ships(self):
        for a_name, b_name in self.sea_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if a and b and a.sea_open and b.sea_open:
                chance = 0.010 * self.spread_multiplier
                if a.crisis or b.crisis:
                    chance += 0.008 * self.spread_multiplier
                if random.random() < chance:
                    self.ships.append({"from": a.center, "to": b.center, "progress": 0.0})

    def update_ships(self):
        for ship in self.ships:
            ship["progress"] += 0.009
        self.ships = [s for s in self.ships if s["progress"] < 1.0]

    def draw_ship_icon(self, screen, x, y, angle):
        size = 7
        pts = [
            (x + math.cos(angle) * size, y + math.sin(angle) * size),
            (x + math.cos(angle + 2.2) * size * 0.8, y + math.sin(angle + 2.2) * size * 0.8),
            (x + math.cos(angle + math.pi) * size * 0.6, y + math.sin(angle + math.pi) * size * 0.6),
            (x + math.cos(angle - 2.2) * size * 0.8, y + math.sin(angle - 2.2) * size * 0.8),
        ]
        pygame.draw.polygon(screen, (100, 220, 255), pts)
        pygame.draw.polygon(screen, (40, 120, 200), pts, 1)

    def draw_ships(self, screen):
        for ship in self.ships:
            x1, y1 = ship["from"]
            x2, y2 = ship["to"]
            p = ship["progress"]
            x = x1 + (x2 - x1) * p
            y = y1 + (y2 - y1) * p
            angle = math.atan2(y2 - y1, x2 - x1)
            self.draw_ship_icon(screen, x, y, angle)

    def spread_by_air(self):
        for a_name, b_name in self.air_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if not a or not b:
                continue

            spread_chance = (a.infection / 100.0) * 0.26 * self.spread_multiplier
            if a.crisis:
                spread_chance += 0.12 * self.spread_multiplier
            if not a.air_open or not b.air_open:
                spread_chance *= 0.18

            if random.random() < spread_chance * 0.08:
                b.infection += random.uniform(1.8, 4.5)
                b.panic += 2.5

            reverse_chance = (b.infection / 100.0) * 0.26 * self.spread_multiplier
            if b.crisis:
                reverse_chance += 0.12 * self.spread_multiplier
            if not a.air_open or not b.air_open:
                reverse_chance *= 0.18

            if random.random() < reverse_chance * 0.08:
                a.infection += random.uniform(1.8, 4.5)
                a.panic += 2.5

    def spread_by_sea(self):
        for a_name, b_name in self.sea_routes:
            a = self.get_continent_by_name(a_name)
            b = self.get_continent_by_name(b_name)
            if not a or not b:
                continue

            spread_chance = (a.infection / 100.0) * 0.13 * self.spread_multiplier
            if a.crisis:
                spread_chance += 0.06 * self.spread_multiplier
            if not a.sea_open or not b.sea_open:
                spread_chance *= 0.28

            if random.random() < spread_chance * 0.09:
                b.infection += random.uniform(1.0, 2.8)
                b.panic += 1.4

            reverse_chance = (b.infection / 100.0) * 0.13 * self.spread_multiplier
            if b.crisis:
                reverse_chance += 0.06 * self.spread_multiplier
            if not a.sea_open or not b.sea_open:
                reverse_chance *= 0.28

            if random.random() < reverse_chance * 0.09:
                a.infection += random.uniform(1.0, 2.8)
                a.panic += 1.4

    def update(self):
        for c in self.continents:
            c.update_internal()

        self.spread_by_air()
        self.spread_by_sea()

        self.spawn_planes()
        self.update_planes()

        self.spawn_ships()
        self.update_ships()

        for c in self.continents:
            c.clamp_stats()

    def draw(self, screen, font):
        self.ensure_layout(screen)
        self.draw_routes(screen)
        for c in self.continents:
            c.draw(screen, font)
        self.draw_planes(screen)
        self.draw_ships(screen)

    def total_infection(self):
        return sum(c.infection for c in self.continents) / len(self.continents)

    def total_ecology(self):
        return sum(c.ecology for c in self.continents) / len(self.continents)

    def total_economy(self):
        return sum(c.economy for c in self.continents) / len(self.continents)

    def total_panic(self):
        return sum(c.panic for c in self.continents) / len(self.continents)

    def total_medical(self):
        return sum(c.medical for c in self.continents) / len(self.continents)

    def total_trust(self):
        return sum(c.trust for c in self.continents) / len(self.continents)

    def crisis_count(self):
        return sum(1 for c in self.continents if c.crisis)