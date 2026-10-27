import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'family-secret-key-1234'

# База данных в памяти
CHATS = [
    {
        'id': 'family_group',
        'title': 'Семейный Чат',
        'members': ['papa', 'mama', 'artem'],
        'messages': [
            {'sender': 'artem', 'text': 'Привет всем! Чат работает!', 'time': '12:00'}
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

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user_key = data.get('userKey')
    password = data.get('password')
    if user_key in USERS and USERS[user_key]['pass'] == password:
        return jsonify({'success': True, 'userData': USERS[user_key]})
    return jsonify({'success': False, 'message': 'Неверный пароль'})

@app.route('/api/chats', methods=['POST'])
def api_get_chats():
    data = request.json
    user_key = data.get('userKey')
    user_chats = [c for c in CHATS if user_key in c['members']]
    return jsonify({'success': True, 'chats': user_chats})

@app.route('/api/create_chat', methods=['POST'])
def api_create_chat():
    data = request.json
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
    return jsonify({'success': True, 'chat': new_chat})

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    data = request.json
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
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Чат не найден'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
