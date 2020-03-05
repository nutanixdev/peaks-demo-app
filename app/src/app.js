#!/usr/bin/env nodejs

var mongodb_host = process.env.MONGODB_HOST
var express = require('express'),
    mongoose = require('mongoose'),
    bodyParser = require('body-parser');
var db = mongoose.connect('mongodb://' + mongodb_host + ':27017/demodb', {useMongoClient: true});
var Peak = require('./models/peakModel');
var app = express();
var port = process.env.PORT || 3000;

app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());
app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

peakRouter = require('./routes/peakRoutes')(Peak);
infoRouter = require('./routes/infoRoutes')();
app.use('/api/peaks', peakRouter);
app.use('/api/info', infoRouter);

app.get('/', function(req, res){
    res.send('API is functional.');
});

module.exports = app.listen(port, function(){
    console.log('Running on port: ' + port);
});
