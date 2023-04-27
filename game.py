import arcade
import random
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Zelda and Link Inspired Adventure Game"

HERO_IMAGE = "/Users/jorgie/Desktop/Mimo/pythonGame/images/Hero_1st_gen.png"
MONSTER_IMAGE = "/Users/jorgie/Desktop/Mimo/pythonGame/images/Monster_1st_gen.png"
TREASURE_IMAGE = "/Users/jorgie/Desktop/Mimo/pythonGame/images/Treasure_1st_gen.png"

LIFE_BAR_WIDTH = 150
LIFE_BAR_HEIGHT = 20


class Hero(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.life = 100
        self.score = 0
        self.attacking = False
        self.last_attack = -5  # Initialize last attack time to negative to avoid initial cooldown
        self.attack_duration = 2  # Attack lasts 2 seconds
        self.invincible = False  # Hero can't take damage while attacking
        self.last_hit_time = -5  # Initialize last hit time to negative to avoid initial cooldown

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check if the attack duration has expired
        if self.attacking and time.time() - self.last_attack > self.attack_duration:
            self.end_attack()

        # Check if the invincibility has expired
        if self.invincible and time.time() - self.last_hit_time > self.attack_duration:
            self.invincible = False

    def start_attack(self):
        if time.time() - self.last_attack > 2:  # 5 second cooldown
            self.attacking = True
            self.last_attack = time.time()
            self.invincible = True

    def end_attack(self):
        self.attacking = False
        self.invincible = False

    def take_damage(self, amount):
        if not self.invincible:
            self.life -= amount
            self.last_hit_time = time.time()


class Monster(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.speed = random.randint(1, 3)

    def update(self):
        self.center_x += self.speed * random.choice([-1, 1])
        self.center_y += self.speed * random.choice([-1, 1])

        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class Treasure(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.points = random.randint(10, 50)

    def on_collect(self):
        self.kill()
        return self.points


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.hero = None
        self.monsters = None
        self.treasures = None
        self.elapsed_time = 0
        self.monster_spawn_timer = 0
        self.monsters_to_spawn = 2

        self.setup()

    def on_show(self):
        self.set_mouse_visible(False)

    def setup(self):
        self.hero = Hero(HERO_IMAGE, 0.1667)
        self.hero.center_x = SCREEN_WIDTH // 2
        self.hero.center_y = SCREEN_HEIGHT // 2

        self.monsters = arcade.SpriteList()
        for i in range(self.monsters_to_spawn):
            monster = Monster(MONSTER_IMAGE, 0.1667)
            monster.center_x = random.randint(0, SCREEN_WIDTH)
            monster.center_y = random.randint(0, SCREEN_HEIGHT)
            self.monsters.append(monster)

        self.treasures = arcade.SpriteList()
        for i in range(3):
            treasure = Treasure(TREASURE_IMAGE, 0.1667)
            treasure.center_x = random.randint(0, SCREEN_WIDTH)
            treasure.center_y = random.randint(0, SCREEN_HEIGHT)
            self.treasures.append(treasure)

    def update(self, delta_time):
        if self.hero.life <= 0:
            # Stop all character movement
            self.hero.change_x = 0
            self.hero.change_y = 0
            for monster in self.monsters:
                monster.change_x = 0
                monster.change_y = 0

            # Display "Game Over" message
            arcade.draw_text(
                "Game Over, press Space to restart game",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                font_size=50,
                anchor_x="center")
        else:
            self.hero.update()

            # Update elapsed time
            self.elapsed_time += delta_time
            self.monster_spawn_timer += delta_time

            # Check if 5 seconds have passed
            if self.elapsed_time >= 5:
                # Spawn monsters
                for _ in range(self.monsters_to_spawn):
                    monster = Monster(MONSTER_IMAGE, 0.1667)
                    monster.center_x = random.randint(0, SCREEN_WIDTH)
                    monster.center_y = random.randint(0, SCREEN_HEIGHT)
                    self.monsters.append(monster)

                # Spawn a new treasure
                treasure = Treasure(TREASURE_IMAGE, 0.1667)
                treasure.center_x = random.randint(0, SCREEN_WIDTH)
                treasure.center_y = random.randint(0, SCREEN_HEIGHT)
                self.treasures.append(treasure)

                # Reset elapsed time
                self.elapsed_time = 0

            # Check if 20 seconds have passed
            if self.monster_spawn_timer >= 20:
                self.monsters_to_spawn += 1
                self.monster_spawn_timer = 0

            for monster in self.monsters:
                monster.update()

            monsters_hit_list = arcade.check_for_collision_with_list(
                self.hero, self.monsters)
            for monster in monsters_hit_list:
                if self.hero.attacking:
                    monster.kill()
                    self.hero.score += 10
                    self.hero.life += 1
                    if self.hero.life > 100:
                        self.hero.life = 100
                else:
                    self.hero.life -= 3

            treasures_hit_list = arcade.check_for_collision_with_list(
                self.hero, self.treasures)
            for treasure in treasures_hit_list:
                points = treasure.on_collect()
                self.hero.score += points

            # End the hero attack animation after 1 second
            if self.hero.attacking and time.time() - self.hero.last_attack > 1:
                self.hero.end_attack()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.hero.change_y = 5
        elif key == arcade.key.S:
            self.hero.change_y = -5
        elif key == arcade.key.A:
            self.hero.change_x = -5
        elif key == arcade.key.D:
            self.hero.change_x = 5
        elif key == arcade.key.SPACE:
            self.hero.start_attack()

        # Restart the game if the space bar is pressed and the game is over
        if key == arcade.key.SPACE and self.hero.life <= 0:
            self.setup()
            # Close the game if the ESC key is pressed and the game is over
        if key == arcade.key.ESCAPE and self.hero.life <= 0:
            arcade.close_window()



    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.S:
            self.hero.change_y = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.hero.change_x = 0
        elif key == arcade.key.SPACE:
            self.hero.end_attack()

    def on_draw(self):
        arcade.start_render()

        if self.hero.life > 0:
            # Draw hero, monsters, and treasures
            self.hero.draw()
            self.monsters.draw()
            self.treasures.draw()

            # Draw life bar
            life_bar_width = LIFE_BAR_WIDTH * (self.hero.life / 100)
            life_bar_center_x = life_bar_width / 2
            life_bar_center_y = SCREEN_HEIGHT - LIFE_BAR_HEIGHT / 2
            arcade.draw_rectangle_filled(
                life_bar_center_x,
                life_bar_center_y,
                life_bar_width,
                LIFE_BAR_HEIGHT,
                arcade.color.RED)

            # Draw score text
            score_text = f"Score: {self.hero.score}"
            arcade.draw_text(
                score_text,
                10,
                SCREEN_HEIGHT - 40,
                arcade.color.WHITE,
                18)
        else:
            # Stop all character movement
            self.hero.change_x = 0
            self.hero.change_y = 0
            for monster in self.monsters:
                monster.change_x = 0
                monster.change_y = 0

            # Display "Game Over" message
            arcade.draw_text(
                "Game Over",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                font_size=50,
                anchor_x="center")

            
# Create a new window instance
game_window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

# Start the game loop
arcade.run()
            
