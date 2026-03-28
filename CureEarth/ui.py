import pygame


def draw_rounded_panel(screen, rect, fill_color, border_color, radius=16, border_width=2):
    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=radius)


class Button:
    def __init__(self, x, y, w, h, text, action, bg_color=(40, 60, 90), border_color=(90, 130, 190)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.bg_color = bg_color
        self.border_color = border_color

    def draw(self, screen, font):
        shadow_rect = self.rect.move(0, 3)
        pygame.draw.rect(screen, (8, 12, 20), shadow_rect, border_radius=10)
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=10)

        label = font.render(self.text, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class UI:
    def __init__(self):
        self.buttons = []
        self.restart_button = None
        self.diff_buttons = []

    def build_layout(self, width, height):
        margin = 12
        top_h = 112
        right_w = 390
        bottom_h = 88

        self.top_rect = pygame.Rect(margin, 10, width - margin * 2, top_h)
        self.map_rect = pygame.Rect(
            margin,
            top_h + 18,
            width - right_w - margin * 3,
            height - top_h - bottom_h - 38
        )
        self.news_rect = pygame.Rect(
            margin,
            height - bottom_h - 12,
            width - right_w - margin * 3,
            bottom_h
        )
        self.side_rect = pygame.Rect(width - right_w - margin, 10, right_w, height - 20)

        sx = self.side_rect.x + 16
        full_w = self.side_rect.width - 32
        half_w = (full_w - 10) // 2

        # Компактная правая панель
        region_info_top = self.side_rect.y + 64
        region_info_h = 210

        local_actions_top = region_info_top + region_info_h + 38
        btn_h = 34
        gap = 6

        transport_top = local_actions_top + 5 * (btn_h + gap) + 16
        global_top = transport_top + 2 * (btn_h + gap) + 42

        self.region_info_rect = pygame.Rect(sx, region_info_top, full_w, region_info_h)

        self.buttons = [
            Button(sx, local_actions_top, full_w, btn_h, "Vaccinate (-100)", "vaccinate",
                   (36, 78, 140), (90, 170, 255)),
            Button(sx, local_actions_top + 1 * (btn_h + gap), full_w, btn_h, "Eco Program (-80)", "eco",
                   (35, 110, 72), (90, 220, 150)),
            Button(sx, local_actions_top + 2 * (btn_h + gap), full_w, btn_h, "Quarantine (-65)", "quarantine",
                   (150, 85, 55), (255, 180, 120)),
            Button(sx, local_actions_top + 3 * (btn_h + gap), full_w, btn_h, "Medical Invest (-95)", "medical_invest",
                   (70, 70, 150), (150, 150, 255)),
            Button(sx, local_actions_top + 4 * (btn_h + gap), full_w, btn_h, "Support Campaign (-60)", "support",
                   (80, 120, 70), (170, 240, 140)),

            Button(sx, transport_top, half_w, btn_h, "Close Air (-20)", "close_air",
                   (130, 85, 35), (255, 180, 80)),
            Button(sx + half_w + 10, transport_top, half_w, btn_h, "Open Air", "open_air",
                   (55, 80, 110), (120, 170, 220)),
            Button(sx, transport_top + btn_h + gap, half_w, btn_h, "Close Sea (-15)", "close_sea",
                   (130, 85, 35), (255, 180, 80)),
            Button(sx + half_w + 10, transport_top + btn_h + gap, half_w, btn_h, "Open Sea", "open_sea",
                   (55, 80, 110), (120, 170, 220)),

            Button(sx, global_top, full_w, btn_h, "Global Vaccine (-180 / -220S)", "global_vaccine",
                   (52, 88, 150), (120, 190, 255)),
            Button(sx, global_top + 1 * (btn_h + gap), full_w, btn_h, "Climate Recovery (-170 / -120S)", "global_climate",
                   (40, 115, 75), (120, 230, 160)),
            Button(sx, global_top + 2 * (btn_h + gap), full_w, btn_h, "Global Info (-140 / -90S)", "global_info",
                   (100, 90, 55), (230, 210, 120)),
        ]

        self.restart_button = Button(
            width // 2 - 130, height // 2 + 145, 260, 56,
            "Restart Game", "restart",
            (50, 100, 170), (120, 190, 255)
        )

        self.diff_buttons = [
            Button(width // 2 - 210, height // 2 - 5, 120, 48, "Easy", "diff_easy",
                   (45, 120, 75), (120, 240, 170)),
            Button(width // 2 - 60, height // 2 - 5, 120, 48, "Normal", "diff_normal",
                   (55, 85, 130), (130, 190, 255)),
            Button(width // 2 + 90, height // 2 - 5, 120, 48, "Hard", "diff_hard",
                   (140, 70, 60), (255, 160, 150)),
        ]

    def draw_stat_card(self, screen, font, rect, title, value, value_color):
        shadow_rect = rect.move(0, 3)
        pygame.draw.rect(screen, (8, 12, 20), shadow_rect, border_radius=12)
        draw_rounded_panel(screen, rect, (22, 32, 48), (70, 95, 130), radius=12)

        title_surf = font.render(title, True, (155, 175, 205))
        value_surf = font.render(value, True, value_color)

        screen.blit(title_surf, (rect.x + 10, rect.y + 6))
        screen.blit(value_surf, (rect.x + 10, rect.y + 27))

    def draw_top_bar(self, screen, font, money, science, day, score, world, difficulty):
        width = screen.get_width()
        height = screen.get_height()
        self.build_layout(width, height)

        draw_rounded_panel(screen, self.top_rect, (18, 28, 44), (70, 95, 130), radius=18)

        card_w = 158
        card_h = 42
        gap = 8
        start_x = self.top_rect.x + 12
        row1_y = self.top_rect.y + 8
        row2_y = self.top_rect.y + 56

        row1 = [
            ("Money", str(money), (255, 220, 120)),
            ("Science", str(science), (120, 200, 255)),
            ("Day", str(day), (235, 235, 255)),
            ("Score", str(score), (180, 255, 160)),
            ("Difficulty", difficulty.title(), (255, 210, 150)),
            ("Crises", str(world.crisis_count()), (255, 130, 130)),
        ]

        row2 = [
            ("Infection", f"{world.total_infection():.1f}%", (255, 110, 110)),
            ("Ecology", f"{world.total_ecology():.1f}%", (110, 255, 150)),
            ("Economy", f"{world.total_economy():.1f}%", (255, 205, 120)),
            ("Panic", f"{world.total_panic():.1f}%", (255, 160, 120)),
            ("Medical", f"{world.total_medical():.1f}%", (150, 210, 255)),
            ("Trust", f"{world.total_trust():.1f}%", (180, 240, 180)),
        ]

        x = start_x
        for title, value, color in row1:
            rect = pygame.Rect(x, row1_y, card_w, card_h)
            self.draw_stat_card(screen, font, rect, title, value, color)
            x += card_w + gap

        x = start_x
        for title, value, color in row2:
            rect = pygame.Rect(x, row2_y, card_w, card_h)
            self.draw_stat_card(screen, font, rect, title, value, color)
            x += card_w + gap

    def draw_side_panel(self, screen, title_font, text_font, selected_continent):
        width = screen.get_width()
        height = screen.get_height()
        self.build_layout(width, height)

        draw_rounded_panel(screen, self.side_rect, (18, 28, 44), (70, 95, 130), radius=20)

        sx = self.side_rect.x + 16
        sy = self.side_rect.y + 14

        title = title_font.render("Region Control", True, (245, 248, 255))
        screen.blit(title, (sx, sy))

        draw_rounded_panel(screen, self.region_info_rect, (24, 36, 56), (75, 105, 145), radius=16)

        if selected_continent is None:
            msg = text_font.render("Select a continent on the map", True, (170, 190, 210))
            screen.blit(msg, (sx + 12, self.region_info_rect.y + 18))
        else:
            name_surf = title_font.render(selected_continent.name, True, (255, 255, 255))
            screen.blit(name_surf, (sx + 14, self.region_info_rect.y + 12))

            crisis_text = "YES" if selected_continent.crisis else "NO"
            crisis_color = (255, 100, 100) if selected_continent.crisis else (120, 255, 160)

            lines = [
                ("Infection", f"{selected_continent.infection:.1f}%", (255, 110, 110)),
                ("Ecology", f"{selected_continent.ecology:.1f}%", (110, 255, 150)),
                ("Economy", f"{selected_continent.economy:.1f}%", (255, 210, 130)),
                ("Panic", f"{selected_continent.panic:.1f}%", (255, 170, 120)),
                ("Medical", f"{selected_continent.medical:.1f}%", (150, 210, 255)),
                ("Trust", f"{selected_continent.trust:.1f}%", (180, 240, 180)),
                ("Crisis", crisis_text, crisis_color),
                ("Air", "Open" if selected_continent.air_open else "Closed",
                 (150, 220, 255) if selected_continent.air_open else (255, 190, 90)),
                ("Sea", "Open" if selected_continent.sea_open else "Closed",
                 (150, 220, 255) if selected_continent.sea_open else (255, 190, 90)),
            ]

            y = self.region_info_rect.y + 54
            for label, value, color in lines:
                label_surf = text_font.render(f"{label}:", True, (170, 190, 215))
                value_surf = text_font.render(value, True, color)
                screen.blit(label_surf, (sx + 14, y))
                screen.blit(value_surf, (sx + 165, y))
                y += 18

        local_title = title_font.render("Local Actions", True, (245, 248, 255))
        screen.blit(local_title, (sx, self.region_info_rect.bottom + 10))

        transport_y = self.buttons[5].rect.y - 20
        transport_title = text_font.render("Transport", True, (155, 175, 205))
        screen.blit(transport_title, (sx, transport_y))

        global_y = self.buttons[9].rect.y - 22
        global_title = title_font.render("Global Projects", True, (245, 248, 255))
        screen.blit(global_title, (sx, global_y))

        for button in self.buttons:
            button.draw(screen, text_font)

    def draw_event_box(self, screen, title_font, text_font, event_text):
        width = screen.get_width()
        height = screen.get_height()
        self.build_layout(width, height)

        shadow_rect = self.news_rect.move(0, 3)
        pygame.draw.rect(screen, (8, 12, 20), shadow_rect, border_radius=16)
        draw_rounded_panel(screen, self.news_rect, (18, 28, 44), (70, 95, 130), radius=16)

        title = title_font.render("Global News", True, (245, 248, 255))
        screen.blit(title, (self.news_rect.x + 16, self.news_rect.y + 10))

        if not event_text:
            event_text = "No major events right now."

        text_surface = text_font.render(event_text, True, (180, 200, 225))
        screen.blit(text_surface, (self.news_rect.x + 16, self.news_rect.y + 46))

    def draw_start_screen(self, screen, title_font, text_font):
        width = screen.get_width()
        height = screen.get_height()
        self.build_layout(width, height)

        overlay = pygame.Surface((width, height))
        overlay.fill((10, 18, 30))
        screen.blit(overlay, (0, 0))

        title = title_font.render("Cure Earth: Global Defense", True, (245, 248, 255))
        title_rect = title.get_rect(center=(width // 2, height // 2 - 120))
        screen.blit(title, title_rect)

        sub = text_font.render("Choose difficulty to start", True, (180, 200, 225))
        sub_rect = sub.get_rect(center=(width // 2, height // 2 - 65))
        screen.blit(sub, sub_rect)

        for btn in self.diff_buttons:
            btn.draw(screen, text_font)

    def draw_end_screen(self, screen, title_font, text_font, result_text, score, day, world, rank):
        width = screen.get_width()
        height = screen.get_height()
        self.build_layout(width, height)

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel_w = 650
        panel_h = 430
        panel_x = width // 2 - panel_w // 2
        panel_y = height // 2 - panel_h // 2

        shadow_rect = pygame.Rect(panel_x, panel_y + 8, panel_w, panel_h)
        pygame.draw.rect(screen, (5, 8, 14), shadow_rect, border_radius=24)

        if result_text.upper() == "VICTORY":
            main_color = (120, 255, 160)
            border_color = (90, 210, 140)
        else:
            main_color = (255, 120, 120)
            border_color = (220, 90, 90)

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (18, 28, 44), panel_rect, border_radius=24)
        pygame.draw.rect(screen, border_color, panel_rect, 3, border_radius=24)

        title = title_font.render(result_text, True, main_color)
        title_rect = title.get_rect(center=(width // 2, panel_y + 50))
        screen.blit(title, title_rect)

        rank_surf = text_font.render(f"Rank: {rank}", True, (255, 220, 140))
        rank_rect = rank_surf.get_rect(center=(width // 2, panel_y + 92))
        screen.blit(rank_surf, rank_rect)

        lines = [
            f"Final Score: {score}",
            f"Days: {day}",
            f"Infection: {world.total_infection():.1f}%",
            f"Ecology: {world.total_ecology():.1f}%",
            f"Economy: {world.total_economy():.1f}%",
            f"Panic: {world.total_panic():.1f}%"
        ]

        y = panel_y + 145
        for line in lines:
            surf = text_font.render(line, True, (230, 238, 248))
            rect = surf.get_rect(center=(width // 2, y))
            screen.blit(surf, rect)
            y += 30

        hint = text_font.render("Press R or use the button below", True, (160, 180, 205))
        hint_rect = hint.get_rect(center=(width // 2, panel_y + 360))
        screen.blit(hint, hint_rect)

        self.restart_button.draw(screen, text_font)

    def get_clicked_action(self, pos):
        for button in self.buttons:
            if button.is_clicked(pos):
                return button.action
        return None

    def is_restart_clicked(self, pos):
        return self.restart_button.is_clicked(pos)

    def get_clicked_difficulty(self, pos):
        for btn in self.diff_buttons:
            if btn.is_clicked(pos):
                return btn.action
        return None