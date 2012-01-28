import time
import pkg_resources
import random
from functools import partial


class Map(object):

    def __init__(self):
        self.data = pkg_resources.resource_string('snakemud', 'map.txt').splitlines()
        self.start_pos = []
        for y in range(len(self.data)):
            self.data[y] = list(self.data[y])
            for x in range(len(self.data[y])):
                if self[x, y] == '@':
                    self.start_pos.append((x, y))
                    self.data[y][x] = '.'
        if not self.start_pos:
            self.start_pos.append((1, 1))

    def __getitem__(self, (x, y)):
        if not 0 <= y < len(self.data) or not 0 <= x < len(self.data[y]):
            return '#'
        return self.data[y][x]

    def __setitem__(self, (x, y), c):
        assert 0 <= y < len(self.data) and 0 <= x < len(self.data[y])
        self.data[y][x] = c


class Interpreter(object):
    """Stateful command interpeter for a single player."""

    map = Map()

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

    x, y = random.choice(map.start_pos)
    seen = None
    tail = ()
    length = 7

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
        return description

    def describe_exits(self, original_direction=None):
        exit_color = '#66f'
        exits = [direction for direction in ['north', 'south', 'east', 'west']
                 if self.look(direction) in '.*']
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
        if what == 'compass':
            return self.do_compass()
        elif what == 'map':
            return self.do_map()
        elif what == 'gps':
            return self.do_gps()
        else:
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
        """print help about available commands"""
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
        return "You don't have any food!"

    def do_bite(self, *args):
        """bite something"""
        return "Bite what?"

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
        if what == '.':
            if not self.seen:
                self.mark_seen(self.x, self.y)
            self.tail += ((self.x, self.y), )
            self.map[self.x, self.y] = '*'
            while len(self.tail) > self.length:
                x, y = self.tail[0]
                self.map[x, y] = '.'
                self.tail = self.tail[1:]
            self.x += dx
            self.y += dy
            self.mark_seen(self.x, self.y)
            msg = self.describe_exits(direction)
            if not msg:
                msg = "You somehow ended up in a room with no exits!?!?!"
            if self.auto_map:
                msg += '\n' + self.do_map()
            return msg
        elif what == '#':
            return "There's a wall blocking your way."
        elif what == '*':
            if (self.x + dx, self.y + dy) == self.tail[0]:
                return "You found your tail!"
                # do something victory-like
            else:
                return "Your body blocks the way."
        else:
            return "You can't go there!"

    def look(self, direction):
        try:
            dx, dy = self.directions[direction.lower()]
        except KeyError:
            return False
        what = self.map[self.x + dx, self.y + dy]
        return what

    def can_go(self, direction):
        return (self.look(direction) == '.')

    def do_gps(self, *args):
        return "Your GPS reads: %+d, %+d" % (self.x, self.y)

    def do_compass(self, *args):
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
        self.last_event = None
        self.seen = None
        self.x, self.y = random.choice(self.map.start_pos)
        self.mark_seen(self.x, self.y)
        self.do_explore(self.length)
        return '\n\n\n\n\n' + self.greeting

    def mark_seen(self, x, y):
        if self.seen is None:
            self.seen = set()
        for ax in range(x-1, x+2):
            for ay in range(y-1, y+2):
                self.seen.add((ax, ay))

    def do_map(self, *args):
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
        ymin, ymax = min(ys), max(ys)
        rows = []
        for y in range(ymin, ymax + 1):
            row = ['[[;#a84;]@]' if (x, y) == (self.x, self.y)
                   else '[[;#a84;]*]' if self.map[x, y] == '*'
                                         and (x, y) in self.seen
                   else self.map[x, y] if (x, y) in self.seen
                   else ' '
                   for x in range(xmin, xmax + 1)]
            rows.append(' '.join(row))
        return '\n'.join(rows)

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
        def overlay_image(back, front):
            return [''.join(fc if fc != ' ' else bc
                            for fc, bc in zip(frow, brow))
                    for frow, brow in zip(front, back)]
        if self.look('n') in '.*':
            room = overlay_image(room, north_exit)
        if self.look('e') in '.*':
            room = overlay_image(room, east_exit)
        if self.look('w') in '.*':
            room = overlay_image(room, west_exit)
        if self.look('s') in '.*':
            room = overlay_image(room, south_exit)
        return '\n'.join(room)



def main():
    import readline, re
    strip_escapes = partial(re.sub, r'\[\[[^]]*]([^]]*)]', r'\1')
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
