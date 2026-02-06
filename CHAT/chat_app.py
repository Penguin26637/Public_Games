import json, os, requests, time, uuid
from flask import Flask, request, render_template_string, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DATA_FILE = 'chat_data.json'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_d():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f: return json.load(f)
        except: return {"c": {}, "groups": {}}
    return {"c": {}, "groups": {}}

def save_d(d):
    with open(DATA_FILE, 'w') as f: json.dump(d, f)

db = load_d()
if "groups" not in db: db["groups"] = {}
if "c" not in db: db["c"] = {}

# --- ROUTES ---
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No name"}), 400
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({"url": f"/uploads/{filename}"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_all')
def get_all(): return jsonify(db)

@app.route('/add_f', methods=['POST'])
def add_f():
    data = request.json
    f_id = str(len(db["c"]))
    db["c"][f_id] = {"u": data['u'], "n": data['n'], "m": []}
    save_d(db)
    return jsonify({"status": "ok"})

@app.route('/create_g', methods=['POST'])
def create_g():
    data = request.json
    g_id = str(len(db["groups"]))
    db["groups"][g_id] = {"name": data['name'], "members": ["Me"], "msgs": []}
    save_d(db)
    return jsonify({"status": "ok"})

@app.route('/add_gm', methods=['POST'])
def add_gm():
    data = request.json
    db["groups"][data['g_id']]["members"].append(data['val'])
    save_d(db)
    return jsonify({"status": "ok"})

@app.route('/rename_member', methods=['POST'])
def rename_member():
    data = request.json
    if data['isG']: db["groups"][data['id']]["members"][data['idx']] = data['newName']
    else: db["c"][data['id']]["n"] = data['newName']
    save_d(db)
    return jsonify({"status": "ok"})

@app.route('/send', methods=['POST'])
def send_msg():
    data = request.json
    m = {"u": data['user'], "msg": data['msg'], "t": time.time()}
    if data['isG']: db["groups"][data['id']]["msgs"].append(m)
    else: db["c"][data['id']]["m"].append(m)
    save_d(db)
    return jsonify({"status": "ok"})

@app.route('/')
def index(): return render_template_string(HTML)

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Modern Chat</title>
<style>
    body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; margin: 0; display: flex; height: 100vh; overflow: hidden; }
    #side { width: 280px; background: #181818; padding: 15px; border-right: 1px solid #333; overflow-y: auto; }
    .t { padding: 12px; margin-bottom: 8px; background: #252525; cursor: pointer; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
    .t:hover { background: #333; }
    .active { background: #0078d4 !important; color: white; }
    #main { flex-grow: 1; display: flex; flex-direction: column; position: relative; background: #121212; }
    #header { padding: 15px; background: #181818; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
    #box { flex-grow: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
    .m { padding: 10px 15px; background: #2a2a2a; border-radius: 12px; max-width: 75%; align-self: flex-start; line-height: 1.4; word-wrap: break-word; }
    #member-panel { position: absolute; right: 0; top: 60px; width: 220px; height: calc(100% - 60px); background: #1a1a1a; border-left: 1px solid #333; display: none; padding: 15px; z-index: 10; box-shadow: -5px 0 15px rgba(0,0,0,0.3); }
    .p-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }
    .p-edit { opacity: 0.6; font-size: 10px; padding: 2px 6px; background: #0078d4; border-radius: 4px; cursor: pointer; }
    .in { padding: 15px; background: #181818; display: flex; gap: 10px; border-top: 1px solid #333; }
    input, button { padding: 10px; border-radius: 6px; border: none; background: #2a2a2a; color: #fff; outline: none; cursor: pointer; }
    .notif-badge { background: #0078d4; color: white; border-radius: 10px; min-width: 20px; height: 20px; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; }
    #prog-wrap { display:none; padding:10px; background:#181818; border-top:1px solid #333; }
    #prog-bar { width:0%; height:4px; background:#0078d4; transition:0.1s; }
</style>
</head>
<body>

<div id="side">
    <h3 style="margin-top:0">Groups</h3>
    <div style="display:flex; gap:5px">
        <input id="gn" type="text" placeholder="New Group..." style="width:75%">
        <button onclick="createG()" style="background:#28a745">+</button>
    </div>
    <div id="gm-mgr" style="display:none; background:#252525; padding:12px; margin-top:10px; border-radius:6px; border:1px solid #333">
        <small>Add Member to: <b id="target-g"></b></small><br>
        <input id="ga" type="text" placeholder="URL or Name" style="width:70%; font-size:11px; margin-top:8px">
        <button onclick="addGM()">Add</button>
    </div>
    <hr style="border:0; border-top:1px solid #333; margin:20px 0;">
    <h3>Friends</h3>
    <input id="fu" type="text" placeholder="Friend Port URL" style="width:90%">
    <input id="fn" type="text" placeholder="Name" style="width:90%; margin:5px 0">
    <button onclick="addF()" style="width:100%; background:#28a745; margin-bottom:15px">Save Friend</button>
    <div id="list"></div>
</div>

<div id="main">
    <div id="header">
        <b id="chat-title" style="font-size:1.1em">Welcome</b>
        <button id="member-toggle" onclick="toggleMemberPanel()" style="display:none; background:#333">Members</button>
    </div>
    <div id="member-panel">
        <h4 style="margin-top:0">Participants</h4>
        <div id="participant-list"></div>
    </div>
    <div id="box"></div>
    <div id="prog-wrap">
        <div style="width:100%; background:#333; height:4px;"><div id="prog-bar"></div></div>
    </div>
    <div class="in">
        <input id="un" type="text" placeholder="Me" style="width:70px">
        <input type="file" id="fi" style="display:none" onchange="sendFile()">
        <button onclick="document.getElementById('fi').click()">📎</button>
        <input id="mi" type="text" placeholder="Type a message..." style="flex-grow:1" onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()" style="background:#0078d4; font-weight:bold; padding:0 20px">Send</button>
    </div>
</div>

<script>
let cur = ""; let isG = false; let readCounts = {};

async function addF() {
    const u = document.getElementById('fu').value.trim().replace(/\/$/, "");
    const n = document.getElementById('fn').value.trim() || "Friend";
    await fetch('/add_f', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u, n})});
    document.getElementById('fu').value = ""; document.getElementById('fn').value = "";
    updateSidebar();
}

async function createG() {
    const name = document.getElementById('gn').value.trim();
    if(!name) return;
    await fetch('/create_g', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name})});
    document.getElementById('gn').value = "";
    updateSidebar();
}

function toggleMemberPanel() {
    const panel = document.getElementById('member-panel');
    panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
    if(panel.style.display === 'block') updateParticipants();
}

async function sel(id, ig) {
    cur = id; isG = ig;
    document.getElementById('member-toggle').style.display = 'block';
    const res = await fetch('/get_all');
    const data = await res.json();
    if(ig) {
        document.getElementById('chat-title').innerText = data.groups[id].name;
        document.getElementById('target-g').innerText = data.groups[id].name;
        document.getElementById('gm-mgr').style.display = 'block';
        readCounts[id] = data.groups[id].msgs.length;
    } else {
        document.getElementById('chat-title').innerText = data.c[id].n;
        document.getElementById('gm-mgr').style.display = 'none';
        readCounts[id] = data.c[id].m.length;
    }
    updateSidebar(); updateMessages();
}

async function renameMember(oldName, idx) {
    const newName = prompt("Rename Participant:", oldName);
    if (!newName || newName === oldName) return;
    await fetch('/rename_member', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:cur, isG, oldName, newName, idx})});
    updateParticipants(); updateSidebar();
}

