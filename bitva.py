# Исправленный код (полный файл)
# Изменения: добавлена обработка столкновений питомцев и мин в основном цикле,
# а также метод attack у Pet и check_collision у Mine теперь вызываются.

import pygame
import random
import math
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

ARENA_PADDING = 60
ARENA_LEFT = ARENA_PADDING
ARENA_RIGHT = SCREEN_WIDTH - ARENA_PADDING
ARENA_TOP = ARENA_PADDING + 50
ARENA_BOTTOM = SCREEN_HEIGHT - ARENA_PADDING

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 80, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
GOLD = (255, 215, 0)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

BALL_RADIUS = 25
BASE_DAMAGE = 10
ABILITY_COOLDOWN_MAX = 300

ABILITY_RAGE = 'rage'
ABILITY_HEAL = 'heal'
ABILITY_FREEZE = 'freeze'
ABILITY_SHIELD = 'shield'
ABILITY_CRIT = 'crit'
ABILITY_ACCEL = 'accel'
ABILITY_SUMMON = 'summon'
ABILITY_RANGED = 'ranged'
ABILITY_SWORD = 'sword'
ABILITY_VAMPIRE = 'vampire'
ABILITY_TANK = 'tank'
ABILITY_NECRO = 'necro'
ABILITY_ENGINEER = 'engineer'
ABILITY_SHAMAN = 'shaman'
ABILITY_DEATHKNIGHT = 'deathknight'

CHARACTERS = [
    {"name": "Берсерк", "color": RED, "ability": ABILITY_RAGE, "desc": "Ярость: удвоенный урон 3с", "effect_duration": 180, "effect_value": 2.0},
    {"name": "Жрец", "color": GREEN, "ability": ABILITY_HEAL, "desc": "Исцеление: +20 HP", "effect_duration": 0, "effect_value": 20},
    {"name": "Маг", "color": BLUE, "ability": ABILITY_FREEZE, "desc": "Заморозка: замедление врага 3с", "effect_duration": 180, "effect_value": 0.5},
    {"name": "Паладин", "color": GOLD, "ability": ABILITY_SHIELD, "desc": "Щит: -50% урона 3с", "effect_duration": 180, "effect_value": 0.5},
    {"name": "Разбойник", "color": PURPLE, "ability": ABILITY_CRIT, "desc": "Крит: следующая атака x3", "effect_duration": 1, "effect_value": 3.0},
    {"name": "Ускоритель", "color": CYAN, "ability": ABILITY_ACCEL, "desc": "Ускорение: +0.1 скорости каждые 2с", "effect_duration": 0, "effect_value": 0.1},
    {"name": "Призыватель", "color": BROWN, "ability": ABILITY_SUMMON, "desc": "Призыв: питомец 5 HP", "effect_duration": 0, "effect_value": 1},
    {"name": "Стрелок", "color": PINK, "ability": ABILITY_RANGED, "desc": "Стрела: дальняя атака 8 урона", "effect_duration": 0, "effect_value": 8},
    {"name": "Мечник", "color": (160, 160, 160), "ability": ABILITY_SWORD, "desc": "Мастер меча: +2 урона с атакой", "effect_duration": 0, "effect_value": 2},
    {"name": "Вампир", "color": (128, 0, 128), "ability": ABILITY_VAMPIRE, "desc": "Вампиризм: 25% урона в HP", "effect_duration": 0, "effect_value": 0.25},
    {"name": "Танк", "color": DARK_GRAY, "ability": ABILITY_TANK, "desc": "Танк: 150 HP, урон 7", "effect_duration": 0, "effect_value": 0},
    {"name": "Некромант", "color": (50, 50, 100), "ability": ABILITY_NECRO, "desc": "При смерти врага вызывает скелета", "effect_duration": 0, "effect_value": 10},
    {"name": "Инженер", "color": (255, 140, 0), "ability": ABILITY_ENGINEER, "desc": "Мины: взрыв 15 урона", "effect_duration": 0, "effect_value": 15},
    {"name": "Шаман", "color": (0, 150, 100), "ability": ABILITY_SHAMAN, "desc": "Тотем: +5 HP каждые 6с", "effect_duration": 0, "effect_value": 5},
    {"name": "Рыцарь смерти", "color": (100, 0, 0), "ability": ABILITY_DEATHKNIGHT, "desc": "Проклятие: -2 брони врагу", "effect_duration": 0, "effect_value": 2}
]

