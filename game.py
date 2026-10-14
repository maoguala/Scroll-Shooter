import random
import sys

import pygame
WIDTH, HEIGHT = 480, 640
FPS = 60
PLAYER_SPEED = 7
BULLET_SPEED = 20
SHOTGUN_PELLETS = 5
SHOTGUN_SPREAD = 5
SHOTGUN_COOLDOWN = 20
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 11
SPAWN_ENEMY = pygame.USEREVENT + 10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scroll Shooter")
clock = pygame.time.Clock()
class BitmapFont:
	GLYPHS = {
		"0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
		"1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
		"2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
		"3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
		"4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
		"5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
		"6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
		"7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
		"8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
		"9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
		"A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
		"E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
		"G": ("01110", "10001", "10000", "10011", "10001", "10001", "01110"),
		"M": ("10001", "11011", "10101", "10001", "10001", "10001", "10001"),
		"O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
		"R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
		"V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100"),
		" ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
	}
	def __init__(self, scale=4, spacing=1):
		self.scale = scale
		self.spacing = spacing
	def measure_text(self, text, scale=None):
		scale = self.scale if scale is None else scale
		char_width = 5 * scale
		char_height = 7 * scale
		spacing = self.spacing * scale
		if not text:
			return 0, char_height
		width = len(text) * (char_width + spacing) - spacing
		return width, char_height
	def draw_text(self, surface, text, x, y, color=(255, 255, 255), center=False, scale=None):
		scale = self.scale if scale is None else scale
		char_width = 5 * scale
		char_height = 7 * scale
		spacing = self.spacing * scale
		text = text.upper()
		width = len(text) * (char_width + spacing) - spacing if text else 0
		start_x = x - width // 2 if center else x
		start_y = y - char_height // 2 if center else y
		for index, char in enumerate(text):
			pattern = self.GLYPHS.get(char, self.GLYPHS[" "])
			char_x = start_x + index * (char_width + spacing)
			for row, bits in enumerate(pattern):
				for col, bit in enumerate(bits):
					if bit == "1":
						rect = pygame.Rect(char_x + col * scale, start_y + row * scale, scale, scale)
						pygame.draw.rect(surface, color, rect)

def draw_heart(surface, x, y, size, color):
	radius = size // 4
	left_center = (x + radius, y + radius)
	right_center = (x + size - radius, y + radius)
	bottom_point = (x + size // 2, y + size)
	top_left = (x, y + radius)
	top_right = (x + size, y + radius)
	pygame.draw.circle(surface, color, left_center, radius)
	pygame.draw.circle(surface, color, right_center, radius)
	pygame.draw.polygon(surface, color, [top_left, top_right, bottom_point])

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = self._create_fly_image()
		self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
		self.cooldown = 0
		self.special_cooldown = 0
		self.lives = 3
		self.exploded = False

	def _create_fly_image(self):
		image = pygame.Surface((34, 28), pygame.SRCALPHA)
		pygame.draw.polygon(image, (80, 220, 255), [(17, 0), (31, 8), (26, 28), (17, 22), (8, 28), (3, 8)])
		pygame.draw.polygon(image, (255, 255, 255), [(17, 5), (22, 15), (17, 20), (12, 15)])
		return image

	def _create_fireball_image(self):
		image = pygame.Surface((46, 46), pygame.SRCALPHA)
		center = (23, 23)
		for radius, color in ((22, (255, 90, 0)), (18, (255, 160, 0)), (12, (255, 230, 80))):
			pygame.draw.circle(image, color, center, radius)
		pygame.draw.circle(image, (255, 255, 255), (18, 18), 4)
		pygame.draw.circle(image, (255, 120, 40), (30, 14), 5)
		pygame.draw.circle(image, (255, 120, 40), (13, 30), 4)
		return image

	def explode(self):
		if self.exploded:
			return

		center = self.rect.center
		self.image = self._create_fireball_image()
		self.rect = self.image.get_rect(center=center)
		self.exploded = True

	def update(self, keys, bounds_rect):
		dx = 0
		dy = 0
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			dx -= PLAYER_SPEED
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			dx += PLAYER_SPEED
		if keys[pygame.K_UP] or keys[pygame.K_w]:
			dy -= PLAYER_SPEED
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			dy += PLAYER_SPEED

		self.rect.x += dx
		self.rect.y += dy
		self.rect.clamp_ip(bounds_rect)
		self.cooldown = max(0, self.cooldown - 1)
		self.special_cooldown = max(0, self.special_cooldown - 1)

	def shoot(self, bullets, all_sprites):
		if self.cooldown == 0:
			bullet = Bullet(self.rect.centerx, self.rect.top)
			bullets.add(bullet)
			all_sprites.add(bullet)
			self.cooldown = 10

	def shoot_shotgun(self, bullets, all_sprites):
		if self.special_cooldown != 0:
			return

		spread_values = [-2, -1, 0, 1, 2]
		for offset in spread_values[:SHOTGUN_PELLETS]:
			bullet = Bullet(self.rect.centerx, self.rect.top, velocity_x=offset * SHOTGUN_SPREAD)
			bullets.add(bullet)
			all_sprites.add(bullet)
		self.special_cooldown = SHOTGUN_COOLDOWN

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, velocity_x=0):
		super().__init__()
		self.image = pygame.Surface((6, 14), pygame.SRCALPHA)
		pygame.draw.rect(self.image, (255, 230, 120), (0, 0, 6, 14), border_radius=3)
		self.rect = self.image.get_rect(midbottom=(x, y))
		self.velocity_x = velocity_x

	def update(self):
		self.rect.x += self.velocity_x
		self.rect.y -= BULLET_SPEED
		if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > WIDTH:
			self.kill()

