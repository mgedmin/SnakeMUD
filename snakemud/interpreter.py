from functools import partial


class Interpreter(object):

    def interpret(self, command):
        words = command.split()
        if not words:
            return "Huh?"
        command = words[0].lower()
        fn = getattr(self, 'do_%s' % command,
                     partial(self.unknown_command, command))
        return fn(*words)

    def unknown_command(self, command, *args):
        return ("Don't know how to %s, sorry." % command)

    def do_look(self, *args):
        return ("You're slithering on the cold hard stone floor.\n"
                "The cold doesn't bother you.")


def main():
    interpreter = Interpreter()
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