class Projectile:
    def __init__(self, x, y, target, damage, color):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.radius = 5
        self.speed = 6
        self.active = True

    def update(self):
        if not self.target or self.target.health <= 0:
            self.active = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.active = False
            self.target.take_damage(self.damage)
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Mine:
    def __init__(self, x, y, damage, owner):
        self.x = x
        self.y = y
        self.damage = damage
        self.radius = 12
        self.active = True
        self.owner = owner

    def check_collision(self, ball):
        if ball != self.owner and math.hypot(ball.x - self.x, ball.y - self.y) < ball.radius + self.radius:
            ball.take_damage(self.damage)
            self.active = False
            return True
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y)), self.radius, 2)

class Pet:
    def __init__(self, x, y, owner, health, damage):
        self.x = x
        self.y = y
        self.owner = owner
        self.health = health
        self.max_health = health
        self.damage = damage
        self.radius = 12
        self.vx = random.choice([-2, 2])
        self.vy = random.choice([-2, 2])
        self.active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x - self.radius <= ARENA_LEFT:
            self.x = ARENA_LEFT + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius >= ARENA_RIGHT:
            self.x = ARENA_RIGHT - self.radius
            self.vx = -abs(self.vx)
        if self.y - self.radius <= ARENA_TOP:
            self.y = ARENA_TOP + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= ARENA_BOTTOM:
            self.y = ARENA_BOTTOM - self.radius
            self.vy = -abs(self.vy)

    def attack(self, other):
        # Питомец атакует врага и получает урон (погибает)
        other.take_damage(self.damage)
        self.active = False

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 100), (int(self.x), int(self.y)), self.radius)
        hp_width = 2 * self.radius
        hp_height = 3
        hp_x = self.x - self.radius
        hp_y = self.y - self.radius - 5
        pygame.draw.rect(screen, RED, (hp_x, hp_y, hp_width, hp_height))
        pygame.draw.rect(screen, GREEN, (hp_x, hp_y, hp_width * (self.health / self.max_health), hp_height))

