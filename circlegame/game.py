import pygame
from circlegame.polarutilities.coordinateconverter import CoordinateConverter
import random
import circlegame.characters.goal
import circlegame.characters.killer
import circlegame.characters.player


colors = {"BLACK": (0, 0, 0),
          "WHITE": (255, 255, 255),
          "RED": (255, 0, 0),
          "GREEN": (0, 255, 0),
          "BLUE": (0, 0, 255),
          "HOTPINK": (255, 105, 180),
          "YELLOW": (255,255,204)}

TEXT_SIZE = 30

class Game:
    def __init__(self, screen, clock, wallpaper_path):
        self.screen = screen
        self.clock = clock
        self.converter = CoordinateConverter(self.screen.get_width(), self.screen.get_height())
        self.game_over = False
        self.wallpaper_img = pygame.image.load(wallpaper_path)

        self.radius_list = self.setup_orbits()
        self.goals = self.setup_goals()
        self.killers = self.setup_killers()
        self.player = self.setup_player()

    def setup_orbits(self):
        smaller_dimension = min(self.screen.get_width(), self.screen.get_height())
        orbit_spacing = 50  # number of pixels
        orbit_count = (smaller_dimension // 2) // orbit_spacing
        return [orbit_spacing * i for i in range(1, orbit_count)]

    def setup_goals(self):
        goal_count = len(self.radius_list)  # 1 goal per orbit
        return [circlegame.characters.goal.Goal(self.radius_list,
                                                i,
                                                random.randint(0, 359)) for i in range(goal_count)]

    def setup_killers(self):
        killer_count = len(self.radius_list)  # 1 goal per orbit
        return [circlegame.characters.killer.Killer(self.radius_list,
                                                    i,
                                                    random.randint(0, 359)) for i in range(killer_count)]

    def setup_player(self):
        """
        Must be called after setup_killers() not before.
        """
        radius_index = len(self.radius_list) - 1

        # Place on opposite side of killer as not to get killed immediately when spawned.
        initial_angle = self.killers[radius_index].get_angle() - 180

        # Have player and killer in initial orbit move the same direction.
        self.killers[radius_index].move_left()

        return circlegame.characters.player.Player(self.radius_list, radius_index, initial_angle)

    def start(self):

        self.text_set = pygame.font.Font(pygame.font.get_default_font(), TEXT_SIZE)

        while not self.game_over:
            self.listen_for_events()

            self.move_characters()

            if self.player.is_alive():
                self.check_player_interactions()

            self.display_wallpaper()      # make sure to be the first thing to display
            self.display_score(self.text_set)
            self.display_interactive_buttons()
            self.display_orbits()  # draw the orbits over the screens
            self.display_characters()
            pygame.display.flip()
            self.clock.tick(10)

    def listen_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True

            if self.player.is_alive():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.player.move_left()
                    if event.key == pygame.K_RIGHT:
                        self.player.move_right()
                    if event.key == pygame.K_UP:
                        self.player.increment_radius_index()
                    if event.key == pygame.K_DOWN:
                        self.player.decrement_radius_index()

    def move_characters(self):
        for killer in self.killers:
            if killer.is_moving_left():
                killer.change_angle(5)
            else:
                killer.change_angle(-5)
        if self.player.is_alive():
            if self.player.is_moving_left():
                self.player.change_angle(5)
            else:
                self.player.change_angle(-5)

    def check_player_interactions(self):
        for i, goal in enumerate(self.goals):
            if goal.is_colliding_with(self.player):
                self.player.pick_up_goal(goal)
                del self.goals[i]

        # spawn new goals if none left
        if not self.goals:
            self.goals = self.setup_goals()

        for killer in self.killers:
            if killer.is_colliding_with(self.player):
                self.player.die()

    def display_wallpaper(self):
        self.screen.blit(self.wallpaper_img, self.wallpaper_img.get_rect())

    def display_score(self, text_set):
        self.text_set = text_set
        self.score_text = self.text_set.render("SCORE", True, colors["WHITE"])
        self.screen.blit(self.score_text, (10, 10))
        self.point_text = self.text_set.render(str(self.player.get_points_collected()), True, colors["WHITE"])
        self.screen.blit(self.point_text, (50, 50))

    def display_interactive_buttons(self):
        # NEW board
        pygame.draw.rect(self.screen, colors['BLACK'], (self.screen.get_width() - 206, 6, 186, 36))
        self.new_game_text = self.text_set.render("NEW", True, colors["WHITE"])
        self.screen.blit(self.new_game_text, (self.screen.get_width() - 150, 12))

        # NEXT board
        pygame.draw.rect(self.screen, colors['BLACK'], (self.screen.get_width() - 206, 48, 186, 36))
        self.new_game_text = self.text_set.render("NEXT", True, colors["WHITE"])
        self.screen.blit(self.new_game_text, (self.screen.get_width() - 156, 54))

        # QUIT board
        pygame.draw.rect(self.screen, colors['BLACK'], (self.screen.get_width() - 206, 90, 186, 36))
        self.new_game_text = self.text_set.render("QUIT", True, colors["WHITE"])
        self.screen.blit(self.new_game_text, (self.screen.get_width() - 150, 96))

        # Get mouse position
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        # NEW interactive button
        if (self.screen.get_width() - 206 <= self.mouse_x <= self.screen.get_width() - 20) and (6 <= self.mouse_y <= 42):
            pygame.draw.rect(self.screen, colors['WHITE'], (self.screen.get_width() - 206, 6, 186, 36))
            self.new_game_text = self.text_set.render("NEW", True, colors["RED"])
            self.screen.blit(self.new_game_text, (self.screen.get_width()- 200, 12))
            if pygame.mouse.get_pressed()[0] == 1:
                self.player.renew_point()
                self.player.resurrect()
                self.goals = self.setup_goals()
                self.start()

        # NEXT interactive button
        elif (self.screen.get_width() - 206 <= self.mouse_x <= self.screen.get_width() - 20) and (48 <= self.mouse_y <= 84):
            pygame.draw.rect(self.screen, colors['WHITE'], (self.screen.get_width() - 206, 48, 186, 36))
            self.new_game_text = self.text_set.render("NEXT", True, colors["RED"])
            self.screen.blit(self.new_game_text, (self.screen.get_width()- 200, 54))
            if pygame.mouse.get_pressed()[0] == 1:
                self.player.resurrect()
                self.goals = self.setup_goals()
                self.start()

        # QUIT interactive button
        elif (self.screen.get_width() - 206 <= self.mouse_x <= self.screen.get_width() - 20) and (90 <= self.mouse_y <= 126):
            pygame.draw.rect(self.screen, colors['WHITE'], (self.screen.get_width() - 206, 90, 186, 36))
            self.new_game_text = self.text_set.render("QUIT", True, colors["RED"])
            self.screen.blit(self.new_game_text, (self.screen.get_width()- 200, 96))
            if pygame.mouse.get_pressed()[0] == 1:
                pygame.quit()
                quit()

    def display_orbits(self):
        for radius in self.radius_list:
            for angle in range(360):
                pygame.draw.circle(self.screen, colors['WHITE'], self.converter.polar_to_pixel((radius, angle)), 1)

    def display_characters(self):
        characters_to_move = self.goals + self.killers

        if self.player.is_alive():
            characters_to_move.append(self.player)

        for character in characters_to_move:
            radius_index, angle, color_key = character.get_draw_data()
            radius = self.radius_list[radius_index]
            pygame.draw.circle(self.screen, colors[color_key],
                               self.converter.polar_to_pixel((radius, angle)), 10)
