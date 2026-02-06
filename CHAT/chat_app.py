import json, os, requests, uuid
from flask import Flask, request, render_template_string, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration for File Uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Pro Chat</title>
<style>
    body { font-family: sans-serif; background: #222; color: #fff; margin: 0; display: flex; height: 100vh; }
    #side { width: 250px; background: #111; padding: 15px; border-right: 1px solid #444; overflow-y: auto; }
    #main { flex-grow: 1; display: flex; flex-direction: column; background: #121212; }
    #box { flex-grow: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }
    .t { padding: 10px; margin-bottom: 5px; background: #333; cursor: pointer; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; position: relative; }
    .active { background: #0078d4; }
    .dot { width: 10px; height: 10px; background: #00bfff; border-radius: 50%; position: absolute; left: -5px; top: 50%; box-shadow: 0 0 8px #00bfff; }
    .m { padding: 8px; margin-bottom: 5px; background: #444; border-radius: 5px; max-width: 85%; align-self: flex-start; }
    .m img { max-width: 100%; border-radius: 5px; margin-top: 5px; }
    .in { padding: 15px; background: #111; display: flex; gap: 5px; border-top: 1px solid #444; align-items: center; }
    input, button { padding: 8px; border-radius: 4px; border: none; background: #333; color: #fff; }
    .btn-s { font-size: 10px; background: #555; padding: 2px 5px; cursor: pointer; }
    #search-results { background: #333; border-radius: 4px; margin-top: 5px; max-height: 100px; overflow-y: auto; }
    .search-item { padding: 5px; cursor: pointer; border-bottom: 1px solid #444; font-size: 12px; }
    .search-item:hover { background: #0078d4; }
</style>
</head>
<body>
    <div id="side">
        <h3>New Group</h3>
        <input id="gn" type="text" placeholder="Group Name" style="width:90%">
        <button onclick="createG()" style="width:100%; margin:5px 0; background:#28a745">Create Group</button>
        <hr style="border:0; border-top:1px solid #444; margin:15px 0;">
        <div id="gm-mgr" style="display:none; background:#222; padding:8px; border-radius:4px;">
            <b>Add Member (Search):</b>
            <input id="ga" type="text" placeholder="Search nickname..." oninput="searchUsers()" style="width:90%; font-size:11px; margin-top:5px;">
            <div id="search-results"></div>
            <p style="font-size:10px; color:#888; margin-top:5px;">Members: <span id="gm-list"></span></p>
        </div>
        <hr style="border:0; border-top:1px solid #444; margin:15px 0;">
        <h3>Friends</h3>
        <input id="fu" type="text" placeholder="Friend Port URL" style="width:90%"><br>
        <input id="fn" type="text" placeholder="Name" style="width:90%; margin:5px 0">
        <button onclick="addF()" style="width:100%; background:#28a745">Save Friend</button>
        <div id="list" style="margin-top:15px"></div>
    </div>
    <div id="main">
        <div id="box"></div>
        <div class="in">
            <input id="un" type="text" placeholder="Me" style="width:60px">
            <input id="mi" type="text" placeholder="Message..." style="flex-grow:1" onkeypress="if(event.key==='Enter') send()">
            <input type="file" id="file-input" style="display:none" onchange="uploadFile()">
            <button onclick="document.getElementById('file-input').click()" style="background:#555">📎</button>
            <button onclick="send()" style="background:#0078d4">Send</button>
        </div>
    </div>
<script>
    let cur = ""; let isG = false;
    let unread = JSON.parse(localStorage.getItem('unread') || "[]");

    async function addF() {
        const u = document.getElementById('fu').value.trim().replace(/\/$/, "");
        const n = document.getElementById('fn').value.trim() || "Friend";
        await fetch('/add_f', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u, n})});
        location.reload();
    }

    async function createG() {
        const name = document.getElementById('gn').value.trim();
        if(name) await fetch('/create_g', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name})});
        location.reload();
    }

    async function searchUsers() {
        const query = document.getElementById('ga').value.toLowerCase();
        const res = await fetch('/get_all');
        const data = await res.json();
        const resultsDiv = document.getElementById('search-results');
        resultsDiv.innerHTML = "";
        
        if(!query) return;

        Object.entries(data.c).forEach(([url, friend]) => {
            if(friend.n.toLowerCase().includes(query)) {
                const div = document.createElement('div');
                div.className = 'search-item';
                div.innerText = friend.n;
                div.onclick = () => addGM(friend.n);
                resultsDiv.appendChild(div);
            }
        });
    }

    async function addGM(val) {
        if(val) await fetch('/add_gm', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({g_id:cur, val})});
        document.getElementById('ga').value = "";
        document.getElementById('search-results').innerHTML = "";
        sel(cur, true);
    }

    async function uploadFile() {
        const fileInput = document.getElementById('file-input');
        if (!fileInput.files[0]) return;
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        
        if (data.url) {
            const msg = data.is_img ? `[IMG]:\${data.url}` : `[FILE]:\${data.url}`;
            document.getElementById('mi').value = msg;
            send();
        }
    }

    async function load() {
        const res = await fetch('/get_all');
        const data = await res.json();
        let html = "<b>Groups</b>";
        Object.entries(data.groups).forEach(([id, g]) => {
            const dot = (unread.includes(id) && cur !== id) ? '<div class="dot"></div>' : '';
            html += `<div class="t g-tab \${cur===id?'active':''}" onclick="sel('\${id}', true)">
                \${dot}<span>\${g.name}</span>
            </div>`;
        });
        html += "<br><b>Friends</b>";
        Object.entries(data.c).forEach(([u, d]) => {
            const dot = (unread.includes(u) && cur !== u) ? '<div class="dot"></div>' : '';
            html += `<div class="t \${cur===u?'active':''}" onclick="sel('\${u}', false)">
                \${dot}<span>\${d.n}</span><button class="btn-s" onclick="event.stopPropagation(); ren('\${u}')">Edit</button>
            </div>`;
        });
        document.getElementById('list').innerHTML = html;
    }

    function ren(u) {
        const n = prompt("New nickname:");
        if(n) fetch('/add_f', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u, n})}).then(()=>location.reload());
    }

    function sel(u, g) { 
        cur = u; isG = g;
        unread = unread.filter(i => i !== u);
        localStorage.setItem('unread', JSON.stringify(unread));
        document.getElementById('gm-mgr').style.display = g ? 'block' : 'none';
        if(g) fetch(\`/get_g_info?id=\${u}\`).then(r=>r.json()).then(d=>{ document.getElementById('gm-list').innerText=d.members.join(', '); });
        load(); update(); 
    }

    async function send() {
        const t = document.getElementById('mi').value;
        const u = document.getElementById('un').value || "Me";
        if(!cur || !t) return;
        document.getElementById('mi').value = "";
        const mid = Date.now() + Math.random();
        const route = isG ? '/send_g' : '/send_i';
        const body = isG ? {g_id:cur, u, t, mid} : {t_u:cur+'/receive', f_u:cur, u, t, mid};
        await fetch(route, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        update();
    }

    function formatMsg(m) {
        if (m.t.startsWith('[IMG]:')) {
            const url = m.t.split('[IMG]:')[1];
            return \`<b>\${m.u}:</b><br><img src="\${url}" onclick="window.open('\${url}')">\`;
        } else if (m.t.startsWith('[FILE]:')) {
            const url = m.t.split('[FILE]:')[1];
            const name = url.split('/').pop();
            return \`<b>\${m.u}:</b> <a href="\${url}" target="_blank" style="color:#00bfff">Download \${name}</a>\`;
        }
        return \`<b>\${m.u}:</b> \${m.t}\`;
    }

    async function update() {
        if(!cur) return;
        const resM = await fetch(isG ? \`/get_g_msgs?id=\${cur}\` : \`/get_m?f=\${encodeURIComponent(cur)}\`);
        const ms = await resM.json();
        const b = document.getElementById('box');
        b.innerHTML = ms.map(m => \`<div class="m">\${formatMsg(m)}</div>\`).join('');
        b.scrollTop = b.scrollHeight;
    }
    load(); setInterval(update, 2500);
</script>
</body></html>
'''

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files: return jsonify({"e": "No file"})
    file = request.files['file']
    if file.filename == '': return jsonify({"e": "No filename"})
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4()}.{ext}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    my_u = f"https://{os.getenv('CODESPACE_NAME')}-4000.app.github.dev"
    file_url = f"{my_u}/uploads/{filename}"
    is_img = ext in ['jpg', 'jpeg', 'png', 'gif']
    return jsonify({"url": file_url, "is_img": is_img})

@app.route('/add_f', methods=['POST'])
def add_f():
    d = request.json
    db['c'][d['u']] = {"n": d['n'], "m": db['c'].get(d['u'], {}).get('m', []), "ids": db['c'].get(d['u'], {}).get('ids', [])}
    save_d(db); return jsonify({"s": "ok"})

@app.route('/create_g', methods=['POST'])
def create_g():
    gid = "GRP_" + str(len(db.get('groups', {})))
    db.setdefault('groups', {})[gid] = {"name": request.json['name'], "members": [], "msgs": [], "ids": []}
    save_d(db); return jsonify({"s": "ok"})

@app.route('/add_gm', methods=['POST'])
def add_gm():
    g = db['groups'][request.json['g_id']]
    if request.json['val'] not in g['members']: g['members'].append(request.json['val'])
    save_d(db); return jsonify({"s": "ok"})

@app.route('/get_all')
def get_all(): return jsonify(db)

@app.route('/get_g_info')
def get_g_info(): return jsonify(db['groups'].get(request.args.get('id')))

@app.route('/get_g_msgs')
def get_g_msgs(): return jsonify(db['groups'].get(request.args.get('id'), {}).get('msgs', []))

@app.route('/get_m')
def get_m(): return jsonify(db['c'].get(request.args.get('f'), {}).get('m', []))

@app.route('/receive', methods=['POST'])
def recv():
    d = request.json; s_u = d.get('my_u', 'Unk'); mid = d.get('mid')
    gn = d.get('gn') 
    if gn:
        gid = next((k for k,v in db.setdefault('groups', {}).items() if v['name'] == gn), None)
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

if __name__ == '__main__': app.run(host='0.0.0.0', port=4000)
