var http = require('http');

var server = http.createServer(function(req, res) {
	res.writeHead(200, { 'Content-Type': 'application/json' });
	res.end(JSON.stringify({'id': '3345', 'name': 'addidas sneakers', 'type': 'shoes', 'color': 'yellow'}));
});

server.listen(3000);