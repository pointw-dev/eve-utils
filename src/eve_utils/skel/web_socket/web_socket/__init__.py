import logging
from flask import Flask, render_template
from log_trace.decorators import trace
from flask_socketio import send, emit


LOG = logging.getLogger('web_socket')


@trace
def initialize(app, socket):
    @app.route('/_ws')
    def web_socket():
        return render_template('ws.html', sync_mode=socket.async_mode)
        
    @app.route('/_ws/chat')
    def chat_room():
        return render_template('chat.html')
        
    add_events(socket)


@trace
def add_events(socket):
    @socket.on('message')
    def handle_message(data):
        emit('message', data)
        LOG.info(f'Received message: {data}')


