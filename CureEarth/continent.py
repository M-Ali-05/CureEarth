import pygame


class Continent:
    def __init__(
        self,
        name,
        points,
        center,
        infection=10,
        ecology=80,
        economy=70,
        panic=15,
        medical=50,
        trust=60,
        crisis_threshold=70,
        growth_multiplier=1.0,
        cities=None
    ):
        self.name = name
        self.points = points
        self.center = center

        self.infection = float(infection)
        self.ecology = float(ecology)
        self.economy = float(economy)
        self.panic = float(panic)
        self.medical = float(medical)
        self.trust = float(trust)

        self.air_open = True
        self.sea_open = True

        self.selected = False
        self.crisis = False
        self.crisis_threshold = crisis_threshold
        self.growth_multiplier = growth_multiplier

        self.active_effects = []
        self.cities = cities or []

    def clamp_stats(self):
        self.infection = max(0, min(100, self.infection))
        self.ecology = max(0, min(100, self.ecology))
        self.economy = max(0, min(100, self.economy))
        self.panic = max(0, min(100, self.panic))
        self.medical = max(0, min(100, self.medical))
        self.trust = max(0, min(100, self.trust))

    def get_base_color(self):
        infection_ratio = self.infection / 100.0
        ecology_ratio = self.ecology / 100.0

        red = int(45 + infection_ratio * 200)
        green = int(95 + ecology_ratio * 95 - infection_ratio * 85)
        blue = int(95 + ecology_ratio * 35)

        return (
            max(0, min(255, red)),
            max(0, min(255, green)),
            max(0, min(255, blue)),
        )

    def get_light_color(self, color):
        r, g, b = color
        return min(255, r + 25), min(255, g + 25), min(255, b + 25)

    def get_dark_border_color(self, color):
        r, g, b = color
        return max(0, r - 35), max(0, g - 35), max(0, b - 35)

    def draw_glow_polygon(self, screen, color, width):
        temp = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(temp, (*color, 65), self.points, width)
        screen.blit(temp, (0, 0))

    def draw_infection_markers(self, screen):
        if self.infection < 20:
            count = 1
        elif self.infection < 40:
            count = 2
        elif self.infection < 60:
            count = 3
        elif self.infection < 80:
            count = 4
        else:
            count = 5

        cx, cy = self.center
        offsets = [(-14, 14), (14, 12), (-18, -10), (16, -12), (0, 20)]

        for i in range(count):
            ox, oy = offsets[i]
            if self.infection < 30:
                color = (255, 210, 120)
            elif self.infection < 60:
                color = (255, 150, 110)
            else:
                color = (255, 90, 90)
            pygame.draw.circle(screen, color, (int(cx + ox), int(cy + oy)), 4)

    def draw_cities(self, screen, font):
        city_color = (245, 245, 255)
        city_label_color = (200, 220, 245)

        for city in self.cities:
            name = city["name"]
            x, y = city["pos"]

            pygame.draw.circle(screen, city_color, (int(x), int(y)), 3)

            if self.selected:
                label = font.render(name, True, city_label_color)
                screen.blit(label, (x + 6, y - 10))

    def draw_label(self, screen, font):
        label_y_shift = -22
        if self.name == "Europe":
            label_y_shift = -18
        elif self.name == "Australia":
            label_y_shift = -16
        elif self.name == "South America":
            label_y_shift = -12

        text = font.render(self.name, True, (242, 247, 255))
        shadow = font.render(self.name, True, (20, 28, 40))

        rect = text.get_rect(center=(self.center[0], self.center[1] + label_y_shift))
        shadow_rect = shadow.get_rect(center=(self.center[0] + 1, self.center[1] + label_y_shift + 1))

        screen.blit(shadow, shadow_rect)
        screen.blit(text, rect)

    def draw(self, screen, font):
        base_color = self.get_base_color()
        light_color = self.get_light_color(base_color)
        border_color = self.get_dark_border_color(base_color)

        if self.selected:
            self.draw_glow_polygon(screen, (255, 255, 255), 10)

        if self.crisis:
            self.draw_glow_polygon(screen, (255, 80, 80), 12)

        pygame.draw.polygon(screen, base_color, self.points)
        pygame.draw.polygon(screen, light_color, self.points, 2)

        if self.selected:
            pygame.draw.polygon(screen, (255, 255, 255), self.points, 4)
        elif self.crisis:
            pygame.draw.polygon(screen, (255, 90, 90), self.points, 3)
        else:
            pygame.draw.polygon(screen, border_color, self.points, 2)

        if self.selected:
            pygame.draw.circle(screen, (255, 255, 255), self.center, 5)

        self.draw_infection_markers(screen)
        self.draw_cities(screen, font)
        self.draw_label(screen, font)

    def contains_point(self, pos):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        rect = pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        return rect.collidepoint(pos)

    def add_effect(self, effect_type, days, power):
        self.active_effects.append({"type": effect_type, "days": days, "power": power})

    def vaccinate(self):
        self.add_effect("vaccination", 5, 4.2)

    def improve_ecology(self):
        self.add_effect("eco", 6, 3.5)

    def quarantine(self):
        self.add_effect("quarantine", 4, 0)

    def invest_medical(self):
        self.add_effect("medical_invest", 5, 2.8)

    def support_campaign(self):
        self.add_effect("support", 5, 3.2)

    def close_air(self):
        self.air_open = False

    def open_air(self):
        self.air_open = True

    def close_sea(self):
        self.sea_open = False

    def open_sea(self):
        self.sea_open = True

    def apply_effects(self):
        for effect in self.active_effects[:]:
            effect_type = effect["type"]
            power = effect["power"]

            if effect_type == "vaccination":
                trust_modifier = 0.45 + (self.trust / 100.0)
                medical_modifier = 0.45 + (self.medical / 100.0)
                self.infection -= power * 0.75 * trust_modifier * medical_modifier
                self.panic -= 0.35

            elif effect_type == "eco":
                self.ecology += power
                self.panic -= 0.2

            elif effect_type == "quarantine":
                self.infection -= 2.0
                self.economy -= 2.2
                self.panic += 1.6
                self.trust -= 0.5

            elif effect_type == "medical_invest":
                self.medical += power
                self.economy -= 0.9

            elif effect_type == "support":
                self.trust += power
                self.panic -= 1.8

            elif effect_type == "global_vaccine":
                self.medical += power
                self.infection -= 0.9

            elif effect_type == "global_climate":
                self.ecology += power
                self.panic -= 0.2

            elif effect_type == "global_info":
                self.trust += power
                self.panic -= power * 0.7

            effect["days"] -= 1
            if effect["days"] <= 0:
                self.active_effects.remove(effect)

    def update_internal(self):
        self.apply_effects()

        base_growth = 0.55
        eco_factor = (100 - self.ecology) * 0.032
        panic_factor = self.panic * 0.025
        medical_factor = self.medical * 0.026
        trust_factor = self.trust * 0.015

        phase_bonus = 0.0
        if self.infection >= 20:
            phase_bonus += 0.7
        if self.infection >= 50:
            phase_bonus += (self.infection - 50) * 0.05
        if self.infection >= 70:
            phase_bonus += (self.infection - 70) * 0.08

        growth = base_growth + eco_factor + panic_factor + phase_bonus - medical_factor - trust_factor
        growth = max(0.12, growth)
        growth *= self.growth_multiplier

        quarantine_active = any(e["type"] == "quarantine" for e in self.active_effects)
        if quarantine_active:
            growth *= 0.52

        self.infection += growth
        self.crisis = self.infection >= self.crisis_threshold

        if self.infection > 40:
            self.ecology -= (0.35 + (self.infection - 40) * 0.032) * self.growth_multiplier

        economic_loss = 0.08 + self.infection * 0.021
        if not self.air_open:
            economic_loss += 1.4
        if not self.sea_open:
            economic_loss += 0.9
        if self.crisis:
            economic_loss += 1.8
        economic_loss *= 0.9 + self.growth_multiplier * 0.1
        self.economy -= economic_loss

        panic_gain = 0.18 + self.infection * 0.016
        if self.crisis:
            panic_gain += 1.6
        panic_gain *= 0.9 + self.growth_multiplier * 0.1
        self.panic += panic_gain

        trust_loss = 0.0
        if self.panic > 50:
            trust_loss += 0.6
        if self.economy < 40:
            trust_loss += 0.55
        self.trust -= trust_loss

        if self.economy > 65 and self.panic < 35:
            self.trust += 0.22

        self.clamp_stats()