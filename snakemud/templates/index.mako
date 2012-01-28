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
        $('#terminal').terminal(function(command, term) {
            $.post(${request.route_url("api_command")|js,n}, {c: command}, function(data){
                term.echo(data.response);
                term.echo('\n');
            });
        }, {
            greetings: ${greeting|js,n} + '\n\n',
            tabcompletion: true,
            exit: false,
            command_list: ${command_list|js,n},
            prompt: '>'});
    });
  </script>
</head>
<body>
  <h1>Welcome to SnakeMUD</h1>
  <div id="terminal">
  </div>
</body>
</html>