async function updateParticipants() {
    if (!cur) return;
    const res = await fetch('/get_all');
    const data = await res.json();
    let html = "";
    if (isG) {
        data.groups[cur].members.forEach((m, i) => {
            html += `<div class="p-item"><span>• ${m}</span> <span class="p-edit" onclick="renameMember('${m}', ${i})">✎</span></div>`;
        });
    } else {
        const f = data.c[cur];
        html += `<div class="p-item"><span>• Me</span></div><div class="p-item"><span>• ${f.n}</span> <span class="p-edit" onclick="renameMember('${f.n}', -1)">✎</span></div>`;
    }
    document.getElementById('participant-list').innerHTML = html;
}

async function addGM() {
    const val = document.getElementById('ga').value.trim();
    if(val) await fetch('/add_gm', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({g_id:cur, val})});
    document.getElementById('ga').value = "";
    updateParticipants();
}

async function updateSidebar() {
    const res = await fetch('/get_all');
    const data = await res.json();
    let html = "<b>Groups</b><br>";
    Object.entries(data.groups).forEach(([id, g]) => {
        const unread = g.msgs.length - (readCounts[id] || 0);
        const badge = (unread > 0 && cur !== id) ? `<span class="notif-badge">${unread}</span>` : "";
        html += `<div class="t ${cur===id?'active':''}" onclick="sel('${id}', true)">${g.name} ${badge}</div>`;
    });
    html += "<br><b>Friends</b><br>";
    Object.entries(data.c).forEach(([id, f]) => {
        const unread = f.m.length - (readCounts[id] || 0);
        const badge = (unread > 0 && cur !== id) ? `<span class="notif-badge">${unread}</span>` : "";
        html += `<div class="t ${cur===id?'active':''}" onclick="sel('${id}', false)">${f.n} ${badge}</div>`;
    });
    document.getElementById('list').innerHTML = html;
}

