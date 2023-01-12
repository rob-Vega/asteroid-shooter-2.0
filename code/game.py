import pygame, sys
from random import randint, uniform

class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/ship.png').convert_alpha()
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)
        
        # timer
        self.can_shoot = True
        self.shoot_time = None

        # sound
        self.laser_sound = pygame.mixer.Sound('../sounds/laser.ogg')

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 500:
                self.can_shoot = True

    def laser_shot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.laser_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

            Laser(laser_group, self.rect.midtop)

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask):
            pygame.quit()
            sys.exit()

    def update(self):
        self.input_position()
        self.laser_timer()
        self.laser_shot()
        self.meteor_collision()

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 600

        # sound
        self.explosion_sound = pygame.mixer.Sound('../sounds/explosion.wav')
        self.explosion_sound.set_volume(0.1)

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            self.kill()
            self.explosion_sound.play()

    def update(self):
        # self.rect.y -= 10
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        if self.rect.bottom < 0:
            self.kill()
        self.meteor_collision()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)

        # rnadomize meteor size
        surface = pygame.image.load('../graphics/meteor.png').convert_alpha()
        size = pygame.math.Vector2(surface.get_size()) * uniform(0.5, 1.5)
        self.scale_surf = pygame.transform.scale(surface, size)
        self.image = self.scale_surf
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 600)

        # rotation logic
        self.rotation = 0
        self.rotation_speed = randint(20, 50)

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotate_surf = pygame.transform.rotozoom(self.scale_surf, self.rotation, 1)
        self.image = rotate_surf
        self.rect = self.image.get_rect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.rotate()
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Score:
    def __init__(self):
        self.font = pygame.font.Font('../graphics/subatomic.ttf', 50)

    def display(self):
        score_text = f'Score: {pygame.time.get_ticks() // 1000}'
        text_surf = self.font.render(score_text, True, 'white')
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(
            display_surface, 
            'white', 
            text_rect.inflate(30, 30), 
            width = 8, 
            border_radius = 5
        )

# basic setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Asteroid Shooter 2.0')
clock = pygame.time.Clock()

# backgroud
bg_surf = pygame.image.load('../graphics/background.png').convert()

# sprite group
ship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# sprite creation 
ship = Ship(ship_group)
score = Score()

# timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 500)

music = pygame.mixer.Sound('../sounds/music.wav')
music.set_volume(0.1)

# game loop
while True:
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == meteor_timer:
            meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
            meteor_y_pos = randint(-150, -50)
            Meteor(groups = meteor_group, pos = (meteor_x_pos, meteor_y_pos))
    
    # delta time
    dt = clock.tick(60) / 1000

    # background
    display_surface.blit(bg_surf, (0, 0))

    # score
    score.display()

    # update
    ship_group.update()
    laser_group.update()
    meteor_group.update()

    # graphics
    ship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    music.play(loops = -1)

    # draw frame
    pygame.display.update()