class Enemy(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.size = random.randint(22, 42)
		self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		color = random.choice([(255, 100, 100), (255, 170, 60), (200, 80, 255)])
		pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
		pygame.draw.circle(self.image, (35, 35, 35), (self.size // 2, self.size // 2), self.size // 4)
		self.rect = self.image.get_rect(midtop=(random.randint(20, WIDTH - 20), -self.size))
		self.speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
		self.drift = random.choice([-2, -1, 0, 1, 2])

	def update(self):
		self.rect.y += self.speed
		self.rect.x += self.drift
		if self.rect.top > HEIGHT or self.rect.left > WIDTH + 20 or self.rect.right < -20:
			self.kill()

class EnemyFactory:
	def create_enemy(self):
		return Enemy()

class GameWorld:
	def __init__(self, enemy_factory):
		self.enemy_factory = enemy_factory
		self.bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
		self.reset()

	def reset(self):
		self.all_sprites = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.player = Player()
		self.all_sprites.add(self.player)
		self.score = 0
		self.game_over = False

	def spawn_enemy(self):
		enemy = self.enemy_factory.create_enemy()
		self.enemies.add(enemy)
		self.all_sprites.add(enemy)

	def update(self, keys):
		if self.game_over:
			return

		self.player.update(keys, self.bounds)
		if keys[pygame.K_SPACE]:
			self.player.shoot(self.bullets, self.all_sprites)

		self.bullets.update()
		self.enemies.update()

		hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
		if hits:
			self.score += 10 * len(hits)

		if pygame.sprite.spritecollide(self.player, self.enemies, True):
			self.player.lives -= 1
			if self.player.lives <= 0:
				self.player.explode()
				self.game_over = True

class HUDRenderer:
	def __init__(self, font):
		self.font = font

	def draw_hearts(self, surface, lives):
		heart_size = 16
		spacing = 6
		for index in range(3):
			x = 10 + index * (heart_size + spacing)
			color = (255, 70, 70) if index < lives else (80, 50, 50)
			draw_heart(surface, x, 10, heart_size, color)

	def draw_score(self, surface, score):
		score_text = str(score)
		width, _ = self.font.measure_text(score_text, scale=3)
		self.font.draw_text(surface, score_text, WIDTH - width - 12, 10, color=(255, 255, 255), scale=3)

	def draw(self, surface, score, lives):
		self.draw_hearts(surface, lives)
		self.draw_score(surface, score)

class GameRenderer:
	def __init__(self, font):
		self.font = font
		self.hud = HUDRenderer(font)
		self.bg1 = 0
		self.bg2 = -HEIGHT

	def update_background(self, active):
		if not active:
			return

		self.bg1 += 2
		self.bg2 += 2
		if self.bg1 >= HEIGHT:
			self.bg1 = -HEIGHT
		if self.bg2 >= HEIGHT:
			self.bg2 = -HEIGHT

	def draw_background(self, surface):
		for y in (self.bg1, self.bg2):
			for x in range(0, WIDTH, 24):
				pygame.draw.circle(surface, (30, 30, 50), (x + 12, y % HEIGHT), 1)
				pygame.draw.circle(surface, (25, 25, 40), (x + 6, (y * 1.5) % HEIGHT), 1)

	def render(self, surface, world):
		self.update_background(not world.game_over)
		surface.fill((10, 10, 25))
		self.draw_background(surface)
		world.all_sprites.draw(surface)
		self.hud.draw(surface, world.score, world.player.lives)
		if world.game_over:
			self.font.draw_text(surface, "GAMEOVER", WIDTH // 2, HEIGHT // 2, color=(255, 255, 255), center=True, scale=8)

class GameState:
	def handle_event(self, event, game):
		return

	def update(self, game, keys):
		return

class PlayingState(GameState):
	def handle_event(self, event, game):
		if event.type == SPAWN_ENEMY:
			game.world.spawn_enemy()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
			game.world.player.shoot_shotgun(game.world.bullets, game.world.all_sprites)

	def update(self, game, keys):
		game.world.update(keys)
		if game.world.game_over:
			game.state = GameOverState()

class GameOverState(GameState):
	def handle_event(self, event, game):
		if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
			game.restart()

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption("Scroll Shooter")
		self.clock = pygame.time.Clock()
		self.font = BitmapFont()
		self.world = GameWorld(EnemyFactory())
		self.renderer = GameRenderer(self.font)
		self.state = PlayingState()
		pygame.time.set_timer(SPAWN_ENEMY, 550)

	def restart(self):
		self.world.reset()
		self.state = PlayingState()

	def run(self):
		running = True
		while running:
			self.clock.tick(FPS)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					running = False
				else:
					self.state.handle_event(event, self)

			keys = pygame.key.get_pressed()
			self.state.update(self, keys)
			self.renderer.render(self.screen, self.world)
			pygame.display.flip()

		pygame.quit()
		sys.exit()

def main():
	Game().run()

if __name__ == "__main__":
	main()
import random
import sys

import pygame


WIDTH, HEIGHT = 480, 640
FPS = 60
PLAYER_SPEED = 3
BULLET_SPEED = 1
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 5
SPAWN_ENEMY = pygame.USEREVENT + 10


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scroll Shooter")
clock = pygame.time.Clock()



def draw_text(text, x, y, color=(255, 255, 255), center=False, big=False):
	return


GAME_OVER_GLYPHS = {
	"A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
	"E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
	"G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
	"M": ("10001", "11011", "10101", "10001", "10001", "10001", "10001"),
	"O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
	"R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
	"V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100"),
	" ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def draw_game_over_text(surface, text, center_x, center_y, color=(255, 255, 255)):
	lines = text.upper().splitlines()
	scale = 6
	char_width = 5 * scale
	char_height = 7 * scale
	line_gap = 10
	total_height = len(lines) * char_height + max(0, len(lines) - 1) * line_gap
	start_y = center_y - total_height // 2

	for line_index, line in enumerate(lines):
		line_width = len(line) * (char_width + scale) - scale if line else 0
		start_x = center_x - line_width // 2
		y = start_y + line_index * (char_height + line_gap)
		for char_index, char in enumerate(line):
			pattern = GAME_OVER_GLYPHS.get(char, GAME_OVER_GLYPHS[" "])
			x = start_x + char_index * (char_width + scale)
			for row, bits in enumerate(pattern):
				for col, bit in enumerate(bits):
					if bit == "1":
						rect = pygame.Rect(x + col * scale, y + row * scale, scale, scale)
						pygame.draw.rect(surface, color, rect)


def draw_heart(surface, x, y, size, color):
	radius = size // 4
	left_center = (x + radius, y + radius)
	right_center = (x + size - radius, y + radius)
	bottom_point = (x + size // 2, y + size)
	top_left = (x, y + radius)
	top_right = (x + size, y + radius)
	pygame.draw.circle(surface, color, left_center, radius)
	pygame.draw.circle(surface, color, right_center, radius)
	pygame.draw.polygon(surface, color, [top_left, top_right, bottom_point])


def draw_hp(surface, lives):
	heart_size = 16
	spacing = 6
	for index in range(3):
		x = 10 + index * (heart_size + spacing)
		color = (255, 70, 70) if index < lives else (80, 50, 50)
		draw_heart(surface, x, 10, heart_size, color)


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pygame.Surface((34, 28), pygame.SRCALPHA)
		pygame.draw.polygon(self.image, (80, 220, 255), [(0, 14), (24, 0), (34, 14), (24, 28)])
		pygame.draw.polygon(self.image, (255, 255, 255), [(7, 10), (18, 14), (7, 18)])
		self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
		self.cooldown = 0
		self.lives = 3

	def update(self, keys):
		dx = dy = 0
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			dx -= PLAYER_SPEED
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			dx += PLAYER_SPEED
		if keys[pygame.K_UP] or keys[pygame.K_w]:
			dy -= PLAYER_SPEED
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			dy += PLAYER_SPEED

		self.rect.x += dx
		self.rect.y += dy
		self.rect.clamp_ip(screen.get_rect())
		self.cooldown = max(0, self.cooldown - 1)

	def shoot(self, bullets, all_sprites):
		if self.cooldown == 0:
			bullet = Bullet(self.rect.centerx, self.rect.top)
			bullets.add(bullet)
			all_sprites.add(bullet)
			self.cooldown = 10


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((6, 14), pygame.SRCALPHA)
		pygame.draw.rect(self.image, (255, 230, 120), (0, 0, 6, 14), border_radius=3)
		self.rect = self.image.get_rect(midbottom=(x, y))

	def update(self):
		self.rect.y -= BULLET_SPEED
		if self.rect.bottom < 0:
			self.kill()


class Enemy(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.size = random.randint(22, 42)
		self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
		color = random.choice([(255, 100, 100), (255, 170, 60), (200, 80, 255)])
		pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
		pygame.draw.circle(self.image, (35, 35, 35), (self.size // 2, self.size // 2), self.size // 4)
		self.rect = self.image.get_rect(midtop=(random.randint(20, WIDTH - 20), -self.size))
		self.speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
		self.drift = random.choice([-2, -1, 0, 1, 2])

	def update(self):
		self.rect.y += self.speed
		self.rect.x += self.drift
		if self.rect.top > HEIGHT or self.rect.left > WIDTH + 20 or self.rect.right < -20:
			self.kill()


def reset_game():
	all_sprites = pygame.sprite.Group()
	bullets = pygame.sprite.Group()
	enemies = pygame.sprite.Group()
	player = Player()
	all_sprites.add(player)
	return all_sprites, bullets, enemies, player, 0, False


def main():
	all_sprites, bullets, enemies, player, score, game_over = reset_game()
	pygame.time.set_timer(SPAWN_ENEMY, 550)
	bg1 = 0
	bg2 = -HEIGHT

	running = True
	while running:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				elif event.key == pygame.K_r and game_over:
					all_sprites, bullets, enemies, player, score, game_over = reset_game()
				elif event.key == pygame.K_SPACE and not game_over:
					player.shoot(bullets, all_sprites)
			elif event.type == SPAWN_ENEMY and not game_over:
				enemy = Enemy()
				enemies.add(enemy)
				all_sprites.add(enemy)

		keys = pygame.key.get_pressed()
		if not game_over:
			player.update(keys)
			if keys[pygame.K_SPACE]:
				player.shoot(bullets, all_sprites)

			bullets.update()
			enemies.update()

			hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
			if hits:
				score += 10 * len(hits)

			if pygame.sprite.spritecollide(player, enemies, True):
				player.lives -= 1
				if player.lives <= 0:
					game_over = True

			bg1 += 2
			bg2 += 2
			if bg1 >= HEIGHT:
				bg1 = -HEIGHT
			if bg2 >= HEIGHT:
				bg2 = -HEIGHT

		screen.fill((10, 10, 25))
		for y in (bg1, bg2):
			for x in range(0, WIDTH, 24):
				pygame.draw.circle(screen, (30, 30, 50), (x + 12, y % HEIGHT), 1)
				pygame.draw.circle(screen, (25, 25, 40), (x + 6, (y * 1.5) % HEIGHT), 1)

		all_sprites.draw(screen)
		draw_hp(screen, player.lives)
		draw_text(f"Score: {score}", 12, 10)
		draw_text(f"Lives: {player.lives}", 12, 36)
		draw_text("Arrows/WASD move, Space shoots", WIDTH // 2, HEIGHT - 24, color=(180, 180, 200), center=True)

		if game_over:
			draw_game_over_text(screen, "GAME OVER", WIDTH // 2, HEIGHT // 2, color=(255, 255, 255))

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