async function send(fileUrl = null) {
    const user = document.getElementById('un').value || "Me";
    const msg = fileUrl || document.getElementById('mi').value.trim();
    if(!msg || !cur) return;
    await fetch('/send', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:cur, isG, user, msg})});
    if(!fileUrl) document.getElementById('mi').value = "";
    updateMessages();
}

function sendFile() {
    const fileInput = document.getElementById('fi');
    if(fileInput.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]); // CRITICAL FIX: Send only the selected file
    const xhr = new XMLHttpRequest();
    document.getElementById('prog-wrap').style.display = 'block';
    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) document.getElementById('prog-bar').style.width = Math.round((e.loaded/e.total)*100)+'%';
    };
    xhr.onload = () => {
        if (xhr.status === 200) {
            const res = JSON.parse(xhr.responseText);
            send(res.url);
        }
        document.getElementById('prog-wrap').style.display = 'none';
        document.getElementById('prog-bar').style.width = '0%';
        fileInput.value = "";
    };
    xhr.open('POST', '/upload'); xhr.send(formData);
}

async function updateMessages() {
    if(!cur) return;
    const res = await fetch('/get_all');
    const data = await res.json();
    const msgs = isG ? data.groups[cur].msgs : data.c[cur].m;
    if(cur && !isG) readCounts[cur] = data.c[cur].m.length;
    if(cur && isG) readCounts[cur] = data.groups[cur].msgs.length;
    document.getElementById('box').innerHTML = msgs.map(m => {
        let content = m.msg;
        if(content.startsWith('/uploads/')) {
            const isImg = /\.(jpg|jpeg|png|gif)$/i.test(content);
            content = isImg ? `<img src="${content}" style="max-width:250px; border-radius:8px; display:block">` : 
                              `<a href="${content}" target="_blank" style="color:#0078d4">View Attachment</a>`;
        }
        return `<div class="m"><b>${m.u}:</b><br>${content}</div>`;
    }).join('');
    const b = document.getElementById('box'); b.scrollTop = b.scrollHeight;
}

updateSidebar();
setInterval(updateMessages, 3000);
</script>
</body>
</html>
'''

if __name__ == '__main__': app.run(debug=True, port=5000)