class Ball:
    def __init__(self, x, y, vx, vy, character, name_suffix=""):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = BALL_RADIUS
        self.character = character
        self.color = character["color"]
        self.name = character["name"] + name_suffix
        if character["ability"] == ABILITY_TANK:
            self.max_health = 150
            self.base_damage = 7
        else:
            self.max_health = 100
            self.base_damage = BASE_DAMAGE
        self.health = self.max_health
        self.ability_cooldown = 0
        self.active_effect = None
        self.active_effect_timer = 0
        self.damage_multiplier = 1.0
        self.incoming_damage_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.crit_ready = False
        self.hit_flash = 0
        self.particles = []
        self.extra_power = 0
        self.speed_bonus = 1.0
        self.summon_timer = 0
        self.ranged_timer = 0
        self.mines = []
        self.pets = []
        self.totem_timer = 0

    def update(self):
        self.x += self.vx * self.speed_multiplier * self.speed_bonus
        self.y += self.vy * self.speed_multiplier * self.speed_bonus

        if self.x - self.radius <= ARENA_LEFT:
            self.x = ARENA_LEFT + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius >= ARENA_RIGHT:
            self.x = ARENA_RIGHT - self.radius
            self.vx = -abs(self.vx)
        if self.y - self.radius <= ARENA_TOP:
            self.y = ARENA_TOP + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= ARENA_BOTTOM:
            self.y = ARENA_BOTTOM - self.radius
            self.vy = -abs(self.vy)

        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
        if self.ability_cooldown == 0:
            self.use_ability()
            self.ability_cooldown = ABILITY_COOLDOWN_MAX

        ab_type = self.character["ability"]
        if ab_type == ABILITY_ACCEL and self.speed_bonus < 2.5:
            if random.randrange(1, 121) == 1:
                self.speed_bonus += 0.1
        if ab_type == ABILITY_SUMMON:
            if self.summon_timer <= 0:
                self.summon_timer = 600
                pet = Pet(self.x, self.y, self, 5, 2)
                self.pets.append(pet)
            else:
                self.summon_timer -= 1
        if ab_type == ABILITY_SHAMAN:
            if self.totem_timer <= 0:
                self.totem_timer = 360
                self.health = min(self.health + self.character["effect_value"], self.max_health)
            else:
                self.totem_timer -= 1

        if self.active_effect_timer > 0:
            self.active_effect_timer -= 1
            if self.active_effect_timer <= 0:
                self.reset_effects()

        if self.hit_flash > 0:
            self.hit_flash -= 1

        for pet in self.pets[:]:
            pet.update()
            if pet.health <= 0 or not pet.active:
                self.pets.remove(pet)
        for mine in self.mines[:]:
            if not mine.active:
                self.mines.remove(mine)
        for p in self.particles[:]:
            p[0] += p[3]
            p[1] += p[4]
            p[2] -= 1
            if p[2] <= 0:
                self.particles.remove(p)

    def use_ability(self):
        ab_type = self.character["ability"]
        value = self.character["effect_value"]
        duration = self.character["effect_duration"]

        if ab_type == ABILITY_RAGE:
            self.active_effect = ABILITY_RAGE
            self.active_effect_timer = duration
            self.damage_multiplier = value
        elif ab_type == ABILITY_HEAL:
            self.health = min(self.health + value, self.max_health)
            for _ in range(10):
                self.particles.append([self.x, self.y, 10, random.uniform(-2,2), random.uniform(-2,2)])
        elif ab_type == ABILITY_SHIELD:
            self.active_effect = ABILITY_SHIELD
            self.active_effect_timer = duration
            self.incoming_damage_multiplier = value
        elif ab_type == ABILITY_CRIT:
            self.crit_ready = True
            for _ in range(15):
                self.particles.append([self.x, self.y, 8, random.uniform(-3,3), random.uniform(-3,3)])
        elif ab_type == ABILITY_ACCEL:
            self.speed_bonus = min(self.speed_bonus + 0.2, 2.5)
        elif ab_type == ABILITY_SUMMON:
            pet = Pet(self.x, self.y, self, 5, 2)
            self.pets.append(pet)
        elif ab_type == ABILITY_SWORD:
            self.extra_power = min(self.extra_power + value, 20)
        elif ab_type == ABILITY_TANK:
            self.incoming_damage_multiplier *= 0.7
            self.active_effect = "DEFENSE"
            self.active_effect_timer = 180
        elif ab_type == ABILITY_ENGINEER:
            mine = Mine(self.x, self.y, value, self)
            self.mines.append(mine)
        elif ab_type == ABILITY_SHAMAN:
            self.health = min(self.health + value*2, self.max_health)

    def reset_effects(self):
        self.damage_multiplier = 1.0
        self.incoming_damage_multiplier = 1.0
        self.active_effect = None

    def take_damage(self, amount, source=None):
        if source and source.crit_ready and source.character["ability"] == ABILITY_CRIT:
            amount *= source.character["effect_value"]
            source.crit_ready = False
            for _ in range(15):
                source.particles.append([source.x, source.y, 12, random.uniform(-3,3), random.uniform(-3,3)])
        if source and source.character["ability"] == ABILITY_SWORD:
            amount += source.extra_power
        actual_damage = amount * self.incoming_damage_multiplier
        self.health -= actual_damage
        self.hit_flash = 5
        for _ in range(8):
            self.particles.append([self.x, self.y, 6, random.uniform(-2,2), random.uniform(-2,2)])
        if source and source.character["ability"] == ABILITY_VAMPIRE and source != self:
            heal = actual_damage * source.character["effect_value"]
            source.health = min(source.health + heal, source.max_health)
        if self.health < 0:
            self.health = 0

    def draw(self, screen, font):
        glow_radius = self.radius + 4
        glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        if self.active_effect == ABILITY_RAGE:
            glow_color = (*ORANGE, 80)
        elif self.active_effect == ABILITY_SHIELD:
            glow_color = (*GOLD, 80)
        elif self.active_effect == "DEFENSE":
            glow_color = (*DARK_GRAY, 80)
        else:
            glow_color = (*self.color, 40)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (self.x - glow_radius, self.y - glow_radius))

        current_color = self.color
        if self.hit_flash > 0:
            current_color = WHITE
        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        highlight = pygame.Surface((self.radius//2, self.radius//3), pygame.SRCALPHA)
        highlight.fill((255,255,255,80))
        screen.blit(highlight, (self.x - self.radius//3, self.y - self.radius//2))

        health_width = 2 * self.radius
        health_height = 8
        health_x = self.x - self.radius
        health_y = self.y - self.radius - 12
        pygame.draw.rect(screen, (100,0,0), (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, (0,200,0), (health_x, health_y, health_width * (self.health / self.max_health), health_height))

        hp_text = font.render(f"{self.name} {int(self.health)}", True, BLACK)
        text_rect = hp_text.get_rect(center=(self.x, self.y - self.radius - 25))
        screen.blit(hp_text, text_rect)

        cd_progress = self.ability_cooldown / ABILITY_COOLDOWN_MAX
        if cd_progress < 1:
            cd_secs = math.ceil(self.ability_cooldown / FPS)
            cd_text = font.render(f"CD:{cd_secs}", True, DARK_GRAY)
            screen.blit(cd_text, (self.x - 18, self.y + self.radius + 5))
        else:
            ready_text = font.render("READY!", True, GREEN)
            screen.blit(ready_text, (self.x - 25, self.y + self.radius + 5))

        if self.active_effect == ABILITY_RAGE:
            effect_text = font.render("RAGE!", True, ORANGE)
            screen.blit(effect_text, (self.x - 22, self.y - self.radius - 42))
        elif self.active_effect == ABILITY_SHIELD:
            effect_text = font.render("SHIELD", True, GOLD)
            screen.blit(effect_text, (self.x - 25, self.y - self.radius - 42))
        elif self.active_effect == "DEFENSE":
            effect_text = font.render("DEFENSE", True, DARK_GRAY)
            screen.blit(effect_text, (self.x - 28, self.y - self.radius - 42))
        elif self.crit_ready:
            effect_text = font.render("CRIT!", True, PURPLE)
            screen.blit(effect_text, (self.x - 22, self.y - self.radius - 42))

        for pet in self.pets:
            pet.draw(screen)
        for mine in self.mines:
            mine.draw(screen)
        for p in self.particles:
            pygame.draw.circle(screen, self.color, (int(p[0]), int(p[1])), max(1, p[2]//3))

class ImpactEffect:
    def __init__(self, x, y, duration=10, max_radius=30):
        self.x = x; self.y = y; self.duration = duration; self.max_radius = max_radius; self.frame = 0
    def update(self):
        self.frame += 1
        return self.frame < self.duration
    def draw(self, screen):
        progress = self.frame / self.duration
        rad = int(self.max_radius * progress)
        alpha = int(255 * (1 - progress))
        surf = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255,255,255,alpha), (rad, rad), rad, 2)
        screen.blit(surf, (self.x - rad, self.y - rad))

def resolve_collision(ball1, ball2, impact_effects, projectiles):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = math.hypot(dx, dy)
    min_distance = ball1.radius + ball2.radius
    if distance < min_distance:
        impact_effects.append(ImpactEffect((ball1.x+ball2.x)/2, (ball1.y+ball2.y)/2))
        overlap = min_distance - distance
        angle = math.atan2(dy, dx)
        cx = math.cos(angle) * overlap / 2
        cy = math.sin(angle) * overlap / 2
        ball1.x -= cx; ball1.y -= cy
        ball2.x += cx; ball2.y += cy
        nx = dx / distance; ny = dy / distance
        vrelx = ball2.vx - ball1.vx
        vrely = ball2.vy - ball1.vy
        dot = vrelx * nx + vrely * ny
        if dot < 0:
            imp = (2.0 * dot) / 2.0
            ball1.vx += imp * nx; ball1.vy += imp * ny
            ball2.vx -= imp * nx; ball2.vy -= imp * ny
        damage1 = ball1.base_damage * ball1.damage_multiplier
        damage2 = ball2.base_damage * ball2.damage_multiplier
        ball1.take_damage(damage2, source=ball2)
        ball2.take_damage(damage1, source=ball1)
        if ball1.character["ability"] == ABILITY_RANGED:
            proj = Projectile(ball1.x, ball1.y, ball2, ball1.character["effect_value"], ball1.color)
            projectiles.append(proj)
        if ball2.character["ability"] == ABILITY_RANGED:
            proj = Projectile(ball2.x, ball2.y, ball1, ball2.character["effect_value"], ball2.color)
            projectiles.append(proj)
        if ball1.character["ability"] == ABILITY_DEATHKNIGHT:
            ball2.incoming_damage_multiplier += 0.2
            ball2.active_effect = "CURSE"
            ball2.active_effect_timer = 300
        if ball2.character["ability"] == ABILITY_DEATHKNIGHT:
            ball1.incoming_damage_multiplier += 0.2
            ball1.active_effect = "CURSE"
            ball1.active_effect_timer = 300
        return True
    return False

def draw_gradient_background(screen):
    for y in range(SCREEN_HEIGHT):
        r = int(30 + 20 * y/SCREEN_HEIGHT)
        g = int(30 + 40 * y/SCREEN_HEIGHT)
        b = int(50 + 30 * y/SCREEN_HEIGHT)
        pygame.draw.line(screen, (r,g,b), (0,y), (SCREEN_WIDTH,y))

def draw_arena(screen):
    inner = pygame.Rect(ARENA_LEFT, ARENA_TOP, ARENA_RIGHT-ARENA_LEFT, ARENA_BOTTOM-ARENA_TOP)
    pygame.draw.rect(screen, (0,0,0,128), (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.draw.rect(screen, (20,20,40), inner)
    for x in range(ARENA_LEFT, ARENA_RIGHT, 40):
        pygame.draw.line(screen, (80,80,100), (x, ARENA_TOP), (x, ARENA_BOTTOM), 1)
    for y in range(ARENA_TOP, ARENA_BOTTOM, 40):
        pygame.draw.line(screen, (80,80,100), (ARENA_LEFT, y), (ARENA_RIGHT, y), 1)
    pygame.draw.rect(screen, (200,200,220), inner, 4)
    corners = [(ARENA_LEFT, ARENA_TOP), (ARENA_RIGHT, ARENA_TOP),
               (ARENA_LEFT, ARENA_BOTTOM), (ARENA_RIGHT, ARENA_BOTTOM)]
    for cx,cy in corners:
        pygame.draw.circle(screen, (150,150,180), (cx,cy), 12)
        pygame.draw.circle(screen, (200,200,230), (cx,cy), 6)

def draw_top_panel(screen, font, ball1, ball2):
    panel = pygame.Rect(0,0,SCREEN_WIDTH,50)
    pygame.draw.rect(screen, (30,30,50), panel)
    pygame.draw.line(screen, (100,100,150), (0,50), (SCREEN_WIDTH,50), 2)
    mid = SCREEN_WIDTH//2
    pygame.draw.line(screen, (150,150,200), (mid,5), (mid,45), 1)
    pygame.draw.circle(screen, ball1.color, (40,25), 15)
    name1 = font.render(ball1.name, True, WHITE)
    screen.blit(name1, (65,12))
    hp_w = 150
    hp_x = 65
    hp_y = 32
    pygame.draw.rect(screen, (100,0,0), (hp_x, hp_y, hp_w, 8))
    pygame.draw.rect(screen, (0,200,0), (hp_x, hp_y, hp_w * (ball1.health/ball1.max_health), 8))
    hp_text = font.render(f"{int(ball1.health)}/{ball1.max_health}", True, WHITE)
    screen.blit(hp_text, (hp_x+hp_w+5, hp_y-2))
    cd_w = 60
    cd_prog = ball1.ability_cooldown / ABILITY_COOLDOWN_MAX
    cd_fill = int(cd_w * (1 - cd_prog))
    pygame.draw.rect(screen, (60,60,80), (mid-80,12,cd_w,8))
    pygame.draw.rect(screen, (0,200,255), (mid-80,12,cd_fill,8))
    cd_text = font.render(f"CD: {math.ceil(ball1.ability_cooldown/FPS)}с", True, WHITE)
    screen.blit(cd_text, (mid-80,22))
    ability1 = ball1.character["ability"][:3].upper()
    ab_text1 = font.render(f"Умение: {ability1}", True, YELLOW)
    screen.blit(ab_text1, (mid-80,35))
    pygame.draw.circle(screen, ball2.color, (SCREEN_WIDTH-40,25), 15)
    name2 = font.render(ball2.name, True, WHITE)
    screen.blit(name2, (SCREEN_WIDTH-135,12))
    hp_x2 = SCREEN_WIDTH-215
    pygame.draw.rect(screen, (100,0,0), (hp_x2, hp_y, hp_w, 8))
    pygame.draw.rect(screen, (0,200,0), (hp_x2, hp_y, hp_w * (ball2.health/ball2.max_health), 8))
    hp_text2 = font.render(f"{int(ball2.health)}/{ball2.max_health}", True, WHITE)
    screen.blit(hp_text2, (hp_x2+hp_w+5, hp_y-2))
    cd_fill2 = int(cd_w * (1 - ball2.ability_cooldown / ABILITY_COOLDOWN_MAX))
    pygame.draw.rect(screen, (60,60,80), (mid+20,12,cd_w,8))
    pygame.draw.rect(screen, (0,200,255), (mid+20,12,cd_fill2,8))
    cd_text2 = font.render(f"CD: {math.ceil(ball2.ability_cooldown/FPS)}с", True, WHITE)
    screen.blit(cd_text2, (mid+20,22))
    ability2 = ball2.character["ability"][:3].upper()
    ab_text2 = font.render(f"Умение: {ability2}", True, YELLOW)
    screen.blit(ab_text2, (mid+20,35))

def draw_menu(screen, font, title_font):
    screen.fill(DARK_GRAY)
    draw_gradient_background(screen)
    title = title_font.render("ВЫБОР ПЕРСОНАЖЕЙ (15 классов)", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
    instr = font.render("Игрок 1 кликает на персонажа, затем Игрок 2", True, LIGHT_GRAY)
    screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 70))
    card_w = 130
    card_h = 160
    spacing = 10
    cols = 5
    total_w = cols * card_w + (cols-1) * spacing
    start_x = (SCREEN_WIDTH - total_w) // 2
    start_y = 110
    cards = []
    for i, ch in enumerate(CHARACTERS):
        row = i // cols
        col = i % cols
        x = start_x + col * (card_w + spacing)
        y = start_y + row * (card_h + spacing)
        rect = pygame.Rect(x, y, card_w, card_h)
        pygame.draw.rect(screen, (60,60,80), rect, border_radius=8)
        pygame.draw.rect(screen, ch["color"], rect.inflate(-4,-4), border_radius=6)
        name_text = font.render(ch["name"], True, BLACK)
        screen.blit(name_text, (x+card_w//2 - name_text.get_width()//2, y+8))
        desc1 = font.render(ch["desc"][:12], True, DARK_GRAY)
        desc2 = font.render(ch["desc"][12:], True, DARK_GRAY)
        screen.blit(desc1, (x+5, y+40))
        screen.blit(desc2, (x+5, y+55))
        cd_text = font.render("5 сек", True, DARK_GRAY)
        screen.blit(cd_text, (x+card_w//2 - 15, y+card_h-25))
        cards.append((rect, i))
    selected = [None, None]
    selecting = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                for rect, idx in cards:
                    if rect.collidepoint(pos):
                        selected[selecting] = idx
                        if selecting == 0:
                            selecting = 1
                        else:
                            return selected[0], selected[1]
        for rect, idx in cards:
            if selected[0] == idx:
                pygame.draw.rect(screen, WHITE, rect.inflate(6,6), 2)
                label = font.render("Игрок 1", True, WHITE)
                screen.blit(label, (rect.x+5, rect.y-18))
            if selected[1] == idx:
                pygame.draw.rect(screen, WHITE, rect.inflate(6,6), 2)
                label = font.render("Игрок 2", True, WHITE)
                screen.blit(label, (rect.x+5, rect.y-18))
            if selecting == 0 and selected[0] is None:
                pointer = font.render("▲", True, YELLOW)
                screen.blit(pointer, (rect.centerx-5, rect.y-22))
            elif selecting == 1 and selected[1] is None and selected[0] is not None:
                pointer = font.render("▲", True, YELLOW)
                screen.blit(pointer, (rect.centerx-5, rect.y-22))
        pygame.display.flip()
        pygame.time.delay(30)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Битва шаров - 15 классов")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)
    title_font = pygame.font.SysFont("Arial", 24, bold=True)

    idx1, idx2 = draw_menu(screen, font, title_font)
    char1 = CHARACTERS[idx1]
    char2 = CHARACTERS[idx2]

    ball1 = Ball(
        random.randint(ARENA_LEFT + BALL_RADIUS + 20, (ARENA_LEFT+ARENA_RIGHT)//2 - 30),
        random.randint(ARENA_TOP + BALL_RADIUS + 20, ARENA_BOTTOM - BALL_RADIUS - 20),
        random.choice([-4,-3,3,4]), random.choice([-4,-3,3,4]),
        char1, " (1)"
    )
    ball2 = Ball(
        random.randint((ARENA_LEFT+ARENA_RIGHT)//2 + 30, ARENA_RIGHT - BALL_RADIUS - 20),
        random.randint(ARENA_TOP + BALL_RADIUS + 20, ARENA_BOTTOM - BALL_RADIUS - 20),
        random.choice([-4,-3,3,4]), random.choice([-4,-3,3,4]),
        char2, " (2)"
    )

    impact_effects = []
    projectiles = []
    running = True
    winner = None
    game_over = False
    game_over_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()
                return

        if not game_over:
            ball1.update()
            ball2.update()
            resolve_collision(ball1, ball2, impact_effects, projectiles)

            # Обновление снарядов
            for p in projectiles[:]:
                p.update()
                if not p.active:
                    projectiles.remove(p)

            # --- Проверка столкновений питомцев с вражеским шаром ---
            for pet in ball1.pets[:]:
                if math.hypot(pet.x - ball2.x, pet.y - ball2.y) < pet.radius + ball2.radius:
                    pet.attack(ball2)
                    impact_effects.append(ImpactEffect((pet.x+ball2.x)/2, (pet.y+ball2.y)/2))
            for pet in ball2.pets[:]:
                if math.hypot(pet.x - ball1.x, pet.y - ball1.y) < pet.radius + ball1.radius:
                    pet.attack(ball1)
                    impact_effects.append(ImpactEffect((pet.x+ball1.x)/2, (pet.y+ball1.y)/2))

            # --- Проверка столкновений мин ---
            for mine in ball1.mines[:]:
                if mine.check_collision(ball2):
                    impact_effects.append(ImpactEffect(mine.x, mine.y))
            for mine in ball2.mines[:]:
                if mine.check_collision(ball1):
                    impact_effects.append(ImpactEffect(mine.x, mine.y))

            # Обновление анимаций
            for eff in impact_effects[:]:
                if not eff.update():
                    impact_effects.remove(eff)

            if ball1.health <= 0:
                winner = ball2.name
                game_over = True
                game_over_timer = FPS * 3
            elif ball2.health <= 0:
                winner = ball1.name
                game_over = True
                game_over_timer = FPS * 3
        else:
            game_over_timer -= 1
            if game_over_timer <= 0:
                running = False

        draw_gradient_background(screen)
        draw_arena(screen)
        ball1.draw(screen, font)
        ball2.draw(screen, font)
        for p in projectiles:
            p.draw(screen)
        for eff in impact_effects:
            eff.draw(screen)
        draw_top_panel(screen, font, ball1, ball2)

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            winner_text = title_font.render(f"{winner} ПОБЕДИЛ!", True, YELLOW)
            screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            restart_text = font.render("Нажми R для реванша, ESC для выхода", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()