<!DOCTYPE html>
<%! from json import dumps as js %>\
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>SnakeMUD</title>
  <link rel="stylesheet" href="${request.application_url}/static/css/snakemud.css" type="text/css" media="screen" charset="utf-8">
  <link rel="stylesheet" href="${request.application_url}/static/css/jquery.terminal.css" type="text/css" media="screen" charset="utf-8">
  <script src="${request.application_url}/static/js/jquery-1.7.1.js"></script>
  <script src="${request.application_url}/static/js/jquery.terminal-0.4.6.js"></script>
  <script>
    jQuery(function($, undefined) {
        var term = $('#terminal').terminal(function(command, term) {
            $.post(${request.route_url("api_command")|js,n}, {c: command}, function(data){
                term.echo(data.response);
                term.echo('\n');
                term.set_command_list(data.command_list);
            });
        }, {
            greetings: ${greeting|js,n} + '\n\n',
            tabcompletion: true,
            exit: false,
            command_list: ${command_list|js,n},
            prompt: '>'});
        var event_poll = function() {
            $.getJSON(${request.route_url("api_events")|js,n}, function(data){
                if (data.response) {
                    term.echo(data.response);
                    term.echo('\n');
                }
                term.set_command_list(data.command_list);
                window.setTimeout(event_poll, 1000);
            });
        };
        window.setTimeout(event_poll, 1000);
    });
  </script>
</head>
<body>
  <h1>Welcome to SnakeMUD</h1>
  <div id="terminal">
  </div>
</body>
</html>
