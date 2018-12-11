<%
    url = '%s?t_=%s&state=%s&email=%s' % (callback_url, token, state, email)
%>

<html>
    <head>
        <meta name="viewport" content="width=device-width"/>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    </head>

    <body>
    	<h1>Carrene Authentication Service</h1>
        <p> Click <a href="${url}">here</a> to join organization.</p>
    </body>
</html>
