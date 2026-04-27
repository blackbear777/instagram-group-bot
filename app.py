from flask import Flask, render_template, request, jsonify
from instagrapi import Client
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
app = Flask(__name__)

bot = Client()
bot.delay_range = [1, 3]

@app.route('/')
def dashboard():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Instagram Group Bot</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-indigo-600 to-purple-600 min-h-screen p-8">
    <div class="max-w-4xl mx-auto bg-white/20 backdrop-blur-xl rounded-3xl p-12 shadow-2xl">
        <h1 class="text-5xl font-bold text-white mb-8 drop-shadow-2xl">🤖 Instagram Group Bot</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div class="bg-white/30 p-8 rounded-2xl">
                <h2 class="text-2xl font-bold mb-4 text-white">🔐 Login</h2>
                <input id="username" placeholder="Username" class="w-full p-4 rounded-xl mb-4">
                <input id="password" type="password" placeholder="Password" class="w-full p-4 rounded-xl mb-4">
                <button onclick="login()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-white p-4 rounded-xl font-bold text-lg">Login</button>
            </div>
            
            <div class="bg-white/30 p-8 rounded-2xl">
                <h2 class="text-2xl font-bold mb-4 text-white">📱 Groups</h2>
                <button onclick="loadGroups()" class="w-full bg-blue-500 hover:bg-blue-600 text-white p-4 rounded-xl font-bold">Load Groups</button>
                <div id="groups" class="mt-4"></div>
            </div>
        </div>
        
        <div class="bg-white/20 p-8 rounded-2xl">
            <h2 class="text-2xl font-bold mb-4 text-white">💬 Send Message</h2>
            <input id="groupId" placeholder="Group ID" class="w-full p-4 rounded-xl mb-4">
            <textarea id="message" placeholder="Message..." rows="3" class="w-full p-4 rounded-xl mb-4"></textarea>
            <button onclick="sendMessage()" class="w-full bg-purple-500 hover:bg-purple-600 text-white p-4 rounded-xl font-bold">Send 🚀</button>
        </div>
        
        <div id="logs" class="mt-8 bg-black/30 p-6 rounded-2xl text-green-400 font-mono text-sm h-48 overflow-y-auto"></div>
    </div>
    
    <script>
        async function api(path, data) {
            const res = await fetch(path, {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data)
            });
            return res.json();
        }
        
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            log('🔐 Logging in...');
            const result = await api('/login', {username, password});
            log(result.success ? '✅ Logged in!' : '❌ ' + result.error);
        }
        
        async function loadGroups() {
            log('📱 Loading groups...');
            const groups = await (await fetch('/groups')).json();
            const container = document.getElementById('groups');
            container.innerHTML = groups.map(g => 
                `<div class="p-4 bg-white/20 rounded-xl cursor-pointer" onclick="navigator.clipboard.writeText('${g.id}'); document.getElementById('groupId').value='${g.id}'; log('📋 Copied ${g.id}')">
                    <div class="font-bold">${g.title}</div>
                    <div class="text-sm opacity-80">${g.members} members</div>
                    <div class="font-mono text-xs bg-black/30 px-2 py-1 rounded">${g.id}</div>
                </div>`
            ).join('');
        }
        
        async function sendMessage() {
            const groupId = document.getElementById('groupId').value;
            const message = document.getElementById('message').value;
            log(`💬 Sending to ${groupId}...`);
            const result = await api('/send', {groupId, message});
            log(result.success ? '✅ Sent!' : '❌ Failed');
        }
        
        function log(msg) {
            const logs = document.getElementById('logs');
            logs.innerHTML += `[${new Date().toLocaleTimeString()}] ${msg}<br>`;
            logs.scrollTop = logs.scrollHeight;
        }
    </script>
</body>
</html>
    '''

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        bot.login(data['username'], data['password'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/groups')
def groups():
    try:
        threads = bot.direct_threads(amount=20)
        groups = [t for t in threads if t.is_group]
        return jsonify([{
            'id': g.id,
            'title': g.thread_title or 'Unnamed',
            'members': len(g.users)
        } for g in groups])
    except:
        return jsonify([])

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    try:
        bot.direct_send(data['message'], [data['groupId']])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
