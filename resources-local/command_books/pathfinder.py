"""A collection of all commands that a PathFinder can use to interact with the game."""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    UP = 'up'

    # Buffs
    BUFFS_MACRO = 'd'
    AWAKENED_RELIC = '5'
    EPIC_ADVENTURE = '6'
    DECENT_HOLY_SYMBOL = 'pgup'

    # Skills
    CARDINALS_MACRO = 'z'
    CARDINAL_BURST = 'x'
    CARDINAL_TORRENT = 'c'
    GLYPH_OF_IMPALEMENT = 'v'
    COMBO_ASSAULT = 'b'
    NOVA_BLAST = 'n'
    SHADOW_RAVEN = 'r'
    TRIPLE_IMPACT = 't'
    RAVEN_TEMPEST = 'y'
    ANCIENT_ASTRA = '4'
    RELIC_UNBOUND = '7'
    FURY_OF_THE_WILD = 'f1'
    GUIDED_ARROW = 'f2'


#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5:
        if direction == 'down':
            press(Key.FLASH_JUMP, 4)
        elif direction == 'up':
            press(Key.FLASH_JUMP, 1)
            press(Key.UP, 4)
    press(Key.FLASH_JUMP, num_presses)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        Teleport('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Uses each of PathFinder's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.buff_time = 0

    def main(self):
        buffs = [Key.BUFFS_MACRO, Key.DECENT_HOLY_SYMBOL, Key.AWAKENED_RELIC, Key.EPIC_ADVENTURE]
        now = time.time()
        if self.buff_time == 0 or now - self.buff_time > settings.buff_cooldown:
            for key in buffs:
                press(key, 3, up_time=0.3)
            self.buff_time = now


class Teleport(Command):
    """
    Teleports in a given direction, jumping if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.05)
        if self.direction in ['up', 'down']:
            num_presses = 2
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press(Key.JUMP, 3, down_time=0.1)
            else:
                press(Key.JUMP, 1)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.05)
        press(Key.TELEPORT, num_presses)
        key_up(self.direction)
        if settings.record_layout:
            config.layout.add(*config.player_pos)


class CardinalMacro(Command):
    """Attacks using 'Cardinal Macro' in a given direction."""

    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press(Key.CARDINALS_MACRO, self.attacks, up_time=0.05)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class CardinalTorrent(Command):
    """Uses 'Cardinal Torrent' once."""

    def main(self):
        press(Key.CARDINAL_TORRENT, 1, up_time=0.05)


class GlyphOfImpalement(Command):
    """Uses 'Glyph Of Impalement' once"""

    def main(self):
        press(Key.GLYPH_OF_IMPALEMENT, 1, up_time=0.05)

class ComboAssault(Command):
    """Uses 'Combo Assault' once"""

    def main(self):
        press(Key.COMBO_ASSAULT, 1, up_time=0.05)


class NovaBlast(Command):
    """
    Places 'Nova Blast' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.NOVA_BLAST, 3)


class ShadowRaven(Command):
    """Summon 'Shadow Raven'"""

    def main(self):
        press(Key.SHADOW_RAVEN, 1, up_time=0.05)


class TripleImpact(Command):
    """Uses 'Triple Impact' once."""

    def main(self):
        press(Key.TRIPLE_IMPACT, 4, down_time=0.1, up_time=0.15)


class RavenTempest(Command):
    """
    Throws 'Raven Tempest' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.RAVEN_TEMPEST, 3)


class AncientAstra(Command):
    """Holds down 'Ancient Astra' until this command is called again."""

    def main(self):
        key_up(Key.ANCIENT_ASTRA)
        time.sleep(0.075)
        key_down(Key.ANCIENT_ASTRA)
        time.sleep(0.15)


class RelicUnbound(Command):
    """Uses 'Relic Unbound' once."""

    def main(self):
        press(Key.RELIC_UNBOUND, 3)


class FuryOfTheWild(Command):
    """Uses 'Fury Of The Wild' once."""

    def main(self):
        press(Key.FURY_OF_THE_WILD, 2, down_time=0.1)
