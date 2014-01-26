#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo, sys, os

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.contrib.fixers import ProxyFix
from tools import parse_playlist

sys.path.append(os.path.abspath('../../loader'))
from client import SimpleClient

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_pyfile('config.py')

db = pymongo.Connection()[app.config['DBNAME']]

class User(object):
	id = 1

user = User()

# backend client
bd = SimpleClient(('localhost', 4243))
bd.debug = True

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/streams')
def streams():
	streams = bd.streams_get()
	return render_template('streams.html', streams=streams.get('Items') or [])

@app.route('/upload_playlist', methods=['POST'])
def upload_playlist():
	playlist = request.files.get('playlist')
	if playlist:
		# TODO: check mime and len
		content = playlist.stream.read()
		urls = parse_playlist(content.decode('utf-8', errors='ignore'))
		if urls:
			result = dict((url, bd.streams_save(url=url, owner_id=user.id)) for url in urls)
			print result

	return redirect(url_for('streams'))

@app.context_processor
def context():
    return {
        'need_layout': True,
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13017, debug=True)
