"""
================================================================
  KAY´S KULEBRITA QUEST  —  NEON ARCADE EDITION  (v2)
  Single-file pygame-ce game.  Spanglish UI.  CRT vibes.
================================================================

WHAT'S NEW IN v2
----------------
1.  Pantalla de inicio = imagen `assets/images/start.png`
2.  Frutas especiales cada 5 manzanas:
        banana (5)  →  mandarina (10)  →  mango (15)
        fresa (20)  →  uva (25)        →  ciclo se repite
3.  Cada 5 manzanas también aparece una figura tipo Tetris con
    forma de letra (K · A · Y · C · I · M · A · R · V · A · L),
    con la fruta especial en el CENTRO de la figura → más difícil.
4.  Al completar las 11 letras → pantalla de victoria con
    `assets/images/win.png`.
5.  Controles táctiles (D-pad + Pause) para móvil / pygbag.

ESTRUCTURA DE ARCHIVOS
----------------------
    main.py
    assets/
        images/
            start.png      ← portada (INSERT COIN)
            win.png        ← pantalla de victoria
        music/
            theme.wav      ← (opcional) música de fondo

CÓMO CORRER
-----------
Local (Windows / Mac / Linux):
    pip install pygame-ce
    python main.py

En el navegador (móvil incluído):
    pip install pygbag
    pygbag main.py
    # abre http://localhost:8000

CONTROLES
---------
    SPACE / TAP      Start / Restart
    Arrows / WASD    Mover (teclado)
    D-PAD (en pantalla)  Mover (móvil / mouse)
    P / botón ||     Pause
    ESC              Volver al menú / Salir desde el menú
"""

import asyncio
import math
import os
import random
import pygame


# ==========================================================================
# 🎨   CONFIGURACIÓN  /  CONFIGURATION
# Cambia estos valores para personalizar el juego.
# ==========================================================================

# ---- Textos (Spanglish) -------------------------------------------------
GAME_TITLE     = "KAY´S KULEBRITA QUEST"
SUBTITLE       = "* NEON ARCADE EDITION *"
TEXT_INSERT    = "INSERT COIN"
TEXT_START     = "PRESS SPACE / TAP TO START"
TEXT_SCORE     = "SCORE"
TEXT_HISCORE   = "HI-SCORE"
TEXT_LEVEL     = "LEVEL"
TEXT_GAMEOVER  = "GAME OVER, BRO!"
TEXT_RESTART   = "TAP / SPACE - PLAY AGAIN"
TEXT_PAUSED    = "PAUSADO"
TEXT_RESUME    = "TAP || / PRESS P TO RESUME"
TEXT_CONTROLS  = "WASD / ARROWS - MOVE     P - PAUSE     ESC - EXIT"
TEXT_PRESS     = "▶  TAP TO PLAY  ◀"
TEXT_WIN_BIG   = "FELICIDADES BRO!  GANASTE"
TEXT_PROGRESS  = "WORD"

# ---- Ventana / Window ---------------------------------------------------
INITIAL_WIDTH  = 960
INITIAL_HEIGHT = 720
WINDOW_TITLE   = "Kay´s Kulebrita Quest"
TARGET_FPS     = 60

# ---- Tablero / Grid -----------------------------------------------------
GRID_COLS = 28
GRID_ROWS = 20

# ---- Velocidad / Speed --------------------------------------------------
INITIAL_MOVE_DELAY_MS = 140
MIN_MOVE_DELAY_MS     = 55
SPEED_UP_PER_LEVEL_MS = 8

# ---- Frutas, letras y dificultad progresiva ----------------------------
APPLES_PER_LETTER = 5   # cada N manzanas → letra nueva + fruta especial + sube nivel
LETTERS_SEQUENCE  = "KAYCIMARVAL"  # 11 letras a deletrear para ganar

# Tabla de frutas. Cambia points, color, glow.
FRUIT_TYPES = {
    "apple":     {"points": 10, "color": (255, 60,  110), "glow": (255, 110, 160)},
    "banana":    {"points": 5,  "color": (255, 215, 60),  "glow": (255, 240, 130)},
    "mandarina": {"points": 10, "color": (255, 150, 50),  "glow": (255, 200, 100)},
    "mango":     {"points": 15, "color": (255, 110, 60),  "glow": (255, 180, 100)},
    "fresa":     {"points": 20, "color": (220, 40,  70),  "glow": (255, 100, 130)},
    "uva":       {"points": 25, "color": (160, 90,  220), "glow": (200, 140, 240)},
}
# Orden cíclico (se repite si hay más letras que frutas).
SPECIAL_FRUIT_ORDER = ["banana", "mandarina", "mango", "fresa", "uva"]

# ---- Letras tipo Tetris -------------------------------------------------
LETTER_SCALE        = 2  # Cada '#' se vuelve un bloque LETTER_SCALE×LETTER_SCALE.
COLOR_OBSTACLE      = (170, 70, 230)
COLOR_OBSTACLE_GLOW = (210, 130, 255)

# Patrones base (5 ancho × 9 alto). Scaled ×2 → 10×18 grid cells (≈32% del tablero).
LETTER_BASE_PATTERNS = {
    "K": [
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "##...",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ],
    "A": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
    ],
    "Y": [
        "#...#",
        ".#.#.",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "C": [
        ".####",
        "##..#",
        "##...",
        "##...",
        "##...",
        "##...",
        "##...",
        "##..#",
        ".####",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "M": [
        "#...#",
        "##.##",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
    ],
    "R": [
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#..#.",
        "#...#",
    ],
    "V": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        ".#.#.",
        ".#.#.",
        "..#..",
        "..#..",
    ],
    "L": [
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ],
}

# ---- Colores neón / Neon palette (R, G, B) -----------------------------
COLOR_BG           = (8,   6,  24)
COLOR_GRID_DIM     = (24, 18,  60)
COLOR_GRID_BRIGHT  = (40, 30, 100)
COLOR_BORDER       = (180, 90, 255)
COLOR_BORDER_GLOW  = (120, 60, 220)

