import json, os, requests
from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATA_FILE = 'chat_data.json'

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

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Modern Chat</title>
<style>
    body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; margin: 0; display: flex; height: 100vh; overflow: hidden; }
    
    /* Sidebar */
    #side { width: 280px; background: #181818; padding: 15px; border-right: 1px solid #333; overflow-y: auto; }
    .t { padding: 12px; margin-bottom: 8px; background: #252525; cursor: pointer; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
    .t:hover { background: #333; }
    .active { background: #0078d4 !important; color: white; }
    
    /* Main Chat Area */
    #main { flex-grow: 1; display: flex; flex-direction: column; position: relative; background: #121212; }
    #header { padding: 15px; background: #181818; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
    #box { flex-grow: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
    
    /* Messages */
    .m { padding: 10px 15px; background: #2a2a2a; border-radius: 12px; max-width: 75%; position: relative; align-self: flex-start; line-height: 1.4; }
    .m:hover .actions { display: flex; }
    .actions { display: none; position: absolute; right: -70px; top: 5px; gap: 5px; }
    .actions button { font-size: 11px; padding: 4px 8px; cursor: pointer; background: #333; border: 1px solid #444; color: #ccc; border-radius: 4px; }
    .actions button:hover { background: #444; color: white; }

    /* Participants Sidebar */
    #member-panel { 
        position: absolute; right: 0; top: 60px; width: 220px; height: calc(100% - 60px); 
        background: #1a1a1a; border-left: 1px solid #333; display: none; padding: 15px; z-index: 10;
        box-shadow: -5px 0 15px rgba(0,0,0,0.3);
    }
    .p-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }
    .p-edit { opacity: 0; font-size: 10px; padding: 2px 6px; background: #0078d4; border-radius: 4px; cursor: pointer; transition: 0.2s; }
    .p-item:hover .p-edit { opacity: 1; }

    /* UI Elements */
    .in { padding: 15px; background: #181818; display: flex; gap: 10px; border-top: 1px solid #333; }
    input, button { padding: 10px; border-radius: 6px; border: none; background: #2a2a2a; color: #fff; outline: none; }
    input:focus { background: #333; box-shadow: 0 0 0 2px #0078d4; }
    .notif-badge { background: #0078d4; color: white; border-radius: 10px; min-width: 20px; height: 20px; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; }
    .plus-btn { background: #28a745; width: 22px; height: 22px; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
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
    <div id="list"></div>
</div>

<div id="main">
    <div id="header">
        <b id="chat-title" style="font-size:1.1em">Welcome to Chat</b>
        <button id="member-toggle" onclick="toggleMemberPanel()" style="display:none; background:#333">Members</button>
    </div>
    
    <div id="member-panel">
        <h4 style="margin-top:0">Participants</h4>
        <div id="participant-list"></div>
    </div>
    
    <div id="box"></div>
    
    <div class="in">
        <input id="un" type="text" placeholder="Me" style="width:70px">
        <input id="mi" type="text" placeholder="Type a message..." style="flex-grow:1" onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()" style="background:#0078d4; font-weight:bold; padding:0 20px">Send</button>
    </div>
</div>

<script>
let cur = ""; let isG = false; let readCounts = {};

async function createG() {
    const name = document.getElementById('gn').value.trim();
    if(!name) return;
    await fetch('/create_g', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name})});
    document.getElementById('gn').value = "";
    updateSidebar();
}

function toggleG(id, name) {
    const mgr = document.getElementById('gm-mgr');
    cur = id; isG = true;
    document.getElementById('target-g').innerText = name;
    mgr.style.display = 'block';
    sel(id, true);
}

function toggleMemberPanel() {
    const panel = document.getElementById('member-panel');
    panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
    if(panel.style.display === 'block') updateParticipants();
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
        html += `<div class="p-item"><span>• Me</span></div>`;
        html += `<div class="p-item"><span>• ${f.n}</span> <span class="p-edit" onclick="renameMember('${f.n}', -1)">✎</span></div>`;
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
    let gHtml = ""; let fHtml = "";
    
    Object.entries(data.groups).forEach(([id, g]) => {
        const unread = g.msgs.length - (readCounts[id] || 0);
        const badge = (unread > 0 && cur !== id) ? `<span class="notif-badge">${unread}</span>` : "";
        gHtml += `<div class="t ${cur===id?'active':''}" onclick="sel('${id}', true)">
                    <div style="display:flex; align-items:center">${badge} ${g.name}</div>
                    <div class="plus-btn" onclick="event.stopPropagation(); toggleG('${id}', '${g.name}')">+</div>
                 </div>`;
    });
    
    Object.entries(data.c).forEach(([u, d]) => {
        const unread = d.m.length - (readCounts[u] || 0);
        const badge = (unread > 0 && cur !== u) ? `<span class="notif-badge">${unread}</span>` : "";
        fHtml += `<div class="t ${cur===u?'active':''}" onclick="sel('${u}', false)">
                    <div style="display:flex; align-items:center">${badge} ${d.n}</div>
                 </div>`;
    });
    document.getElementById('list').innerHTML = gHtml + fHtml;
}

async function sel(u, g) {
    cur = u; isG = g;
    const res = await fetch('/get_all');
    const data = await res.json();
    document.getElementById('chat-title').innerText = g ? data.groups[u].name : data.c[u].n;
    document.getElementById('member-toggle').style.display = 'block';
    updateMessages(true); updateSidebar();
}

async function send() {
    const t = document.getElementById('mi').value;
    const u = document.getElementById('un').value || "Me";
    if(!cur || !t) return;
    document.getElementById('mi').value = "";
    const mid = "ID_" + Date.now();
    const route = isG ? '/send_g' : '/send_i';
    const body = isG ? {g_id:cur, u, t, mid} : {t_u:cur+'/receive', f_u:cur, u, t, mid};
    await fetch(route, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    updateMessages();
}

async function updateMessages(force = false) {
    if(!cur) return;
    const url = isG ? `/get_g_msgs?id=${cur}` : `/get_m?f=${encodeURIComponent(cur)}`;
    const res = await fetch(url);
    const ms = await res.json();
    
    if(force || document.getElementById('box').children.length !== ms.length) {
        readCounts[cur] = ms.length;
        document.getElementById('box').innerHTML = ms.map((m, i) => `
            <div class="m">
                <div class="actions">
                    <button onclick="editMsg(${i})">Edit</button>
                    <button onclick="delMsg(${i})">X</button>
                </div>
                <b>${m.u}:</b> <span id="mt-${i}">${m.t}</span>
            </div>`).join('');
        document.getElementById('box').scrollTop = document.getElementById('box').scrollHeight;
    }
}

async function editMsg(idx) {
    const n = prompt("Edit message:", document.getElementById(`mt-${idx}`).innerText);
    if(n) {
        await fetch('/edit_m', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:cur, isG, idx, t:n})});
        updateMessages(true);
    }
}

async function delMsg(idx) {
    if(confirm("Delete?")) {
        await fetch('/del_m', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:cur, isG, idx})});
        updateMessages(true);
    }
}

setInterval(() => { updateSidebar(); updateMessages(); }, 3000);
updateSidebar();
</script>
</body></html>
'''

@app.route('/rename_member', methods=['POST'])
def rename_m():
    d = request.json
    if d['isG']:
        db['groups'][d['id']]['members'][d['idx']] = d['newName']
    else:
        db['c'][d['id']]['n'] = d['newName']
    save_d(db); return jsonify({"s": "ok"})

@app.route('/edit_m', methods=['POST'])
def edit_m():
    d = request.json; target = db['groups'][d['id']]['msgs'] if d['isG'] else db['c'][d['id']]['m']
    target[d['idx']]['t'] = d['t']; save_d(db); return jsonify({"s": "ok"})

@app.route('/del_m', methods=['POST'])
def del_m():
    d = request.json; target = db['groups'][d['id']]['msgs'] if d['isG'] else db['c'][d['id']]['m']
    target.pop(d['idx']); save_d(db); return jsonify({"s": "ok"})

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/add_gm', methods=['POST'])
def add_gm():
    g = db['groups'][request.json['g_id']]
    if request.json['val'] not in g['members']: g['members'].append(request.json['val'])
    save_d(db); return jsonify({"s": "ok"})

@app.route('/create_g', methods=['POST'])
def create_g():
    g_id = "GRP_" + str(len(db['groups']))
    db['groups'][g_id] = {"name": request.json['name'], "members": [], "msgs": [], "ids": []}
    save_d(db); return jsonify({"s": "ok"})

@app.route('/get_all')
def get_all(): return jsonify(db)

@app.route('/get_g_msgs')
def get_g_msgs(): return jsonify(db['groups'].get(request.args.get('id'), {}).get('msgs', []))

@app.route('/get_m')
def get_m(): return jsonify(db['c'].get(request.args.get('f'), {}).get('m', []))

@app.route('/receive', methods=['POST'])
def recv():
    d = request.json; s_u = d.get('my_u', 'Unk'); mid = d.get('mid'); gn = d.get('gn')
    if gn:
        gid = next((k for k,v in db['groups'].items() if v['name'] == gn), None)
        if not gid:
            gid = "GRP_" + str(len(db['groups']))
            db['groups'][gid] = {"name": gn, "members": [s_u], "msgs": [], "ids": []}
        target = db['groups'][gid]; msg_list = target['msgs']
    else:
        if s_u not in db['c']: db['c'][s_u] = {"n": d.get('u', 'Friend'), "m": [], "ids": []}
        target = db['c'][s_u]; msg_list = target['m']
    if mid not in target.setdefault('ids', []):
        msg_list.append({"u": d['u'], "t": d['t']})
        target['ids'].append(mid); save_d(db)
    return jsonify({"s": "ok"})

@app.route('/send_i', methods=['POST'])
def send_i():
    d = request.json; f_u = d['f_u']; mid = d['mid']
    db['c'][f_u]['m'].append({"u": d['u'], "t": d['t']})
    db['c'][f_u].setdefault('ids', []).append(mid); save_d(db)
    try:
        my_u = f"https://{os.getenv('CODESPACE_NAME')}-4000.app.github.dev"
        requests.post(d['t_u'], json={"u": d['u'], "t": d['t'], "my_u": my_u, "mid": mid}, timeout=2)
    except: pass
    return jsonify({"s": "sent"})

@app.route('/send_g', methods=['POST'])
def send_g():
    d = request.json; gid = d['g_id']; mid = d['mid']; g = db['groups'][gid]
    g['msgs'].append({"u": d['u'], "t": d['t']}); g['ids'].append(mid); save_d(db)
    my_u = f"https://{os.getenv('CODESPACE_NAME')}-4000.app.github.dev"
    for item in g['members']:
        t_url = next((u for u, info in db['c'].items() if info['n'] == item), item)
        if t_url.startswith('http'):
            try: requests.post(f"{t_url.rstrip('/')}/receive", json={"u": d['u'], "t": d['t'], "my_u": my_u, "mid": mid, "gn": g['name']}, timeout=1)
            except: pass
    return jsonify({"s": "sent"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
