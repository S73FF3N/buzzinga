import random, pygame, json, sys, traceback

from .quiz_games import QuizGameBase
from .static import Static
from .game_utilities import blit_text_objects, optimize_text_in_container, load_static_sound
from .animation import BuzzingaAnimation


TURN_SECONDS = 20


def is_valid_placement(sorted_values, value, slot, descending=True):
    """Check whether `value` fits into `slot` of an already sorted list.

    `slot` is 1-based: slot 1 lies above the first item, slot k between item k-1
    and item k, slot len+1 below the last item. Equal neighbours count as correct.
    """
    above = sorted_values[slot - 2] if slot > 1 else None
    below = sorted_values[slot - 1] if slot <= len(sorted_values) else None
    if descending:
        return (above is None or above >= value) and (below is None or value >= below)
    return (above is None or above <= value) and (below is None or value <= below)


def format_value(element, unit):
    if element.get("display"):
        return element["display"]
    value = element["value"]
    if float(value).is_integer():
        text = f"{int(value):,}".replace(",", ".")
    else:
        text = str(value).replace(".", ",")
    return f"{text} {unit}" if unit else text


class SortQuiz(QuizGameBase):
    """Players take turns inserting elements into a growing sorted list.

    The game master types the number of the chosen element and the slot the
    player names; the game checks the placement against the values from the
    JSON file. A wrong placement eliminates the player for the current round
    and returns the element to the pool.
    """

    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation, language=None):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation, language)
        self.solution_shown = True
        self.active_player = -1
        self.active_players = [True] * self.amount_players
        self.turn_running = False
        self.sorted_items = []
        self.pool = {}
        self.selected = None
        self.input_buffer = ""
        self.message = ""
        self.turn_started_at = 0
        self.seconds_shown = None
        self.countdown_end_played = False

        inner = self.main_container.inflate(-24, -24)
        list_width = inner.w * 45 // 100
        self.list_rect = pygame.Rect(inner.x, inner.y, list_width, inner.h)
        self.pool_rect = pygame.Rect(inner.x + list_width + inner.w // 20, inner.y,
                                     inner.w - list_width - inner.w // 20, inner.h)
        self.reveal_rect = inner

    @classmethod
    def parse_entry(cls, entry):
        elements = [dict(e) for e in entry["elements"]]
        reference = dict(entry["reference"], is_reference=True)
        for element in elements + [reference]:
            if "name" not in element:
                raise KeyError("name")
            # Values are compared to check placements
            if isinstance(element["value"], bool) or not isinstance(element["value"], (int, float)):
                raise ValueError(f"value={element['value']!r} of {element['name']!r}")
        random.shuffle(elements)
        descending = entry.get("descending", True)
        return {
            'id': str(entry.get("id", "")),
            'criterion': str(entry["criterion"]),
            # None: a default in the game's language is shown (see direction_labels)
            'top_label': entry.get("top_label"),
            'bottom_label': entry.get("bottom_label"),
            'unit': entry.get("unit", ""),
            'descending': descending,
            'reference': reference,
            'elements': elements,
        }

    def load_round_data(self):
        with open(self.game_data, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        self.round_data = self.parse_rounds(data)
        self.total_rounds = len(self.round_data)
        random.shuffle(self.round_data)

    @property
    def current_data(self):
        return self.round_data[self.current_round - 1]

    def handle_events(self):
        key_status = pygame.key.get_pressed()
        keys = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (key_status[pygame.K_LALT] or key_status[pygame.K_RALT]):
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_ESCAPE:
                    self.escape_pressed = True
                    self.running = False
                keys.append((event.key, event.unicode))
        return keys

    # ---------- drawing ----------

    def row_geometry(self, rect):
        # one row per element, the reference and the two direction labels
        rows = len(self.current_data['elements']) + 3
        return rect.h / rows

    def direction_labels(self, data):
        """Banner texts for the top and bottom of the list; without labels in
        the JSON entry, "more"/"fewer" in the game's language."""
        larger, smaller = self.language['more'], self.language['fewer']
        default_top, default_bottom = (larger, smaller) if data['descending'] else (smaller, larger)
        return data['top_label'] or default_top, data['bottom_label'] or default_bottom

    def draw_sorted_list(self, rect, show_values):
        data = self.current_data
        row_h = self.row_geometry(rect)
        slot_w = row_h * 1.2
        box_x = rect.x + slot_w
        box_w = rect.w - slot_w

        items = self.sorted_items if not show_values else self.full_solution()
        top_label, bottom_label = self.direction_labels(data)
        self.draw_direction_banner(pygame.Rect(box_x, rect.y + 2, box_w, row_h - 4), top_label, up=True)
        self.draw_direction_banner(pygame.Rect(box_x, rect.y + row_h * (len(items) + 1) + 2, box_w, row_h - 4),
                                   bottom_label, up=False)

        for i, item in enumerate(items):
            box = pygame.Rect(box_x, rect.y + row_h * (i + 1) + 2, box_w, row_h - 4)
            if item.get('is_reference'):
                fill = Static.RED
            elif item.get('placed', True):
                fill = Static.BLUE
            else:
                fill = Static.GREY
            self.draw_rect(fill, Static.LIGHT_BLUE, 3, box)
            if show_values:
                name_box = pygame.Rect(box.x, box.y, box.w * 6 // 10, box.h)
                value_box = pygame.Rect(box.x + name_box.w, box.y, box.w - name_box.w, box.h)
                optimize_text_in_container(self.screen, name_box, item['name'], max_font_size=int(row_h))
                optimize_text_in_container(self.screen, value_box, format_value(item, data['unit']),
                                           max_font_size=int(row_h), color=Static.YELLOW)
            else:
                optimize_text_in_container(self.screen, box, item['name'], max_font_size=int(row_h))

        if not show_values:
            for slot in range(1, len(items) + 2):
                center = (int(rect.x + slot_w / 2), int(rect.y + row_h * slot))
                pygame.draw.circle(self.screen, Static.YELLOW, center, int(row_h * 0.45))
                blit_text_objects(self.screen, pygame.Rect(center[0] - row_h / 2, center[1] - row_h / 2, row_h, row_h),
                                  str(slot), pygame.font.Font(None, int(row_h * 0.8)), Static.BLACK)

    def draw_direction_banner(self, box, label, up):
        """Banner naming what the top (up=True) or bottom end of the list means, flanked by arrows."""
        self.draw_rect(Static.GREEN, Static.WHITE, 2, box)
        arrow_w = box.h * 0.8
        for center_x in (box.x + box.h, box.right - box.h):
            tip_y, base_y = (box.y + box.h * 0.15, box.bottom - box.h * 0.15)
            if not up:
                tip_y, base_y = base_y, tip_y
            pygame.draw.polygon(self.screen, Static.WHITE, [(center_x, tip_y),
                                                            (center_x - arrow_w / 2, base_y),
                                                            (center_x + arrow_w / 2, base_y)])
        text_box = box.inflate(-box.h * 4, 0)
        optimize_text_in_container(self.screen, text_box, label, max_font_size=int(box.h * 1.1))

    def draw_pool(self):
        if not self.pool:
            return
        numbers = sorted(self.pool)
        total = len(self.current_data['elements'])
        cols = 2 if total > 8 else 1
        rows = -(-total // cols)
        box_h = min(self.pool_rect.h / rows, self.row_geometry(self.list_rect) * 1.6)
        box_w = self.pool_rect.w / cols
        for number in numbers:
            idx = number - 1
            col, row = idx // rows, idx % rows
            box = pygame.Rect(self.pool_rect.x + col * box_w + 3, self.pool_rect.y + row * box_h + 3,
                              box_w - 6, box_h - 6)
            fill = Static.ORANGE if number == self.selected else Static.LIGHT_BLUE
            self.draw_rect(fill, Static.WHITE, 3, box)
            optimize_text_in_container(self.screen, box, f"{number}: {self.pool[number]['name']}",
                                       max_font_size=int(box_h * 0.8))

    def draw_board(self, show_values=False):
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
        if show_values:
            self.draw_sorted_list(self.reveal_rect, show_values=True)
        else:
            self.draw_sorted_list(self.list_rect, show_values=False)
            self.draw_pool()

    def draw_status(self):
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
        if self.message:
            text = self.message
        elif self.selected is None:
            text = f"Element: {self.input_buffer}"
        else:
            text = f"Position: {self.input_buffer}"
        optimize_text_in_container(self.screen, self.bottom_right_container, text)

    def draw_players(self, seconds_left=None):
        for n in range(self.amount_players):
            color = Static.LIGHT_BLUE if self.active_players[n] else Static.GREY
            if n == self.active_player and self.turn_running:
                color = Static.RED
            container = self.display_buzzer(n, color)
            if n == self.active_player and self.turn_running and seconds_left is not None:
                blit_text_objects(self.screen, container, str(seconds_left), self.SMALL_TEXT)

    def full_solution(self):
        data = self.current_data
        placed_names = {id(item) for item in self.sorted_items}
        items = [dict(item, placed=id(item) in placed_names) for item in [data['reference']] + data['elements']]
        return sorted(items, key=lambda item: item['value'], reverse=data['descending'])

    # ---------- game flow ----------

    def play_round(self):
        data = self.current_data
        self.active_players = [True] * self.amount_players
        self.sorted_items = [data['reference']]
        self.pool = {n: element for n, element in enumerate(data['elements'], start=1)}
        self.selected = None
        self.input_buffer = ""
        self.message = ""

        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_left_container)
        optimize_text_in_container(self.screen, self.bottom_left_container, data['criterion'])
        self.draw_board()
        self.start_next_turn()

    def start_next_turn(self):
        start = self.active_player
        for offset in range(1, self.amount_players + 1):
            candidate = (start + offset) % self.amount_players
            if self.active_players[candidate]:
                self.active_player = candidate
                break
        self.turn_running = True
        self.selected = None
        self.input_buffer = ""
        self.turn_started_at = pygame.time.get_ticks()
        self.seconds_shown = None
        self.countdown_end_played = False
        self.draw_board()
        self.draw_status()

    def seconds_left(self):
        elapsed = (pygame.time.get_ticks() - self.turn_started_at) // 1000
        return max(TURN_SECONDS - elapsed, 0)

    def update_timer(self):
        seconds = self.seconds_left()
        if seconds != self.seconds_shown:
            self.seconds_shown = seconds
            self.draw_players(seconds)
        if seconds == 0 and not self.countdown_end_played:
            self.countdown_end_played = True
            if self.is_game_sounds:
                countdown_sound = load_static_sound('countdown_end.wav')
                self.game_sound_channel.play(countdown_sound)

    def handle_turn_input(self, key, letter):
        if key == pygame.K_f:
            self.message = self.language['no_answer']
            self.eliminate_active_player()
            return
        if letter.isdigit():
            self.message = ""
            self.input_buffer += letter
        elif key == pygame.K_BACKSPACE:
            self.message = ""
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
            elif self.selected is not None:
                self.selected = None
                self.draw_board()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.input_buffer:
            number = int(self.input_buffer)
            self.input_buffer = ""
            if self.selected is None:
                if number in self.pool:
                    self.selected = number
                    self.draw_board()
                else:
                    self.message = self.language['wrong_number']
            elif 1 <= number <= len(self.sorted_items) + 1:
                self.place_selected(number)
                return
            else:
                self.message = self.language['wrong_position']
        self.draw_status()

    def place_selected(self, slot):
        data = self.current_data
        element = self.pool[self.selected]
        values = [item['value'] for item in self.sorted_items]
        if is_valid_placement(values, element['value'], slot, data['descending']):
            self.sorted_items.insert(slot - 1, element)
            del self.pool[self.selected]
            self.message = self.language['right']
            if not self.pool:
                self.end_round()
            else:
                self.start_next_turn()
        else:
            self.message = f"{self.language['wrong_placement']}: {element['name']}"
            self.eliminate_active_player()

    def eliminate_active_player(self):
        self.active_players[self.active_player] = False
        if sum(self.active_players) <= 1:
            self.end_round()
        else:
            self.start_next_turn()

    def end_round(self):
        self.turn_running = False
        self.selected = None
        self.input_buffer = ""
        # Players still in the game share the point: the last survivor alone,
        # or everyone left when the whole list has been sorted.
        for idx, is_active in enumerate(self.active_players):
            if is_active:
                self.scores[idx] += 1
                self.update_score(idx)
        if not self.pool:
            self.message = self.language['all_sorted']
        self.draw_board(show_values=True)
        self.draw_status()
        self.draw_players()
        self.check_game_over()
        self.initializing = True

    def run(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        self.screen.fill(Static.WHITE)
        pygame.display.set_caption(self.game_name)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(self.main_container, self.image_cache)
        moving_sprites.add(animation)

        self.display_game_info()

        while self.running:
            keys = self.handle_events()
            if self.escape_pressed:
                break

            if self.initializing:
                enter_pressed = any(key in (pygame.K_RETURN, pygame.K_KP_ENTER) for key, _ in keys)
                if self.winner_found:
                    if enter_pressed:
                        self.show_winner()
                elif enter_pressed:
                    try:
                        self.animation_stopped = True
                        self.current_round += 1
                        self.update_progress()
                        self.initializing = False
                        self.play_round()
                    except Exception:
                        traceback.print_exc()
                        self.running = False
                elif not self.animation_stopped:
                    self.draw_rect(Static.BLUE, Static.WHITE, 8, self.main_container)
                    moving_sprites.draw(self.screen)
                    moving_sprites.update(0.25)
                    animation.animate()
            elif self.turn_running:
                for key, letter in keys:
                    if not self.turn_running:
                        break
                    self.handle_turn_input(key, letter)
                if self.turn_running:
                    self.update_timer()

            self.update_particles()
            pygame.display.flip()
            self.clock.tick(60)