COLOR_SNAKE_HEAD   = (170, 255, 200)
COLOR_SNAKE_BODY   = (40,  230, 140)
COLOR_SNAKE_GLOW   = (40,  255, 180)

COLOR_TEXT_PINK    = (255, 80,  200)
COLOR_TEXT_CYAN    = (90,  230, 255)
COLOR_TEXT_YELLOW  = (255, 230, 80)
COLOR_TEXT_WHITE   = (240, 240, 255)
COLOR_TEXT_DIM     = (110, 110, 140)

# ---- Efecto CRT ---------------------------------------------------------
CRT_ENABLED        = True
SCANLINE_SPACING   = 3
SCANLINE_ALPHA     = 55
VIGNETTE_ENABLED   = True

# ---- Audio --------------------------------------------------------------
AUDIO_ENABLED      = True
MUSIC_VOLUME       = 0.4
SFX_VOLUME         = 0.5
MUSIC_FILE         = os.path.join("assets", "music", "theme.wav")

# ---- Imágenes -----------------------------------------------------------
IMAGE_START_PATH   = os.path.join("assets", "images", "start.png")
IMAGE_WIN_PATH     = os.path.join("assets", "images", "win.png")

# ---- Controles táctiles (móvil) ----------------------------------------
SHOW_TOUCH_CONTROLS = True     # False = solo teclado (puro desktop)
TOUCH_ALPHA         = 150      # 0..255  Transparencia del fondo de botones
TOUCH_BUTTON_COLOR  = (20, 14, 50)         # fondo del botón
TOUCH_BORDER_COLOR  = (180, 90, 255)       # borde
TOUCH_GLOW_COLOR    = (140, 220, 255)      # halo
TOUCH_ICON_COLOR    = (220, 240, 255)      # flechas / símbolos


# ==========================================================================
#   IMPLEMENTACIÓN  —  Modifica con cuidado a partir de aquí
# ==========================================================================

# Direcciones (dx, dy)
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# Estados de juego
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_PAUSED    = "paused"
STATE_GAMEOVER  = "gameover"
STATE_WIN       = "win"


# --------------------------------------------------------------------------
#   GENERACIÓN DE SONIDO  /  SOUND GENERATION
# --------------------------------------------------------------------------

def generate_tone(frequency=440, duration_ms=120, volume=0.3, wave="square"):
    """Genera un beep simple. Devuelve pygame.mixer.Sound (o None)."""
    try:
        sample_rate = 22050
        n = max(1, int(sample_rate * duration_ms / 1000))
        buf = bytearray()
        for i in range(n):
            t = i / sample_rate
            if wave == "square":
                s = 1.0 if (frequency * t) % 1.0 < 0.5 else -1.0
            elif wave == "triangle":
                phase = (frequency * t) % 1.0
                s = 4 * abs(phase - 0.5) - 1
            elif wave == "sawtooth":
                phase = (frequency * t) % 1.0
                s = 2 * phase - 1
            else:
                s = math.sin(2 * math.pi * frequency * t)
            attack = min(1.0, i / max(1, sample_rate * 0.005))
            decay = max(0.0, 1.0 - i / n) ** 1.5
            sample = int(32767 * volume * s * attack * decay)
            sample = max(-32767, min(32767, sample))
            data = sample.to_bytes(2, "little", signed=True)
            buf += data + data
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception as exc:
        print(f"[sound] tone gen failed: {exc}")
        return None


def generate_arpeggio(frequencies, note_ms=80, volume=0.3, wave="square"):
    """Encadena varias notas en un solo Sound (efecto melódico)."""
    try:
        sample_rate = 22050
        buf = bytearray()
        for f in frequencies:
            n = max(1, int(sample_rate * note_ms / 1000))
            for i in range(n):
                t = i / sample_rate
                if wave == "square":
                    s = 1.0 if (f * t) % 1.0 < 0.5 else -1.0
                elif wave == "triangle":
                    phase = (f * t) % 1.0
                    s = 4 * abs(phase - 0.5) - 1
                else:
                    s = math.sin(2 * math.pi * f * t)
                attack = min(1.0, i / max(1, sample_rate * 0.005))
                decay = max(0.0, 1.0 - i / n) ** 1.3
                sample = int(32767 * volume * s * attack * decay)
                sample = max(-32767, min(32767, sample))
                data = sample.to_bytes(2, "little", signed=True)
                buf += data + data
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception as exc:
        print(f"[sound] arp gen failed: {exc}")
        return None


# --------------------------------------------------------------------------
#   LETRAS TETRIS  /  Helpers
# --------------------------------------------------------------------------

def build_letter_cells(letter):
    """Devuelve (cells_set, bbox_rect) con las celdas que ocupa la letra
    ya centrada en el grid y escalada por LETTER_SCALE."""
    pattern = LETTER_BASE_PATTERNS.get(letter)
    if not pattern:
        return set(), None
    base_h = len(pattern)
    base_w = len(pattern[0])
    scale = LETTER_SCALE
    final_w = base_w * scale
    final_h = base_h * scale
    x0 = (GRID_COLS - final_w) // 2
    y0 = (GRID_ROWS - final_h) // 2
    cells = set()
    for by, row in enumerate(pattern):
        for bx, ch in enumerate(row):
            if ch == '#':
                for sx in range(scale):
                    for sy in range(scale):
                        cells.add((x0 + bx * scale + sx,
                                   y0 + by * scale + sy))
    bbox = pygame.Rect(x0, y0, final_w, final_h)
    return cells, bbox


def nearest_empty_cell(target, forbidden):
    """Devuelve la celda libre más cercana a `target` en el grid."""
    tx, ty = target
    best = None
    best_d = float('inf')
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            if (x, y) in forbidden:
                continue
            d = (x - tx) ** 2 + (y - ty) ** 2
            if d < best_d:
                best_d = d
                best = (x, y)
    return best


