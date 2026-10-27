import os
import base64
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'family-secret-key-1234'
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=50 * 1024 * 1024)

# База данных в памяти
CHATS = [
    {
        'id': 'family_group',
        'title': 'Семейный Чат',
        'members': ['papa', 'mama', 'artem'],
        'messages': [
            {'sender': 'artem', 'text': 'Привет всем! Чат на Render работает!', 'time': '12:00'}
        ]
    }
]

USERS = {
    'papa': {'name': 'Папа', 'pass': '1234', 'avatar': '👨'},
    'mama': {'name': 'Мама', 'pass': '1234', 'avatar': '👩'},
    'artem': {'name': 'Артем (Dev)', 'pass': '1234', 'avatar': '👨‍💻'}
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('login')
def handle_login(data):
    user_key = data.get('userKey')
    password = data.get('password')
    if user_key in USERS and USERS[user_key]['pass'] == password:
        emit('login_response', {'success': True, 'userKey': user_key, 'userData': USERS[user_key]})
    else:
        emit('login_response', {'success': False, 'message': 'Неверный пароль'})

@socketio.on('get_chats')
def handle_get_chats(data):
    user_key = data.get('userKey')
    user_chats = [c for c in CHATS if user_key in c['members']]
    emit('chats_list', user_chats)

@socketio.on('create_chat')
def handle_create_chat(data):
    members = data.get('members', [])
    title = data.get('title', 'Новый чат')
    chat_id = f"chat_{len(CHATS) + 1}"
    new_chat = {
        'id': chat_id,
        'title': title,
        'members': members,
        'messages': []
    }
    CHATS.append(new_chat)
    emit('chat_created', new_chat, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data.get('chatId')
    sender = data.get('sender')
    text = data.get('text', '')
    file_data = data.get('file')
    voice_data = data.get('voice')
    time_str = data.get('time')

    chat = next((c for c in CHATS if c['id'] == chat_id), None)
    if chat:
        msg_obj = {
            'sender': sender,
            'text': text,
            'file': file_data,
            'voice': voice_data,
            'time': time_str
        }
        chat['messages'].append(msg_obj)
        emit('new_message', {'chatId': chat_id, 'message': msg_obj}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
