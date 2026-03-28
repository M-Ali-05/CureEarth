import random
import pygame
from settings import WIDTH, HEIGHT, BG_COLOR, TITLE
from world import World
from ui import UI


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.big_font = pygame.font.SysFont("arial", 38, bold=True)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.ui = UI()
        self.running = True

        self.UPDATE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.UPDATE_EVENT, 1000)

        self.game_state = "menu"
        self.difficulty = "normal"
        self.rank = "-"

        self.money = 0
        self.science = 0
        self.day = 1
        self.score = 0
        self.current_event_text = "Choose difficulty to start."
        self.world = World("normal")
        self.selected_continent = None

    def get_action_cost(self, action):
        base_costs = {
            "vaccinate": 100,
            "eco": 80,
            "quarantine": 65,
            "medical_invest": 95,
            "support": 60,
            "close_air": 20,
            "close_sea": 15,
        }

        if self.difficulty == "easy":
            return int(base_costs[action] * 0.65)
        elif self.difficulty == "hard":
            return int(base_costs[action] * 1.15)
        return base_costs[action]

    def start_new_game(self, difficulty):
        self.difficulty = difficulty
        self.world = World(difficulty)
        self.selected_continent = None

        if difficulty == "easy":
            self.money = 500
            self.science = 140
        elif difficulty == "normal":
            self.money = 260
            self.science = 65
        else:
            self.money = 220
            self.science = 55

        self.day = 1
        self.score = 0
        self.rank = "-"
        self.current_event_text = f"{difficulty.title()} mode started."
        self.game_state = "playing"

    def reset_to_menu(self):
        self.game_state = "menu"
        self.current_event_text = "Choose difficulty to start."

    def run(self, fps):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(fps)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.game_state in ("win", "lose") and event.key == pygame.K_r:
                    self.reset_to_menu()

            elif event.type == pygame.VIDEORESIZE:
                new_width = max(1200, event.w)
                new_height = max(780, event.h)
                self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                self.world.rebuild_layout_if_needed(new_width, new_height)

            elif event.type == self.UPDATE_EVENT:
                if self.game_state == "playing":
                    self.update_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state == "menu":
                    choice = self.ui.get_clicked_difficulty(event.pos)
                    if choice == "diff_easy":
                        self.start_new_game("easy")
                    elif choice == "diff_normal":
                        self.start_new_game("normal")
                    elif choice == "diff_hard":
                        self.start_new_game("hard")

                elif self.game_state in ("win", "lose"):
                    if self.ui.is_restart_clicked(event.pos):
                        self.reset_to_menu()

                else:
                    self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        action = self.ui.get_clicked_action(pos)
        if action:
            self.apply_action(action)
            return

        clicked = self.world.get_clicked_continent(pos)
        if clicked:
            for continent in self.world.continents:
                continent.selected = False
            clicked.selected = True
            self.selected_continent = clicked
            self.current_event_text = f"Selected region: {clicked.name}"

    def apply_action(self, action):
        c = self.selected_continent

        if action == "global_vaccine":
            if self.money >= 180 and self.science >= 220:
                self.money -= 180
                self.science -= 220
                self.world.apply_global_project("global_vaccine")
                self.current_event_text = "Global Vaccine Program launched"
            else:
                self.current_event_text = "Not enough money or science"
            return

        elif action == "global_climate":
            if self.money >= 170 and self.science >= 120:
                self.money -= 170
                self.science -= 120
                self.world.apply_global_project("global_climate")
                self.current_event_text = "Climate Recovery Initiative launched"
            else:
                self.current_event_text = "Not enough money or science"
            return

        elif action == "global_info":
            if self.money >= 140 and self.science >= 90:
                self.money -= 140
                self.science -= 90
                self.world.apply_global_project("global_info")
                self.current_event_text = "Global Information Campaign launched"
            else:
                self.current_event_text = "Not enough money or science"
            return

        if c is None:
            self.current_event_text = "Select a continent first"
            return

        if action == "vaccinate":
            cost = self.get_action_cost("vaccinate")
            if self.money >= cost:
                c.vaccinate()
                self.money -= cost
                self.current_event_text = f"Vaccination program launched in {c.name}"
            else:
                self.current_event_text = "Not enough money for vaccination"

        elif action == "eco":
            cost = self.get_action_cost("eco")
            if self.money >= cost:
                c.improve_ecology()
                self.money -= cost
                self.current_event_text = f"Eco program launched in {c.name}"
            else:
                self.current_event_text = "Not enough money for eco program"

        elif action == "quarantine":
            cost = self.get_action_cost("quarantine")
            if self.money >= cost:
                c.quarantine()
                self.money -= cost
                self.current_event_text = f"Quarantine introduced in {c.name}"
            else:
                self.current_event_text = "Not enough money for quarantine"

        elif action == "medical_invest":
            cost = self.get_action_cost("medical_invest")
            if self.money >= cost:
                c.invest_medical()
                self.money -= cost
                self.current_event_text = f"Medical investment started in {c.name}"
            else:
                self.current_event_text = "Not enough money for medical investment"

        elif action == "support":
            cost = self.get_action_cost("support")
            if self.money >= cost:
                c.support_campaign()
                self.money -= cost
                self.current_event_text = f"Support campaign started in {c.name}"
            else:
                self.current_event_text = "Not enough money for support campaign"

        elif action == "close_air":
            cost = self.get_action_cost("close_air")
            if self.money >= cost:
                c.close_air()
                self.money -= cost
                c.panic += 1.5
                self.current_event_text = f"Air routes closed in {c.name}"
            else:
                self.current_event_text = "Not enough money to close air routes"

        elif action == "open_air":
            c.open_air()
            self.current_event_text = f"Air routes reopened in {c.name}"

        elif action == "close_sea":
            cost = self.get_action_cost("close_sea")
            if self.money >= cost:
                c.close_sea()
                self.money -= cost
                c.panic += 1.0
                self.current_event_text = f"Sea routes closed in {c.name}"
            else:
                self.current_event_text = "Not enough money to close sea routes"

        elif action == "open_sea":
            c.open_sea()
            self.current_event_text = f"Sea routes reopened in {c.name}"

    def calculate_score(self):
        avg_infection = self.world.total_infection()
        avg_ecology = self.world.total_ecology()
        avg_economy = self.world.total_economy()
        avg_panic = self.world.total_panic()
        avg_trust = self.world.total_trust()

        score = 0
        score += int(self.day * 5)
        score += int((100 - avg_infection) * 15)
        score += int(avg_ecology * 8)
        score += int(avg_economy * 10)
        score += int((100 - avg_panic) * 7)
        score += int(avg_trust * 7)
        score += int(self.money * 0.15)
        score += int(self.science * 0.15)
        if self.difficulty == "hard":
            score = int(score * 1.2)
        return max(0, score)

    def update_resources(self):
        base_income = sum(c.economy * 0.9 for c in self.world.continents) * 0.07

        if self.difficulty == "easy":
            base_income *= 1.35
        elif self.difficulty == "hard":
            base_income *= 0.9

        closed_air_count = sum(1 for c in self.world.continents if not c.air_open)
        closed_sea_count = sum(1 for c in self.world.continents if not c.sea_open)
        crisis_count = self.world.crisis_count()

        maintenance = closed_air_count * 5 + closed_sea_count * 3 + crisis_count * 8
        income = max(0, int(base_income - maintenance))
        self.money += income

        science_gain = 0
        for c in self.world.continents:
            if c.panic < 35 and c.trust > 45:
                science_gain += c.medical * 0.06

        if self.difficulty == "easy":
            science_gain *= 1.2

        self.science += int(science_gain)

    def trigger_random_event(self):
        event_chance = {
            "easy": 0.06,
            "normal": 0.13,
            "hard": 0.18
        }[self.difficulty]

        if random.random() >= event_chance:
            return

        event = random.choice([
            "fire", "science", "pollution", "aid", "protests", "hospital_overload", "volunteers"
        ])

        if event == "fire":
            c = random.choice(self.world.continents)
            c.ecology = max(0, c.ecology - 12)
            c.infection = min(100, c.infection + 3)
            self.current_event_text = f"Wildfire damaged ecosystems in {c.name}"

        elif event == "science":
            self.science += 35
            self.current_event_text = "Research grant accelerated science"

        elif event == "pollution":
            c = random.choice(self.world.continents)
            c.ecology = max(0, c.ecology - 8)
            c.panic = min(100, c.panic + 4)
            self.current_event_text = f"Pollution wave worsened conditions in {c.name}"

        elif event == "aid":
            self.money += 50
            self.current_event_text = "International aid delivered emergency funds"

        elif event == "protests":
            c = random.choice(self.world.continents)
            c.trust = max(0, c.trust - 7)
            c.panic = min(100, c.panic + 6)
            self.current_event_text = f"Transport protests disrupted response in {c.name}"

        elif event == "hospital_overload":
            c = random.choice(self.world.continents)
            c.infection = min(100, c.infection + 5)
            c.medical = max(0, c.medical - 6)
            c.panic = min(100, c.panic + 6)
            self.current_event_text = f"Hospitals overloaded in {c.name}"

        elif event == "volunteers":
            c = random.choice(self.world.continents)
            c.trust = min(100, c.trust + 6)
            c.panic = max(0, c.panic - 5)
            self.current_event_text = f"Volunteer movement stabilized {c.name}"

    def calculate_rank(self):
        inf = self.world.total_infection()
        eco = self.world.total_ecology()
        econ = self.world.total_economy()
        panic = self.world.total_panic()
        trust = self.world.total_trust()
        crises = self.world.crisis_count()

        if inf < 3 and eco > 75 and econ > 55 and panic < 35 and trust > 60 and crises == 0:
            return "Gold Victory"
        elif inf < 5 and eco > 68 and crises <= 1:
            return "Silver Victory"
        elif inf < 8 and self.day >= 25:
            return "Bronze Victory"
        return "Survived"

    def update_game(self):
        self.day += 1
        self.world.update()
        self.update_resources()
        self.trigger_random_event()

        self.score = self.calculate_score()

        avg_infection = self.world.total_infection()
        avg_ecology = self.world.total_ecology()
        avg_economy = self.world.total_economy()
        avg_panic = self.world.total_panic()
        crisis_count = self.world.crisis_count()

        if avg_infection > 85:
            self.current_event_text = "Defeat. Infection overwhelmed the world."
            self.rank = "Defeat"
            self.game_state = "lose"

        elif crisis_count >= 3:
            self.current_event_text = "Defeat. Too many continents entered crisis."
            self.rank = "Defeat"
            self.game_state = "lose"

        elif avg_economy < 15:
            self.current_event_text = "Defeat. Global economy collapsed."
            self.rank = "Defeat"
            self.game_state = "lose"

        elif avg_panic > 90:
            self.current_event_text = "Defeat. Global panic became uncontrollable."
            self.rank = "Defeat"
            self.game_state = "lose"

        elif (
            avg_infection < 5
            and avg_ecology > 70
            and avg_economy > 45
            and crisis_count <= 1
            and self.day >= 25
        ):
            self.current_event_text = "Victory. You stabilized the planet."
            self.rank = self.calculate_rank()
            self.game_state = "win"

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.game_state == "menu":
            self.ui.draw_start_screen(self.screen, self.big_font, self.font)
            pygame.display.flip()
            return

        self.world.draw(self.screen, self.small_font)

        self.ui.draw_top_bar(
            self.screen,
            self.font,
            self.money,
            self.science,
            self.day,
            self.score,
            self.world,
            self.difficulty
        )

        self.ui.draw_side_panel(
            self.screen,
            self.title_font,
            self.small_font,
            self.selected_continent
        )

        self.ui.draw_event_box(
            self.screen,
            self.font,
            self.small_font,
            self.current_event_text
        )

        if self.game_state == "win":
            self.ui.draw_end_screen(
                self.screen,
                self.big_font,
                self.font,
                "VICTORY",
                self.score,
                self.day,
                self.world,
                self.rank
            )

        elif self.game_state == "lose":
            self.ui.draw_end_screen(
                self.screen,
                self.big_font,
                self.font,
                "DEFEAT",
                self.score,
                self.day,
                self.world,
                self.rank
            )

        pygame.display.flip()