<!DOCTYPE html>
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
            if (command == 'help') {
                term.echo("Commands");
                term.echo("    help         -- print this help");
                term.echo("    clear        -- clear the screen");
                term.echo("    lotsofoutput -- print lots of output to test scrolling");
            } else if (command == 'lotsofoutput') {
                for (var i = 0; i < 100; i++) {
                    term.echo("lots of output");
                }
            } else {
                term.echo('Bad command or file name.');
            }
        }, {
            greetings: "You feel hungry.",
            tabcompletion: true,
            command_list: ['help', 'clear', 'lotsofoutput'],
            prompt: 'C:\\>'});
    });
  </script>
</head>
<body>
  <h1>Welcome to SnakeMUD</h1>
  <div id="terminal">
  </div>
</body>
</html>
