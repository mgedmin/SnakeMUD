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
    events = interpreter.events()
    response = interpreter.interpret(command)
    if events:
        response = events + '\n\n' + response
    request.session.save() # interpreter may have changed its state
    return {'response': response,
            'command_list': interpreter.command_list}

@view_config(route_name='api_events', renderer='json')
def events(request):
    interpreter = get_interpreter(request)
    events = interpreter.events()
    request.session.save() # interpreter may have changed its state
    return {'response': events,
            'command_list': interpreter.command_list}

