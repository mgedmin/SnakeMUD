from pyramid.view import view_config

from .interpreter import Interpreter


@view_config(route_name='home', renderer='snakemud:templates/index.mako')
def index(request):
    interpreter = Interpreter() # XXX use sessions!
    return dict(greeting=interpreter.greeting,
                command_list=interpreter.command_list)


@view_config(route_name='api_command', renderer='json')
def command(request):
    interpreter = Interpreter() # XXX use sessions!
    command = request.params.get('c')
    response = interpreter.interpret(command)
    return {'response': response}
