import pygame
from coordinateconverter import CoordinateConverter

BLACK, WHITE, RED, \
GREEN, BLUE, HOTPINK = (0, 0, 0), (255, 255, 255), (255, 0, 0), \
                       (0, 255, 0), (0, 0, 255), (255, 105, 180)

class CircleGame:
    def __init__(self):
        self.display_width = 800
        self.display_height = 600
        self.title = 'Circle Game'
        pygame.display.set_caption(self.title)

    def screen_set(self):
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        self.space_img = pygame.image.load('../img/space_img.jpg')
        self.screen.blit(self.space_img, self.space_img.get_rect())

    def display_dots(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), 10)

    def dots_pos(self, rr, tt):
        self.rr, self.tt = rr, tt
        return self.converter.cartesian_to_pixel(self.converter.polar_to_cartesian((self.rr, self.tt)))

    def dots_move(self, pygame, clock):
        self.pygame, self.clock = pygame, clock
        self.r, self.theta, self.r_change, self.theta_change = 0, 0, 0, 0
        self.killer_theta, self.goal_theta = 0, 0
        self.converter = CoordinateConverter(self.display_width, self.display_height)
        self.exit = False

        while not self.exit:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.exit = True

                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_LEFT:
                        self.theta_change = -10  # move clockwise
                        print("←")

                    if event.key == self.pygame.K_RIGHT:
                        self.theta_change = 10  # move counterclockwise
                        print("→")

                    if event.key == self.pygame.K_DOWN:
                        self.r_change = -50  # move towards origin
                        print("↓")

                    if event.key == self.pygame.K_UP:
                        self.r_change = 50  # move away from origin
                        print("↑")

                if event.type == self.pygame.KEYUP:

                    if event.key in (self.pygame.K_LEFT, self.pygame.K_RIGHT):
                        self.theta_change = 0
                    if event.key in (self.pygame.K_DOWN, self.pygame.K_UP):
                        self.r_change = 0

            self.r += self.r_change
            self.theta += self.theta_change
            self.killer_theta -= 10
            self.goal_theta += 10
            self.player_x, self.player_y = self.dots_pos(self.r, self.theta)
            self.killer_x, self.killer_y = self.dots_pos(200, self.killer_theta)
            self.goal_x, self.goal_y = self.dots_pos(150, self.goal_theta)

            self.screen_set()

            self.display_dots(self.player_x, self.player_y, HOTPINK)
            self.display_dots(self.killer_x, self.killer_y, RED)
            self.display_dots(self.goal_x, self.goal_y, GREEN)

            self.pygame.display.flip()
            self.clock.tick(30)

        return self.pygame, self.clock