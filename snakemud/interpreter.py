import time
import pkg_resources
import re
import random
from functools import partial

FLOOR = '.'
HEAD = '@'
BODY = '*'
TAIL = ','
WALL = '#'


strip_escapes = partial(re.sub, r'\[\[[^]]*]([^]]*)]', r'\1')


class Map(object):

    def __init__(self, level=1):
        self.data = pkg_resources.resource_string('snakemud', 'maps/l%d.txt' % level).splitlines()
        self.start_length = int(self.data.pop())
        self.start_pos = []
        for y in range(len(self.data)):
            self.data[y] = list(self.data[y])
            for x in range(len(self.data[y])):
                if self[x, y] == HEAD:
                    self.start_pos.append((x, y))
                    self.data[y][x] = FLOOR
        if not self.start_pos:
            self.start_pos.append((1, 1))

    def has_level(self, level):
        return pkg_resources.resource_exists('snakemud', 'maps/l%d.txt' % level)

    def __getitem__(self, (x, y)):
        if not 0 <= y < len(self.data) or not 0 <= x < len(self.data[y]):
            return WALL
        return self.data[y][x]

    def __setitem__(self, (x, y), c):
        assert 0 <= y < len(self.data) and 0 <= x < len(self.data[y])
        self.data[y][x] = c


