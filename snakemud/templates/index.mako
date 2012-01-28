<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>SnakeMUD</title>
  <link rel="stylesheet" href="${request.application_url}/static/css/jquery.terminal.css" type="text/css" media="screen" charset="utf-8">
  <script src="${request.application_url}/static/js/jquery-1.7.1.js"></script>
  <script src="${request.application_url}/static/js/jquery.terminal-0.4.6.js"></script>
  <script>
    jQuery(function($, undefined) {
    $('#terminal').terminal(function(command, term) {
        term.echo('Bad command or file name.');
    }, {
        greetings: "You feel hungry.",
        height: 600,
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
