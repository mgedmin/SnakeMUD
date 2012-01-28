from functools import partial


class Interpreter(object):

    greeting = "You are hungry."

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

    @property
    def command_list(self):
        return sorted(name[3:] for name in dir(self) if name.startswith('do_')
                      and getattr(self, name).__doc__)

    def interpret(self, command):
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
        return ("You're slithering on the cold hard stone floor.\n"
                "The cold doesn't bother you.")

    def do_inventory(self, *args):
        """examine your inventory"""
        return ("You're a snake!  You're carrying nothing.")

    def do_take(self, *args):
        """pick something up"""
        return ("There's nothing here to take.")

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

    counter = 0

    def do_count(self, *args):
        """count from one to infinity"""
        self.counter += 1
        return 'The count is now %d' % self.counter

    def do_eat(self, *args):
        return "You don't have any food!"

    def do_bite(self, *args):
        return "Bite what?"

    x = y = 0

    def do_go(self, direction, *args):
        """move in the given direction (n/s/e/w)"""
        try:
            dx, dy = self.directions[direction.lower()]
        except KeyError:
            return "I don't know where %s is." % direction
        self.x += dx
        self.y += dy
        return "Your GPS reads: %+d, %+d" % (self.x, self.y)

    def do_where(self, *args):
        return "Your GPS reads: %+d, %+d" % (self.x, self.y)

    def do_gps(self, *args):
        return "Yeah, I don't know where a snake found a GPS."


def main():
    interpreter = Interpreter()
    interpreter.do_quit = lambda: 'Bye!'
    interpreter.do_quit.__doc__ = 'exit'
    print interpreter.greeting
    while True:
        try:
            command = raw_input("> ")
        except EOFError:
            break
        if command == 'quit':
            break
        print interpreter.interpret(command)


if __name__ == '__main__':
    main()