# --------------------------------------------------------------------------
#   CLASE PRINCIPAL DEL JUEGO  /  MAIN GAME CLASS
# --------------------------------------------------------------------------

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (INITIAL_WIDTH, INITIAL_HEIGHT),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption(WINDOW_TITLE)
        self.width = INITIAL_WIDTH
        self.height = INITIAL_HEIGHT
        self.clock = pygame.time.Clock()

        self._init_fonts()

        self.sounds = {}
        self._init_sounds()

        # Imágenes (portada y victoria)
        self.image_start = None
        self.image_win = None
        self._load_images()
        self.image_start_scaled = None
        self.image_win_scaled = None
        self._scale_images()

        self.crt_overlay = None
        self.vignette = None
        self._rebuild_overlays()

        # Estado de juego
        self.state = STATE_MENU
        self.high_score = 0
        self.reset()

        # Animaciones
        self.time_ms = 0
        self.blink_timer = 0
        # Botones táctiles "presionados" para feedback visual
        self.active_touch = None

    # ---------- Setup ----------

    def _init_fonts(self):
        self.font_huge   = pygame.font.Font(None, 96)
        self.font_big    = pygame.font.Font(None, 56)
        self.font_mid    = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 44)
        self.font_small  = pygame.font.Font(None, 24)
        self.font_tiny   = pygame.font.Font(None, 18)

    def _init_sounds(self):
        if not AUDIO_ENABLED:
            return
        try:
            self.sounds["eat"]      = generate_tone(880, 90, 0.35, "square")
            self.sounds["special"]  = generate_arpeggio([784, 988, 1175, 1568], 60, 0.40, "square")
            self.sounds["levelup"]  = generate_arpeggio([523, 659, 784, 1047], 70, 0.35, "square")
            self.sounds["gameover"] = generate_arpeggio([392, 330, 262, 196], 150, 0.40, "triangle")
            self.sounds["start"]    = generate_arpeggio([523, 784, 1047], 80, 0.35, "square")
            self.sounds["turn"]     = generate_tone(1100, 28, 0.12, "square")
            self.sounds["pause"]    = generate_tone(440, 80, 0.25, "triangle")
            self.sounds["win"]      = generate_arpeggio(
                [523, 659, 784, 1047, 1319, 1568, 2093], 100, 0.45, "square"
            )

            for snd in self.sounds.values():
                if snd is not None:
                    snd.set_volume(SFX_VOLUME)

            if os.path.exists(MUSIC_FILE):
                try:
                    pygame.mixer.music.load(MUSIC_FILE)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    pygame.mixer.music.play(-1)
                    print(f"[music] Reproduciendo {MUSIC_FILE}")
                except Exception as exc:
                    print(f"[music] No pude reproducir {MUSIC_FILE}: {exc}")
            else:
                print(f"[music] No hay música en {MUSIC_FILE} — corriendo sin música (OK).")
        except Exception as exc:
            print(f"[audio] init failed: {exc}")

    def play(self, name):
        snd = self.sounds.get(name)
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass

    def _load_images(self):
        for attr, path in [("image_start", IMAGE_START_PATH),
                           ("image_win",   IMAGE_WIN_PATH)]:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    setattr(self, attr, img)
                    print(f"[image] cargada {path}  ({img.get_width()}x{img.get_height()})")
                except Exception as exc:
                    print(f"[image] no pude cargar {path}: {exc}")
            else:
                print(f"[image] no encontrada {path} — usaré pantalla procedural.")

    def _scale_images(self):
        self.image_start_scaled = self._scale_to_fit(self.image_start)
        self.image_win_scaled   = self._scale_to_fit(self.image_win)

    def _scale_to_fit(self, image):
        if image is None:
            return None
        iw, ih = image.get_size()
        scale = min(self.width / iw, self.height / ih)
        sw = max(1, int(iw * scale))
        sh = max(1, int(ih * scale))
        return pygame.transform.smoothscale(image, (sw, sh))

    def _rebuild_overlays(self):
        if CRT_ENABLED:
            self.crt_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for y in range(0, self.height, SCANLINE_SPACING):
                pygame.draw.line(
                    self.crt_overlay,
                    (0, 0, 0, SCANLINE_ALPHA),
                    (0, y), (self.width, y),
                )
        else:
            self.crt_overlay = None

        if VIGNETTE_ENABLED:
            self.vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            steps = 36
            for i in range(steps):
                a = int(160 * (i / steps) ** 2)
                pad_x = int((self.width / 2) * (1 - i / steps))
                pad_y = int((self.height / 2) * (1 - i / steps))
                w = max(1, self.width - pad_x * 2)
                h = max(1, self.height - pad_y * 2)
                pygame.draw.rect(self.vignette, (0, 0, 0, a),
                                 (pad_x, pad_y, w, h), width=3)
        else:
            self.vignette = None

    def on_resize(self, w, h):
        self.width = max(420, w)
        self.height = max(320, h)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self._scale_images()
        self._rebuild_overlays()

    # ---------- Layout ----------

    @property
    def play_rect(self):
        margin_x = 30
        top_hud = 110
        bottom = 50
        avail_w = self.width - margin_x * 2
        avail_h = self.height - top_hud - bottom
        cs = max(6, min(avail_w // GRID_COLS, avail_h // GRID_ROWS))
        w = cs * GRID_COLS
        h = cs * GRID_ROWS
        x = (self.width - w) // 2
        y = top_hud + (avail_h - h) // 2
        return pygame.Rect(x, y, w, h), cs

    # ---------- Controles táctiles ----------

    def get_touch_button_size(self):
        """Tamaño de botón adaptativo según el alto de ventana."""
        return max(42, min(72, int(self.height / 11)))

    def get_touch_buttons(self):
        """Devuelve dict {nombre: pygame.Rect} con los botones táctiles."""
        if not SHOW_TOUCH_CONTROLS:
            return {}
        size = self.get_touch_button_size()
        gap = max(4, size // 14)
        margin = max(16, self.height // 30)

        # D-pad cruz (esquina inferior izquierda)
        pad_left = margin
        pad_bottom = self.height - margin
        cross_w = size * 3 + gap * 2
        cross_h = size * 3 + gap * 2
        pad_top = pad_bottom - cross_h

        col0 = pad_left
        col1 = pad_left + size + gap
        col2 = pad_left + (size + gap) * 2
        row0 = pad_top
        row1 = pad_top + size + gap
        row2 = pad_top + (size + gap) * 2

        return {
            "up":    pygame.Rect(col1, row0, size, size),
            "left":  pygame.Rect(col0, row1, size, size),
            "right": pygame.Rect(col2, row1, size, size),
            "down":  pygame.Rect(col1, row2, size, size),
            # Pause (esquina inferior derecha)
            "pause": pygame.Rect(
                self.width - margin - size,
                self.height - margin - size,
                size, size,
            ),
        }

    def draw_touch_controls(self):
        """Dibuja D-pad y botón pausa con estética neón translúcida."""
        if not SHOW_TOUCH_CONTROLS:
            return
        if self.state not in (STATE_PLAYING, STATE_PAUSED):
            return

        buttons = self.get_touch_buttons()
        for name, rect in buttons.items():
            is_active = (self.active_touch == name)
            # Fondo translúcido
            bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            alpha = TOUCH_ALPHA + (60 if is_active else 0)
            alpha = min(230, alpha)
            pygame.draw.rect(
                bg, (*TOUCH_BUTTON_COLOR, alpha),
                bg.get_rect(), border_radius=10,
            )
            self.screen.blit(bg, rect.topleft)
            # Halo neón externo
            pygame.draw.rect(self.screen, TOUCH_GLOW_COLOR,
                             rect.inflate(4, 4), width=1, border_radius=12)
            # Borde
            pygame.draw.rect(self.screen, TOUCH_BORDER_COLOR, rect,
                             width=2, border_radius=10)
            # Símbolo
            if name == "pause":
                symbol = "▶" if self.state == STATE_PAUSED else "II"
                icon_color = COLOR_TEXT_YELLOW
            elif name == "up":
                symbol = "▲"; icon_color = TOUCH_ICON_COLOR
            elif name == "down":
                symbol = "▼"; icon_color = TOUCH_ICON_COLOR
            elif name == "left":
                symbol = "◀"; icon_color = TOUCH_ICON_COLOR
            elif name == "right":
                symbol = "▶"; icon_color = TOUCH_ICON_COLOR
            else:
                symbol = "?"; icon_color = TOUCH_ICON_COLOR
            txt = self.font_button.render(symbol, True, icon_color)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    def handle_pointer_down(self, pos):
        """Procesa un mousedown / tap. Devuelve action name o None."""
        # En menú / game over / win, tap en cualquier parte = restart
        if self.state in (STATE_MENU, STATE_GAMEOVER, STATE_WIN):
            return "start"
        if SHOW_TOUCH_CONTROLS:
            for name, rect in self.get_touch_buttons().items():
                if rect.collidepoint(pos):
                    self.active_touch = name
                    return name
        return None

    def handle_pointer_up(self):
        self.active_touch = None

    # ---------- Lógica de juego ----------

    def reset(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        # Snake: lista de celdas. Último elemento = CABEZA.
        self.snake = [(cx - 2, cy), (cx - 1, cy), (cx, cy)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.level = 1
        self.move_delay = INITIAL_MOVE_DELAY_MS
        self.move_timer = 0

        # Progresión
        self.apples_eaten   = 0
        self.letter_index   = 0
        self.obstacle_cells = set()
        self.special_active = False

        # Fruta inicial = manzana
        self.fruit_kind = "apple"
        self.fruit_cell = self._random_empty_cell()
        self.fruit_pulse = 0.0

    def _random_empty_cell(self):
        forbidden = set(self.snake) | self.obstacle_cells
        empties = [(x, y) for x in range(GRID_COLS)
                          for y in range(GRID_ROWS)
                          if (x, y) not in forbidden]
        if not empties:
            return None
        return random.choice(empties)

    def try_set_direction(self, new_dir):
        if new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]:
            return
        if new_dir != self.next_direction:
            self.play("turn")
        self.next_direction = new_dir

    def step_snake(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[-1]
        nx, ny = head_x + self.direction[0], head_y + self.direction[1]

        # Pared
        if nx < 0 or nx >= GRID_COLS or ny < 0 or ny >= GRID_ROWS:
            self.game_over(); return

        new_head = (nx, ny)

        # Obstáculo (letra)
        if new_head in self.obstacle_cells:
            self.game_over(); return

        will_eat = (self.fruit_cell is not None and new_head == self.fruit_cell)
        body_to_check = self.snake if will_eat else self.snake[1:]
        if new_head in body_to_check:
            self.game_over(); return

        self.snake.append(new_head)

        if will_eat:
            info = FRUIT_TYPES[self.fruit_kind]
            self.score += info["points"]
            if self.score > self.high_score:
                self.high_score = self.score

            was_apple = (self.fruit_kind == "apple")

            if was_apple:
                self.play("eat")
                self.apples_eaten += 1
                # Subir nivel
                new_level = 1 + self.apples_eaten // APPLES_PER_LETTER
                if new_level > self.level:
                    self.level = new_level
                    self.move_delay = max(
                        MIN_MOVE_DELAY_MS,
                        INITIAL_MOVE_DELAY_MS - SPEED_UP_PER_LEVEL_MS * (self.level - 1),
                    )
                    self.play("levelup")
                # ¿Toca letra nueva?
                if (self.apples_eaten % APPLES_PER_LETTER == 0
                        and self.letter_index < len(LETTERS_SEQUENCE)):
                    self._spawn_letter_phase()
                else:
                    self.fruit_kind = "apple"
                    self.fruit_cell = self._random_empty_cell()
            else:
                # Comió fruta especial → limpiar letra, avanzar
                self.play("special")
                self.obstacle_cells = set()
                self.special_active = False
                self.letter_index += 1
                if self.letter_index >= len(LETTERS_SEQUENCE):
                    self.state = STATE_WIN
                    self.play("win")
                    return
                else:
                    self.fruit_kind = "apple"
                    self.fruit_cell = self._random_empty_cell()

            if self.fruit_cell is None:
                self.state = STATE_WIN
                self.play("win")
        else:
            self.snake.pop(0)

    def _spawn_letter_phase(self):
        letter = LETTERS_SEQUENCE[self.letter_index]
        letter_cells, bbox = build_letter_cells(letter)

        # No bloquea celdas que la culebra ocupa ahora — la deja pasar.
        snake_set = set(self.snake)
        self.obstacle_cells = letter_cells - snake_set
        self.special_active = True

        # Fruta especial cerca del centro geométrico de la letra
        if bbox is not None:
            target = (bbox.centerx, bbox.centery)
        else:
            target = (GRID_COLS // 2, GRID_ROWS // 2)
        forbidden = self.obstacle_cells | snake_set
        cell = nearest_empty_cell(target, forbidden)
        self.fruit_cell = cell if cell else self._random_empty_cell()

        # Tipo de fruta cicla cada 5 letras
        self.fruit_kind = SPECIAL_FRUIT_ORDER[self.letter_index % len(SPECIAL_FRUIT_ORDER)]

    def game_over(self):
        self.state = STATE_GAMEOVER
        self.play("gameover")

    # ---------- Update ----------

    def update(self, dt):
        self.time_ms += dt
        self.blink_timer = (self.blink_timer + dt) % 1000
        self.fruit_pulse = (self.fruit_pulse + dt * 0.005) % (math.pi * 2)

        if self.state == STATE_PLAYING:
            self.move_timer += dt
            if self.move_timer >= self.move_delay:
                self.move_timer -= self.move_delay
                self.step_snake()

    # ---------- Draw ----------

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_WIN:
            self.draw_win()
        else:
            self.screen.fill(COLOR_BG)
            rect, cs = self.play_rect
            self.draw_grid(rect, cs)
            self.draw_obstacles(rect, cs)
            self.draw_fruit(rect, cs)
            self.draw_snake(rect, cs)
            self.draw_hud(rect)
            if self.state == STATE_PAUSED:
                self.draw_pause_overlay()
            elif self.state == STATE_GAMEOVER:
                self.draw_gameover_overlay()
            self.draw_touch_controls()

        # Overlays CRT al final
        if self.crt_overlay:
            self.screen.blit(self.crt_overlay, (0, 0))
        if self.vignette:
            self.screen.blit(self.vignette, (0, 0))

        pygame.display.flip()

    # ---- Pantallas con imagen ----

    def draw_menu(self):
        if self.image_start_scaled is not None:
            self.screen.fill((0, 0, 0))
            img = self.image_start_scaled
            x = (self.width - img.get_width()) // 2
            y = (self.height - img.get_height()) // 2
            self.screen.blit(img, (x, y))
            # Pista parpadeante
            blink = (self.blink_timer // 500) % 2 == 0
            if blink:
                self.draw_neon_text(self.font_mid, TEXT_PRESS,
                                    (self.width // 2, self.height - 30),
                                    COLOR_TEXT_YELLOW, COLOR_TEXT_PINK, center=True)
        else:
            self._draw_menu_procedural()

    def draw_win(self):
        if self.image_win_scaled is not None:
            self.screen.fill((0, 0, 0))
            img = self.image_win_scaled
            x = (self.width - img.get_width()) // 2
            y = (self.height - img.get_height()) // 2
            self.screen.blit(img, (x, y))
            # Score final arriba
            self.draw_neon_text(self.font_mid,
                                f"{TEXT_SCORE}  {self.score:06d}",
                                (self.width // 2, 32),
                                COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=True)
            blink = (self.blink_timer // 500) % 2 == 0
            if blink:
                self.draw_neon_text(self.font_mid, TEXT_PRESS,
                                    (self.width // 2, self.height - 30),
                                    COLOR_TEXT_YELLOW, COLOR_TEXT_PINK, center=True)
        else:
            self._draw_win_procedural()

    def _draw_menu_procedural(self):
        self.screen.fill(COLOR_BG)
        rect, cs = self.play_rect
        self.draw_grid(rect, cs)

        t = self.time_ms / 600
        title_y = max(120, self.height // 4) + int(math.sin(t) * 6)
        self.draw_neon_text(self.font_huge, GAME_TITLE,
                            (self.width // 2, title_y),
                            COLOR_TEXT_PINK, COLOR_TEXT_PINK, center=True)
        self.draw_neon_text(self.font_mid, SUBTITLE,
                            (self.width // 2, title_y + 65),
                            COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=True)
        self.draw_neon_text(self.font_mid, f"{TEXT_HISCORE}  {self.high_score:06d}",
                            (self.width // 2, title_y + 120),
                            COLOR_TEXT_YELLOW, COLOR_TEXT_YELLOW, center=True)
        blink = (self.blink_timer // 500) % 2 == 0
        if blink:
            self.draw_neon_text(self.font_big, TEXT_INSERT,
                                (self.width // 2, self.height - 200),
                                COLOR_TEXT_YELLOW, COLOR_TEXT_PINK, center=True)
        self.draw_neon_text(self.font_mid, TEXT_START,
                            (self.width // 2, self.height - 140),
                            COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=True)

    def _draw_win_procedural(self):
        self.screen.fill(COLOR_BG)
        t = self.time_ms / 600
        cy = self.height // 2
        self.draw_neon_text(self.font_huge, "FELICIDADES BRO!",
                            (self.width // 2, cy - 90 + int(math.sin(t) * 4)),
                            COLOR_TEXT_YELLOW, COLOR_TEXT_PINK, center=True)
        self.draw_neon_text(self.font_huge, "GANASTE!",
                            (self.width // 2, cy + 0 + int(math.sin(t + 0.5) * 4)),
                            COLOR_TEXT_PINK, COLOR_TEXT_YELLOW, center=True)
        self.draw_neon_text(self.font_big, f"{TEXT_SCORE}  {self.score:06d}",
                            (self.width // 2, cy + 90),
                            COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=True)
        blink = (self.blink_timer // 500) % 2 == 0
        if blink:
            self.draw_neon_text(self.font_mid, TEXT_RESTART,
                                (self.width // 2, cy + 170),
                                COLOR_TEXT_WHITE, COLOR_TEXT_YELLOW, center=True)

    # ---- Drawing helpers (tablero / culebra / frutas) ----

    def draw_grid(self, rect, cs):
        pygame.draw.rect(self.screen, COLOR_BORDER_GLOW, rect.inflate(12, 12), border_radius=6)
        pygame.draw.rect(self.screen, COLOR_BG,          rect.inflate(8, 8),   border_radius=4)
        pygame.draw.rect(self.screen, COLOR_BORDER,      rect, width=2)

        for c in range(GRID_COLS + 1):
            x = rect.left + c * cs
            pygame.draw.line(self.screen, COLOR_GRID_DIM, (x, rect.top), (x, rect.bottom))
        for r in range(GRID_ROWS + 1):
            y = rect.top + r * cs
            pygame.draw.line(self.screen, COLOR_GRID_DIM, (rect.left, y), (rect.right, y))

        for c in range(0, GRID_COLS + 1, 4):
            x = rect.left + c * cs
            pygame.draw.line(self.screen, COLOR_GRID_BRIGHT, (x, rect.top), (x, rect.bottom))
        for r in range(0, GRID_ROWS + 1, 4):
            y = rect.top + r * cs
            pygame.draw.line(self.screen, COLOR_GRID_BRIGHT, (rect.left, y), (rect.right, y))

    def draw_obstacles(self, rect, cs):
        if not self.obstacle_cells:
            return
        for gx, gy in self.obstacle_cells:
            px = rect.left + gx * cs
            py = rect.top  + gy * cs
            pygame.draw.rect(self.screen, COLOR_OBSTACLE_GLOW,
                             (px - 1, py - 1, cs + 2, cs + 2), width=1)
            pygame.draw.rect(self.screen, COLOR_OBSTACLE,
                             (px + 1, py + 1, cs - 2, cs - 2))
            if cs >= 14:
                pygame.draw.rect(self.screen, COLOR_OBSTACLE_GLOW,
                                 (px + 3, py + 3, cs - 6, cs - 6), width=1)

    def draw_snake(self, rect, cs):
        for gx, gy in self.snake:
            px = rect.left + gx * cs
            py = rect.top  + gy * cs
            pygame.draw.rect(self.screen, COLOR_SNAKE_GLOW,
                             (px - 2, py - 2, cs + 4, cs + 4),
                             width=1, border_radius=4)

        for gx, gy in self.snake[:-1]:
            px = rect.left + gx * cs + 2
            py = rect.top  + gy * cs + 2
            pygame.draw.rect(self.screen, COLOR_SNAKE_BODY,
                             (px, py, cs - 4, cs - 4), border_radius=3)
            if cs >= 14:
                pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD,
                                 (px + 2, py + 2, cs - 8, cs - 8),
                                 width=1, border_radius=2)

        hx, hy = self.snake[-1]
        px = rect.left + hx * cs + 1
        py = rect.top  + hy * cs + 1
        pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD,
                         (px, py, cs - 2, cs - 2), border_radius=4)

        eye_offset = max(2, cs // 5)
        eye_size = max(2, cs // 8)
        dx, dy = self.direction
        if dx == 1:
            e1 = (px + cs - eye_offset - 3, py + eye_offset)
            e2 = (px + cs - eye_offset - 3, py + cs - eye_offset - 4)
        elif dx == -1:
            e1 = (px + eye_offset, py + eye_offset)
            e2 = (px + eye_offset, py + cs - eye_offset - 4)
        elif dy == -1:
            e1 = (px + eye_offset, py + eye_offset)
            e2 = (px + cs - eye_offset - 4, py + eye_offset)
        else:
            e1 = (px + eye_offset, py + cs - eye_offset - 4)
            e2 = (px + cs - eye_offset - 4, py + cs - eye_offset - 4)
        pygame.draw.rect(self.screen, COLOR_BG, (*e1, eye_size, eye_size))
        pygame.draw.rect(self.screen, COLOR_BG, (*e2, eye_size, eye_size))

    def draw_fruit(self, rect, cs):
        if not self.fruit_cell:
            return
        gx, gy = self.fruit_cell
        px = rect.left + gx * cs + cs // 2
        py = rect.top  + gy * cs + cs // 2
        pulse = (math.sin(self.fruit_pulse) + 1) / 2
        info = FRUIT_TYPES[self.fruit_kind]

        # Halo común
        glow_r = max(cs // 2, int(cs * 0.65 + pulse * 3))
        glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            alpha = int(45 * k / 4)
            r = int(glow_r * k / 4)
            pygame.draw.circle(glow_surf, (*info["glow"], alpha),
                               (glow_r + 2, glow_r + 2), r)
        self.screen.blit(glow_surf, (px - glow_r - 2, py - glow_r - 2))

        kind = self.fruit_kind
        if kind == "apple":
            self._draw_apple(px, py, cs, pulse, info)
        elif kind == "banana":
            self._draw_banana(px, py, cs, info)
        elif kind == "mandarina":
            self._draw_mandarina(px, py, cs, info)
        elif kind == "mango":
            self._draw_mango(px, py, cs, info)
        elif kind == "fresa":
            self._draw_fresa(px, py, cs, info)
        elif kind == "uva":
            self._draw_uva(px, py, cs, info)

    def _draw_apple(self, px, py, cs, pulse, info):
        radius = max(3, int(cs * 0.38 + pulse * 1.5))
        pygame.draw.circle(self.screen, info["color"], (px, py), radius)
        pygame.draw.circle(self.screen, info["glow"],
                           (px - radius // 3, py - radius // 3),
                           max(2, radius // 3))
        leaf_w = max(3, cs // 5)
        leaf_h = max(2, cs // 7)
        pygame.draw.ellipse(self.screen, (130, 255, 100),
                            (px + 1, py - radius - leaf_h, leaf_w, leaf_h))

    def _draw_banana(self, px, py, cs, info):
        r = max(3, int(cs * 0.40))
        pygame.draw.ellipse(self.screen, info["color"],
                            (px - r, py - r // 2, r * 2, int(r * 1.1)))
        pygame.draw.ellipse(self.screen, COLOR_BG,
                            (px - r, py - r, r * 2, r))
        pygame.draw.ellipse(self.screen, info["glow"],
                            (px - r + 2, py - r // 4, int(r * 1.4), max(2, r // 3)))
        tip = max(1, r // 5)
        pygame.draw.circle(self.screen, (110, 70, 30), (px - r + tip, py + r // 4), tip)
        pygame.draw.circle(self.screen, (110, 70, 30), (px + r - tip, py + r // 4), tip)

    def _draw_mandarina(self, px, py, cs, info):
        r = max(3, int(cs * 0.40))
        pygame.draw.circle(self.screen, info["color"], (px, py), r)
        pygame.draw.circle(self.screen, info["glow"],
                           (px - r // 3, py - r // 3),
                           max(2, r // 3))
        pygame.draw.ellipse(self.screen, (130, 220, 90),
                            (px - 2, py - r - 4, 5, 5))
        pygame.draw.line(self.screen, (90, 60, 30),
                         (px, py - r), (px, py - r - 2), 2)

    def _draw_mango(self, px, py, cs, info):
        r = max(3, int(cs * 0.40))
        pygame.draw.ellipse(self.screen, info["color"],
                            (px - r, py - int(r * 1.1), int(r * 2), int(r * 2.0)))
        pygame.draw.ellipse(self.screen, info["glow"],
                            (px - r + 2, py - r, max(3, r), max(3, r // 2)))
        pygame.draw.circle(self.screen, (255, 80, 100),
                           (px + r // 3, py - r // 2), max(2, r // 4))
        pygame.draw.ellipse(self.screen, (130, 220, 90),
                            (px - 2, py - r - 5, 5, 4))

    def _draw_fresa(self, px, py, cs, info):
        r = max(3, int(cs * 0.42))
        pts = [(px - r, py - r // 3),
               (px + r, py - r // 3),
               (px,     py + r)]
        pygame.draw.polygon(self.screen, info["color"], pts)
        pygame.draw.polygon(self.screen, (90, 220, 100),
                            [(px - r - 1, py - r // 3 - 1),
                             (px + r + 1, py - r // 3 - 1),
                             (px,         py - r)])
        for sx, sy in [(-r // 2, 0), (r // 2, 0),
                       (0, r // 4),
                       (-r // 3, r // 2), (r // 3, r // 2)]:
            pygame.draw.circle(self.screen, (255, 240, 130),
                               (px + sx, py + sy), max(1, r // 8))

    def _draw_uva(self, px, py, cs, info):
        r = max(2, int(cs * 0.16))
        positions = [
            ( 0,         -r * 2),
            (-r,          0),
            ( r,          0),
            (-r * 2,      r * 2),
            ( 0,          r * 2),
            ( r * 2,      r * 2),
        ]
        for dx, dy in positions:
            pygame.draw.circle(self.screen, info["color"], (px + dx, py + dy), r + 1)
            pygame.draw.circle(self.screen, info["glow"],
                               (px + dx - 1, py + dy - 1), max(1, r // 2))
        pygame.draw.ellipse(self.screen, (130, 220, 90),
                            (px - 3, py - r * 3 - 2, 6, 4))

    # ---- HUD ----

    def draw_hud(self, rect):
        y = 22
        score_str = f"{TEXT_SCORE}  {self.score:06d}"
        self.draw_neon_text(self.font_mid, score_str,
                            (rect.left + 4, y),
                            COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=False)

        hi_str = f"{TEXT_HISCORE}  {self.high_score:06d}"
        self.draw_neon_text(self.font_mid, hi_str,
                            (self.width // 2, y + 12),
                            COLOR_TEXT_YELLOW, COLOR_TEXT_YELLOW, center=True)

        lvl_str = f"{TEXT_LEVEL} {self.level:02d}"
        lvl_surf = self.font_mid.render(lvl_str, True, COLOR_TEXT_PINK)
        self.draw_neon_text(self.font_mid, lvl_str,
                            (rect.right - lvl_surf.get_width() - 4, y),
                            COLOR_TEXT_PINK, COLOR_TEXT_PINK, center=False)

        # Progreso de letras
        self._draw_letter_progress(y_top=58)

        # Banner de fruta especial activa
        if self.fruit_kind != "apple" and self.special_active:
            info = FRUIT_TYPES[self.fruit_kind]
            bonus = f"¡{self.fruit_kind.upper()}!   +{info['points']}"
            self.draw_neon_text(self.font_small, bonus,
                                (self.width // 2, rect.top - 16),
                                info["glow"], info["color"], center=True)

        # Si no hay controles táctiles, mostramos los controles de teclado abajo
        if not SHOW_TOUCH_CONTROLS:
            self.draw_neon_text(self.font_small, TEXT_CONTROLS,
                                (self.width // 2, self.height - 25),
                                COLOR_TEXT_WHITE, COLOR_TEXT_PINK, center=True)

    def _draw_letter_progress(self, y_top):
        chars = list(LETTERS_SEQUENCE)
        spacing = max(18, min(40, (self.width - 80) // len(chars)))
        total_w = spacing * (len(chars) - 1)
        x_start = self.width // 2 - total_w // 2

        self.draw_neon_text(self.font_tiny, TEXT_PROGRESS,
                            (x_start - 50, y_top + 4),
                            COLOR_TEXT_DIM, COLOR_TEXT_DIM, center=False)

        for i, ch in enumerate(chars):
            x = x_start + i * spacing
            if i < self.letter_index:
                color = COLOR_SNAKE_BODY
                glow  = COLOR_SNAKE_GLOW
                draw = True
            elif i == self.letter_index and self.special_active:
                color = COLOR_TEXT_PINK
                glow  = COLOR_TEXT_PINK
                draw = (self.blink_timer // 300) % 2 == 0
            elif i == self.letter_index:
                color = COLOR_TEXT_YELLOW
                glow  = COLOR_TEXT_YELLOW
                draw = True
            else:
                color = COLOR_TEXT_DIM
                glow  = COLOR_TEXT_DIM
                draw = True
            if draw:
                self.draw_neon_text(self.font_small, ch, (x, y_top),
                                    color, glow, center=True)

    def draw_pause_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        self.draw_neon_text(self.font_huge, TEXT_PAUSED,
                            (self.width // 2, self.height // 2 - 30),
                            COLOR_TEXT_YELLOW, COLOR_TEXT_YELLOW, center=True)
        self.draw_neon_text(self.font_mid, TEXT_RESUME,
                            (self.width // 2, self.height // 2 + 50),
                            COLOR_TEXT_CYAN, COLOR_TEXT_CYAN, center=True)

    def draw_gameover_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        self.draw_neon_text(self.font_huge, TEXT_GAMEOVER,
                            (self.width // 2, self.height // 2 - 60),
                            COLOR_TEXT_PINK, COLOR_TEXT_PINK, center=True)
        self.draw_neon_text(self.font_big, f"{TEXT_SCORE}  {self.score:06d}",
                            (self.width // 2, self.height // 2 + 15),
                            COLOR_TEXT_WHITE, COLOR_TEXT_CYAN, center=True)
        blink = (self.blink_timer // 500) % 2 == 0
        if blink:
            self.draw_neon_text(self.font_mid, TEXT_RESTART,
                                (self.width // 2, self.height // 2 + 90),
                                COLOR_TEXT_YELLOW, COLOR_TEXT_YELLOW, center=True)

    def draw_neon_text(self, font, text, pos, color, glow_color, center=True):
        glow = font.render(text, True, glow_color)
        glow.set_alpha(70)
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2),
                   (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for ox, oy in offsets:
            r = glow.get_rect()
            if center:
                r.center = (pos[0] + ox, pos[1] + oy)
            else:
                r.topleft = (pos[0] + ox, pos[1] + oy)
            self.screen.blit(glow, r)
        base = font.render(text, True, color)
        r = base.get_rect()
        if center:
            r.center = pos
        else:
            r.topleft = pos
        self.screen.blit(base, r)


# --------------------------------------------------------------------------
#   ASYNC MAIN LOOP  (compatible con pygbag)
# --------------------------------------------------------------------------

def _do_touch_action(game, action):
    """Helper: traduce un action name (start/up/down/left/right/pause) a juego."""
    if action == "start":
        game.reset()
        game.state = STATE_PLAYING
        game.play("start")
    elif action == "up":
        game.try_set_direction(UP)
    elif action == "down":
        game.try_set_direction(DOWN)
    elif action == "left":
        game.try_set_direction(LEFT)
    elif action == "right":
        game.try_set_direction(RIGHT)
    elif action == "pause":
        if game.state == STATE_PLAYING:
            game.state = STATE_PAUSED
            game.play("pause")
        elif game.state == STATE_PAUSED:
            game.state = STATE_PLAYING
            game.play("pause")


async def main():
    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    except Exception:
        pass

    pygame.init()

    if AUDIO_ENABLED and not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception as exc:
            print(f"[audio] mixer init failed: {exc}")

    game = Game()
    game.play("start")
    running = True

    while running:
        dt = game.clock.tick(TARGET_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                game.on_resize(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                key = event.key

                if key == pygame.K_ESCAPE:
                    if game.state == STATE_MENU:
                        running = False
                    else:
                        game.state = STATE_MENU
                        game.reset()

                elif key == pygame.K_SPACE:
                    if game.state in (STATE_MENU, STATE_GAMEOVER, STATE_WIN):
                        _do_touch_action(game, "start")

                elif key == pygame.K_p:
                    _do_touch_action(game, "pause")

                if game.state == STATE_PLAYING:
                    if key in (pygame.K_UP, pygame.K_w):
                        game.try_set_direction(UP)
                    elif key in (pygame.K_DOWN, pygame.K_s):
                        game.try_set_direction(DOWN)
                    elif key in (pygame.K_LEFT, pygame.K_a):
                        game.try_set_direction(LEFT)
                    elif key in (pygame.K_RIGHT, pygame.K_d):
                        game.try_set_direction(RIGHT)

            # ---- TÁCTIL / MOUSE  (pygbag traduce touch → mouse events) ----
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = game.handle_pointer_down(event.pos)
                if action:
                    _do_touch_action(game, action)

            elif event.type == pygame.MOUSEBUTTONUP:
                game.handle_pointer_up()

            # Touch nativo (no siempre disponible)
            elif event.type == pygame.FINGERDOWN:
                pos = (int(event.x * game.width), int(event.y * game.height))
                action = game.handle_pointer_down(pos)
                if action:
                    _do_touch_action(game, action)

            elif event.type == pygame.FINGERUP:
                game.handle_pointer_up()

        game.update(dt)
        game.draw()

        # ¡IMPORTANTE para pygbag!
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())