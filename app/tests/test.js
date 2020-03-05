//During the test the env variable is set to test
//let process.env.NODE_ENV = 'test';

let mongoose = require("mongoose");
let Peak = require('../models/peakModel');

//Require the dev-dependencies
let chai = require('chai');
let chaiHttp = require('chai-http');
let server = require('../app');
let should = chai.should();

chai.use(chaiHttp);
//Our parent block
describe('Peaks', () => {
    // Test the /GET route
    describe('/GET peaks', () => {
        it('it should GET all 58 peaks', (done) => {
            chai.request(server)
            .get('/api/peaks')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.be.a('array');
                res.body.length.should.be.eql(58);
                if(err) {
                   return done(err);
                }
                done();
            });
        });
    });
    describe('/GET search peaks', () => {
        it('it should search State and GET all 58 peaks', (done) => {
            chai.request(server)
            .get('/api/peaks/?state=Colorado')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.be.a('array');
                res.body.length.should.be.eql(58);
                if(err) {
                   return done(err);
                }
                done();
            });
        });
        it('it should search Rank and GET 1 peak', (done) => {
            chai.request(server)
            .get('/api/peaks/?rank=1')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.be.a('array');
                res.body.length.should.be.eql(1);
                if(err) {
                   return done(err);
                }
                done();
            });
        });
        it('it should search Range and GET 5 peaks', (done) => {
            chai.request(server)
            .get('/api/peaks/?range=Mosquito%20Range')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.be.a('array');
                res.body.length.should.be.eql(5);
                if(err) {
                   return done(err);
                }
                done();
            });
        });
    });
    describe('/GET peak info', () => {
        it('it should be a JSON object', (done) => {
            chai.request(server)
            .get('/api/info')
            .end((err, res) => {
                res.should.have.status(200);
                res.should.be.json;
                res.body.should.be.a('object');
                if(err) {
                   return done(err);
                }
                done();
            });
        });
        it('it should have property -> hostname', (done) => {
            chai.request(server)
            .get('/api/info')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.have.property('hostname');
                if(err) {
                   return done(err);
                }
                done();
            });
        });
        it('it should have property -> ip', (done) => {
            chai.request(server)
            .get('/api/info')
            .end((err, res) => {
                res.should.have.status(200);
                res.body.should.have.property('ip');
                if(err) {
                   return done(err);
                }
                done();
            });
        });
    });
});
