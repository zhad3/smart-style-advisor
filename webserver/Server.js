var express = require('express');
var app = express();
var path = require('path');
var bodyParser = require('body-parser');
var fs = require('fs');

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(express.static(path.join(__dirname, 'public')));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));

app.get("/", function(req, res){
	res.render('index');
});

app.get("/clothing", function(req, res){
	fs.readFile('clothing.json', 'utf8', function(err, data){
		if(err)
			throw err;
		var jsonObj = JSON.parse(data);
		res.writeHead(200, { 'Content-Type': 'application/json' });
		res.end(JSON.stringify(jsonObj));
	});
});

app.get("/weather", function(req, res){
	fs.readFile('weather.json', 'utf8', function(err, data){
		if(err)
			throw err;
		var jsonObj = JSON.parse(data);
		res.writeHead(200, { 'Content-Type': 'application/json' });
		res.end(JSON.stringify(jsonObj));
	});
});


// assuming POST: clothing=[{},{}...]          <-- URL encoding
//
// or       POST: {"clothing":"[{},{}...]"}  <-- JSON encoding

app.post('/updateClothing', function(req, res) {
	console.log("UPDATE -- recieved from client: data = " + JSON.stringify(req.body.clothing));
    var clothing = req.body.clothing;
    var temp = req.body.temp;
	    fs.writeFile('clothing.json', JSON.stringify(clothing), 'utf8', function(err){
	    	//thow err -> the magnificent null error!
	    });
	    fs.writeFile('weather.json', JSON.stringify({"temp": temp}), function(err){

	    });
	    res.end("sucess");

});

app.use("*",function(req, res){
	res.render('404');
});

app.listen(3000,function(){
	console.log("Server running at Port 3000")
});