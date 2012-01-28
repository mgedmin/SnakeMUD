from pyramid.view import view_config

from .interpreter import Interpreter


def get_interpreter(request):
    try:
        return request.session['interpreter']
    except KeyError:
        request.session['interpreter'] = Interpreter()
        request.session.save()
        return request.session['interpreter']


@view_config(route_name='home', renderer='snakemud:templates/index.mako')
def index(request):
    interpreter = get_interpreter(request)
    return dict(greeting=interpreter.greeting,
                command_list=interpreter.command_list)


@view_config(route_name='api_command', renderer='json')
def command(request):
    interpreter = get_interpreter(request)
    command = request.params.get('c')
    response = interpreter.interpret(command)
    request.session.save() # interpreter may have changed its state
    return {'response': response,
            'command_list': interpreter.command_list}