class Interpreter(object):
    """Stateful command interpeter for a single player."""

    level = 1
    map = Map(level=level)

    greeting = "You are hungry.  Type 'help' if you feel lost."

    aliases = {
        'n': 'go north',
        's': 'go south',
        'e': 'go east',
        'w': 'go west',
        'north': 'go north',
        'west': 'go west',
        'south': 'go south',
        'east': 'go east',
        'pick up': 'take',
        'look at': 'examine',
    }

    directions = {
        'n': (0, -1),
        's': (0, +1),
        'e': (+1, 0),
        'w': (-1, 0),
        'north': (0, -1),
        'south': (0, +1),
        'east': (+1, 0),
        'west': (-1, 0),
    }

    full_direction = {
        'n': 'north',
        's': 'south',
        'e': 'east',
        'w': 'west',
        'north': 'north',
        'south': 'south',
        'east': 'east',
        'west': 'west',
    }

    last_event = None
    last_command = None
    activity = True

    auto_map = False
    auto_draw = False

    x, y = random.choice(map.start_pos)
    seen = None
    tail = ()
    length = 11
    found_tail = False

    def __init__(self):
        self.do_restart()

    @property
    def command_list(self):
        return sorted(name[3:] for name in dir(self) if name.startswith('do_')
                      and getattr(self, name).__doc__)

    def events(self):
        if self.last_event is None:
            self.last_event = time.time()
        elif time.time() - self.last_event > 60:
            self.last_event = time.time()
            if self.activity:
                self.activity = False
                return 'You sense the passage of time.'

    def interpret(self, command):
        self.last_event = time.time()
        self.activity = True
        words = command.split()
        if not words:
            return "Huh?"
        command = ' '.join(words[:2]).lower()
        if command in self.aliases:
            words[:2] = self.aliases.get(command).split()
            command = words[0].lower()
        else:
            command = words[0].lower()
            if command in self.aliases:
                words[:1] = self.aliases.get(command).split()
                command = words[0].lower()
        fn = getattr(self, 'do_' + command,
                     partial(self.unknown_command, command))
        return fn(*words[1:])

    def unknown_command(self, command, *args):
        return ("Don't know how to %s, sorry." % command)

    def do_clear(self, *args):
        """clear the screen"""
        # handled by the terminal on the client-side; here just to
        # show up in tab-completion list
        return ''

    def do_look(self, *args):
        """examine your surroundings"""
        description = ("You're slithering on the cold hard stone floor.\n"
                       "The cold doesn't bother you.")
        exits = self.describe_exits()
        if exits:
            description += '\n\n' + exits
        surroundings = self.describe_surroundings()
        if surroundings:
            description += '\n\n' + surroundings
        return description + self.auto_things()

    def describe_surroundings(self, mention_self=True):
        description = ''
        for d in 'nsew':
            if self.look(d) in (BODY, TAIL):
                if self.coords(d) == self.tail[0] or self.look(d) != BODY:
                    description += '\n\nYou see a snake tail in the %s!  Is that your tail?' % self.full_direction[d]
                elif self.coords(d) == self.tail[-1]:
                    if mention_self:
                        description += '\n\nYour body fills the cavern to the %s.' % self.full_direction[d]
                else:
                    description += '\n\nYou see a snake body in the %s.' % self.full_direction[d]
        return description.lstrip()

    def describe_exits(self):
        exit_color = '#66f'
        exits = [direction for direction in ['north', 'south', 'east', 'west']
                 if self.look(direction) in (FLOOR, BODY, TAIL)]
        if not exits:
            return ''
        elif len(exits) == 1:
            return "There's an exit to the [[;%s;]%s]." % (
                exit_color, exits[0])
        else:
            return ("There are exits to %s and the [[;%s;]%s]." % (
                ', '.join('the [[;%s;]%s]' % (exit_color, d)
                          for d in exits[:-1]),
                exit_color, exits[-1]))

    def do_inventory(self, *args):
        """examine your inventory"""
        return ("You're a snake!  You're carrying nothing.\n"
                "Except the GPS you, uh, found somewhere.  And a map.  And a compass.")

    def do_take(self, *args):
        """pick something up"""
        return ("There's nothing here to take.")

    def do_examine(self, *args):
        """examine an object"""
        if not args:
            return "Examine what?"
        what = args[0]
        if what == 'the' and len(args) > 1:
            what = args[1]
        if what == 'compass':
            return self.do_compass()
        elif what == 'map':
            return self.do_map()
        elif what == 'gps':
            return self.do_gps()
        elif what == 'gps':
            return self.do_gps()
        elif what == 'tail' and self.adjacent_to(self.tail[0]):
            return "What a magnificent tail!  Your mouth waters."
        elif what == 'snake' and self.can_see(BODY, TAIL):
            return "It's a snake."
        elif what == 'body' and self.can_see(BODY):
            return "It's a snake."
        elif what == 'tail' and self.can_see(TAIL):
            return "It's a snake."
        return "I see no %s here." % what

    def do_drop(self, *args):
        """drop an object"""
        if not args:
            return "Drop what?"
        what = args[0]
        if what in ('compass', 'map', 'gps'):
            return "I don't want to.  It might still be useful."
        elif what == 'database':
            return "Ha ha, Mr. Bobby Tables."
        else:
            return "I see no %s here." % what

    def do_help(self, *args):
        """print a brief help message"""
        return ("You're a long snake crawling through a dungeon.\n"
                "\n"
                "Type commands like 'look' to see what you can see around you,\n"
                "or commands like 'go north' to move around (short versions\n"
                "'n', 's', 'e', 'w' also work).\n"
                "\n"
                "Type 'commands' to see a list of (almost all) available commands.\n"
                "\n"
                "Your goal is to find your tail and bite it.  It may be easier\n"
                "to achieve this goal if you use 'draw on' and/or 'map on'.")

    def do_commands(self, *args):
        """list available commands"""
        return "\n".join([
            "Commands:",
        ] + [
            '    %(command)-10s -- %(help)s' % dict(
                command=command,
                help=getattr(self, 'do_' + command).__doc__,
            ) for command in self.command_list
        ])

    def do_eat(self, *args):
        """eat something"""
        if not args:
            return "You don't have any food!"
        return self.do_bite(*args)

    def do_bite(self, *args):
        """bite something"""
        if not args:
            return "Bite what?"
        what = args[0]
        if what in ('compass', 'map', 'gps'):
            return "It is inedible and not threatening."
        if what in ('tail', 'snake'):
            if self.adjacent_to(self.tail[0]):
                msg = "Ouch!"
                if not self.found_tail:
                    self.found_tail = True
                    msg += "  You found your tail!"
                if self.map.has_level(self.level + 1):
                    return (msg + "\n\n" +
                            "You win!  Type 'restart %d' to play the next level." % (self.level + 1))
                else:
                    return (msg + "\n\n" +
                            "You win the game!  Type 'restart 1' to play again.")
        if what in ('body', 'snake'):
            for d in 'nsew':
                if self.look(d) == BODY and self.coords(d) not in self.tail:
                    return 'You bite some snake.'
            for d in 'nsew':
                if self.coords(d) in self.tail:
                    return 'Ouch!'
        if what in ('tail', 'snake'):
            if self.can_see(TAIL):
                return 'You bite some snake.'
        return 'I see no %s here.' % what

    def do_go(self, *args):
        """move in the given direction (n/s/e/w)"""
        if not args:
            return 'Go where?  (Try north/south/east/west)'
        direction = args[0]
        try:
            dx, dy = self.directions[direction.lower()]
        except KeyError:
            return "I don't know where %s is." % direction
        what = self.map[self.x + dx, self.y + dy]
        if what == FLOOR:
            if not self.seen:
                self.mark_seen(self.x, self.y)
            self.tail += ((self.x, self.y), )
            self.map[self.x, self.y] = BODY
            while len(self.tail) > self.length:
                x, y = self.tail[0]
                self.map[x, y] = FLOOR
                self.tail = self.tail[1:]
            self.map[self.tail[0]] = TAIL
            self.x += dx
            self.y += dy
            self.mark_seen(self.x, self.y)
            self.map[self.x, self.y] = HEAD
            msg = self.describe_exits()
            if not msg:
                msg = "You somehow ended up in a room with no exits!?!?!"
            surroundings = self.describe_surroundings(False)
            if surroundings:
                msg += '\n' + surroundings
            return msg + self.auto_things()
        elif what == WALL:
            return "There's a wall blocking your way."
        elif what == TAIL and self.coords(direction) == self.tail[0]:
            if self.found_tail:
                return "You found your tail! Try biting it."
            else:
                self.found_tail = True
                return "You found your tail! Your mouth waters."
        elif what == BODY and self.coords(direction) in self.tail:
            return "Your body blocks the way."
        elif what == BODY:
            return "Some other snake's body blocks the way."
        elif what == TAIL:
            # never gonna happen if BODY == TAIL
            return "Some other snake's tail blocks sthe way."
        else:
            return "You can't go there!"

    def coords(self, direction):
        dx, dy = self.directions[direction.lower()]
        return (self.x + dx, self.y + dy)

    def look(self, direction):
        what = self.map[self.coords(direction)]
        return what

    def can_see(self, *what):
        for d in 'nsew':
            if self.look(d) in what:
                return d
        return False

    def adjacent_to(self, (x, y)):
        for d in 'nsew':
            if self.coords(d) == (x, y):
                return d
        return False

    def can_go(self, direction):
        try:
            return (self.look(direction) == FLOOR)
        except KeyError:
            return False

    def do_gps(self, *args):
        """look at your GPS"""
        return "Your GPS reads: %+d, %+d" % (self.x, self.y)

    def do_compass(self, *args):
        """look at your compass"""
        if args:
            if args[0] == 'on':
                return 'The compass always points north, which is up.'
            if args[0] == 'of':
                return 'The compass always points north, which is up.'
            return 'Compass what?'
        compass = [
            "   ___   ",
            " .  N  . ",
            ":   |   :",
            ":W  *  E:",
            ":       :",
            " ' _S_ ' ",
        ]
        return '\n'.join(compass)

    def do_restart(self, *args):
        """start the game from the very beginning"""
        level = self.level
        if args:
            try:
                level = int(args[0])
            except ValueError:
                return "That's not a level number."
            if not self.map.has_level(level):
                return "There is no level %d." % level
            self.level = level
        self.map = Map(level=self.level)
        self.length = self.map.start_length
        self.last_event = None
        self.found_tail = None
        self.tail = ()
        pos = list(self.map.start_pos)
        random.shuffle(pos)
        for self.x, self.y in pos:
            if self.map[self.x, self.y] == FLOOR:
                break
        self.map[self.x, self.y] = HEAD
        self.do_explore(self.length)
        self.seen = None
        self.mark_seen(self.x, self.y)
        msg = '\n\n\n\n\n' + self.greeting
        return msg + self.auto_things()

    def mark_seen(self, x, y):
        if self.seen is None:
            self.seen = set()
        for ax in range(x-1, x+2):
            for ay in range(y-1, y+2):
                self.seen.add((ax, ay))

    def do_map(self, *args):
        """draw the map of cavern's you've seen"""
        if not self.seen:
            self.mark_seen(self.x, self.y)
        if args:
            if args[0] == 'on':
                self.auto_map = True
                return 'Automap enabled.'
            elif args[0] == 'off':
                self.auto_map = False
                return 'Automap disabled.'
            else:
                return 'Map what?'
        xs = [x for (x, y) in self.seen]
        ys = [y for (x, y) in self.seen]
        xmin, xmax = min(xs), max(xs)
        xmin = max(xmin, self.x - 15)
        xmax = min(xmax, self.x + 15)
        ymin, ymax = min(ys), max(ys)
        ymin = max(ymin, self.y - 15)
        ymax = min(ymax, self.y + 15)
        rows = []
        for y in range(ymin, ymax + 1):
            row = ['[[;#a84;]%s]' % self.map[x, y]
                        if (x, y) == (self.x, self.y) or
                           (x, y) in self.tail and (x, y) in self.seen
                   else self.map[x, y] if (x, y) in self.seen
                   else ' '
                   for x in range(xmin, xmax + 1)]
            rows.append(' '.join(row))
        map = '\n'.join(rows)
        while True:
            s = re.sub(r'(\[\[;#a84;][^]]*)] \[\[;#a84;]([^]]*])', r'\1 \2', map)
            if s == map:
                break
            map = s
        return map

    def do_undocumented(self, *args):
        return "\n".join([
            "Undocumented commands:",
        ] + ['    ' + name[3:]
             for name in sorted(dir(self))
             if name.startswith('do_') and not getattr(self, name).__doc__
        ])

    def pick_direction(self):
        if not self.seen:
            self.mark_seen(self.x, self.y)
        choices = []
        for direction in 'nsew':
            if self.can_go(direction):
                dx, dy = self.directions[direction]
                x = self.x + dx
                y = self.y + dy
                for ax in range(x-1, x+2):
                    for ay in range(y-1, y+2):
                        if (ax, ay) not in self.seen:
                            choices.append(direction)
        if choices:
            return random.choice(choices)
        else:
            return None

    def do_explore(self, *args):
        """move randomly towards unseen locations for N turns"""
        if args:
            try:
                n = int(args[0])
            except ValueError:
                return 'What?'
        else:
            n = 1
        res = []
        for i in range(n):
            d = self.pick_direction()
            if not d:
                break
            res.append('You go %s.  %s' % (self.full_direction[d],
                                           self.do_go(d)))
        if not res:
            return 'I agree, you should do some exploring.'
        else:
            return '\n'.join(res)

    def do_draw(self, *args):
        """artistically draw the cavern you're in"""
        if args:
            if args[0] == 'on':
                self.auto_draw = True
                return 'Autodraw enabled.'
            elif args[0] == 'off':
                self.auto_draw = False
                return 'Autodraw disabled.'
            else:
                return 'Map what?'
        room = [
            ' ______________ ',
            '|\            /|',
            '| \ ________ / |',
            '|  |        |  |',
            '|  |        |  |',
            '|  |        |  |',
            '|  |________|  |',
            '| /          \ |',
            '|/____________\|',
        ]
        north_exit = [
            '                ',
            '                ',
            '                ',
            '                ',
            '     .----.     ',
            '     |    |     ',
            '     |____|     ',
            '                ',
            '                ',
        ]
        north_snake = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '       @@       ',
            '       @@       ',
            '                ',
            '                ',
        ]
        north_tail = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '      ,,,,      ',
            '                ',
            '                ',
        ]
        east_exit = [
            '                ',
            '                ',
            '                ',
            '              . ',
            '             /| ',
            '             || ',
            '             || ',
            '             \| ',
            '              \ ',
        ]
        east_snake = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '             @  ',
            '             @  ',
            '                ',
        ]
        east_tail = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '             ,  ',
            '                ',
        ]
        west_exit = [
            '                ',
            '                ',
            '                ',
            ' .              ',
            ' |\             ',
            ' ||             ',
            ' ||             ',
            ' |/             ',
            ' /              ',
        ]
        west_snake = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '  @             ',
            '  @             ',
            '                ',
        ]
        west_tail = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '  ,             ',
            '                ',
        ]
        room_snake = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '     @ @@ @     ',
            '    @  @@  @    ',
            '                ',
        ]
        south_exit = [
            '                ',
            '   _--------_   ',
            '  /          \  ',
            ' |            | ',
            ' |            | ',
            ' |            | ',
            ' |            | ',
            ' |            | ',
            ' |____________| ',
        ]
        south_snake = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '   @  @  @  @   ',
        ]
        south_tail = [
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '                ',
            '      ,,,,      ',
        ]
        def overlay_image(back, front):
            return [''.join(fc if fc != ' ' else bc
                            for fc, bc in zip(frow, brow))
                    for frow, brow in zip(front, back)]
        if self.look('n') in (FLOOR, BODY, TAIL):
            room = overlay_image(room, north_exit)
        if self.look('n') == BODY:
            room = overlay_image(room, north_snake)
        elif self.look('n') == TAIL:
            room = overlay_image(room, north_tail)
        if self.look('e') in (FLOOR, BODY, TAIL):
            room = overlay_image(room, east_exit)
        if self.look('e') == BODY:
            room = overlay_image(room, east_snake)
        elif self.look('e') == TAIL:
            room = overlay_image(room, east_tail)
        if self.look('w') in (FLOOR, BODY, TAIL):
            room = overlay_image(room, west_exit)
        if self.look('w') == BODY:
            room = overlay_image(room, west_snake)
        elif self.look('w') == TAIL:
            room = overlay_image(room, west_tail)
        # The player is always in the middle of the room
        room = overlay_image(room, room_snake)
        if self.look('s') in (FLOOR, BODY, TAIL):
            room = overlay_image(room, south_exit)
        if self.look('s') == BODY:
            room = overlay_image(room, south_snake)
        elif self.look('s') == TAIL:
            room = overlay_image(room, south_tail)
        return '\n'.join(room).replace('@', '[[;#a84;]@]')\
                              .replace(',', '[[;#a84;],]')

    def side_by_side(self, left, right, padding=4):
        if not left:
            return right
        if not isinstance(left, list):
            left = left.splitlines()
        if not isinstance(right, list):
            right = right.splitlines()
        lwidth = max(len(strip_escapes(l)) for l in left) + padding
        while len(left) < len(right):
            left.append('')
        while len(left) > len(right):
            right.append('')
        return '\n'.join(
            (l + ' ' * (lwidth - len(strip_escapes(l))) + r).rstrip()
            for l, r in zip(left, right))

    def auto_things(self):
        msg = ''
        if self.auto_map and self.auto_draw:
            msg += '\n\n' + self.side_by_side(self.do_draw(),
                                              '\n' + self.do_map())
        elif self.auto_map:
            msg += '\n\n' + self.do_map()
        elif self.auto_draw:
            msg += '\n\n' + self.do_draw()
        return msg

    def do_level(self, *args):
        """print current game level number"""
        if args:
            return "If you want to play a different level, use 'restart %s' instead." % args[0]
        return "You're playing level %d." % self.level


def main():
    import readline
    interpreter = Interpreter()
    interpreter.do_quit = lambda: 'Bye!'
    interpreter.do_quit.__doc__ = 'exit'
    print strip_escapes(interpreter.greeting)
    while True:
        print
        try:
            command = raw_input("> ")
        except EOFError:
            break
        if command == 'quit':
            break
        output = interpreter.events() or ''
        if output:
            output += '\n\n'
        output += interpreter.interpret(command)
        print strip_escapes(output)


if __name__ == '__main__':
    main()
