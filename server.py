#!/usr/bin/env python3
"""
ВолонтёрМДК — локальный сервер
Запуск: python server.py
Только стандартная библиотека Python 3.6+
"""

import json, os, hashlib, struct, base64, threading, time, socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT     = 3000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, 'db.json')

# ── База данных ──────────────────────────────────────────────────────────────

def default_db():
    return {
        "users": [
            {"id":1,"email":"admin@demo.kz","phone":"+77770001100","pw":"admin123","name":"Ахметов Даулет Сейткалиевич","age":28,"district":"Центральный","school":"КГУ им. К. Жубанова","work":"МДК Мугунгхва","points":1240,"events":18,"tasks_done":18,"joined":"2022-09-01","avatar":"А","avatarData":None,"bio":"Председатель","warnings":[],"rank":"activist","positionId":"chair","dept":"management","perms":None,"kpiMonth":124,"kpiGoal":150,"kpiArchive":[{"month":"2026-02","points":142,"goal":150,"pct":95}],"pointsLog":[{"date":"25.03.2026","by":"Система","reason":"Участие в субботнике","amount":80,"type":"plus"}],"notifications":[{"id":1,"text":"KPI выполнен на 95%","time":"4 дня назад","read":False}],"tgChatId":"","tgEnabled":False,"promoConditions":{"toVolunteer":{"onboarding":True,"staffAcademy":True,"events3":True,"active":True,"leaderApproval":True},"toActivist":{"staffAcademyFull":True,"events10":True,"organized3":True,"examPassed":True,"leaderApproval":True}},"organizedEvents":[1,2],"promoRequest":None,"examResult":{"passed":True,"score":5,"total":5,"date":"01.01.2023"},"examRetry":{"canRetry":True,"lastAttempt":None,"adminApproved":False}},
            {"id":2,"email":"volunteer@demo.kz","phone":"+77770002200","pw":"vol123","name":"Сейткали Айгерим Нурланкызы","age":20,"district":"мкр Северный","school":"Актюбинский университет","work":"","points":380,"events":7,"tasks_done":11,"joined":"2023-03-15","avatar":"С","avatarData":None,"bio":"","warnings":[],"rank":"volunteer","positionId":"vol_pos","dept":"volunteers","perms":None,"kpiMonth":38,"kpiGoal":100,"kpiArchive":[],"pointsLog":[{"date":"25.03.2026","by":"Ахметов Д.","reason":"Участие в субботнике","amount":80,"type":"plus"}],"notifications":[{"id":1,"text":"Вам начислено 80 баллов 🌱","time":"2 часа назад","read":False}],"tgChatId":"","tgEnabled":False,"promoConditions":{"toVolunteer":{"onboarding":True,"staffAcademy":True,"events3":True,"active":False,"leaderApproval":False},"toActivist":{"staffAcademyFull":False,"events10":False,"organized3":False,"examPassed":False,"leaderApproval":False}},"organizedEvents":[],"promoRequest":None,"examResult":None,"examRetry":{"canRetry":True,"lastAttempt":None,"adminApproved":False}},
            {"id":3,"email":"asel@demo.kz","phone":"+77770003300","pw":"asel","name":"Нурланова Асель Бакытовна","age":19,"district":"мкр Восточный","school":"ЗКМУ","work":"","points":720,"events":14,"tasks_done":22,"joined":"2022-11-20","avatar":"Н","avatarData":None,"bio":"","warnings":[],"rank":"volunteer","positionId":"vol_pos","dept":"volunteers","perms":None,"kpiMonth":72,"kpiGoal":100,"kpiArchive":[],"pointsLog":[],"notifications":[],"tgChatId":"","tgEnabled":False,"promoConditions":{"toVolunteer":{"onboarding":True,"staffAcademy":True,"events3":True,"active":True,"leaderApproval":True},"toActivist":{"staffAcademyFull":True,"events10":True,"organized3":True,"examPassed":False,"leaderApproval":False}},"organizedEvents":[1],"promoRequest":{"status":"pending","date":"24.03.2026","fromRank":"volunteer"},"examResult":None,"examRetry":{"canRetry":True,"lastAttempt":None,"adminApproved":False}},
            {"id":4,"email":"berik@demo.kz","phone":"+77770004400","pw":"berik","name":"Жаксыбеков Берик Маратович","age":22,"district":"Центральный р-н","school":"АГУ","work":"","points":560,"events":10,"tasks_done":18,"joined":"2023-01-10","avatar":"Ж","avatarData":None,"bio":"","warnings":[{"id":1,"reason":"Пропустил субботник","date":"15.02.2026"}],"rank":"volunteer","positionId":"vol_pos","dept":"volunteers","perms":None,"kpiMonth":56,"kpiGoal":100,"kpiArchive":[],"pointsLog":[],"notifications":[],"tgChatId":"","tgEnabled":False,"promoConditions":{"toVolunteer":{"onboarding":True,"staffAcademy":True,"events3":True,"active":True,"leaderApproval":True},"toActivist":{"staffAcademyFull":False,"events10":True,"organized3":False,"examPassed":False,"leaderApproval":False}},"organizedEvents":[],"promoRequest":None,"examResult":{"passed":False,"score":2,"total":5,"date":"20.03.2026"},"examRetry":{"canRetry":False,"lastAttempt":"Mon Mar 20 2026","adminApproved":False}},
            {"id":5,"email":"alina@demo.kz","phone":"+77770005500","pw":"alina","name":"Серикова Алина Дулатовна","age":21,"district":"мкр Жилгородок","school":"АГУ","work":"","points":140,"events":2,"tasks_done":3,"joined":"2024-01-05","avatar":"С","avatarData":None,"bio":"","warnings":[],"rank":"candidate","positionId":"cand_pos","dept":"volunteers","perms":None,"kpiMonth":14,"kpiGoal":50,"kpiArchive":[],"pointsLog":[],"notifications":[],"tgChatId":"","tgEnabled":False,"promoConditions":{"toVolunteer":{"onboarding":False,"staffAcademy":False,"events3":False,"active":False,"leaderApproval":False},"toActivist":{"staffAcademyFull":False,"events10":False,"organized3":False,"examPassed":False,"leaderApproval":False}},"organizedEvents":[],"promoRequest":None,"examResult":None,"examRetry":{"canRetry":True,"lastAttempt":None,"adminApproved":False}},
        ],
        "events": [
            {"id":1,"title":"Городской субботник «Зелёный Актобе»","date":"2026-04-05","location":"Центральный парк","points":80,"max":50,"registered":[2,3],"confirmed":[],"emoji":"🌿","coverData":None,"organizerId":3,"desc":"Уборка и озеленение городского парка.","status":"open","comments":[{"uid":1,"text":"Встречаемся у главного входа в 9:00!","ts":"23 мар, 10:15"}]},
            {"id":2,"title":"Форум молодёжи Казахстана","date":"2026-04-12","location":"ДК «Алтын»","points":120,"max":100,"registered":[2,4],"confirmed":[2],"emoji":"🎤","coverData":None,"organizerId":1,"desc":"Региональный форум с воркшопами.","status":"open","comments":[]},
            {"id":3,"title":"Выездной лагерь","date":"2026-04-20","location":"Озеро Шалкар","points":200,"max":30,"registered":[3,4,5],"confirmed":[3,4],"emoji":"⛺","coverData":None,"organizerId":None,"desc":"Трёхдневный лагерь.","status":"open","comments":[]},
            {"id":4,"title":"Ярмарка профессий","date":"2026-03-10","location":"Школа №15","points":60,"max":20,"registered":[2,3,4,5],"confirmed":[2,3,4,5],"emoji":"🎓","coverData":None,"organizerId":2,"desc":"Помощь в проведении ярмарки.","status":"completed","comments":[]},
            {"id":5,"title":"День добрых дел","date":"2026-03-20","location":"г. Актобе","points":70,"max":40,"registered":[2,3],"confirmed":[2,3],"emoji":"❤️","coverData":None,"organizerId":3,"desc":"Акция помощи пожилым.","status":"completed","comments":[]},
        ],
        "tasks": [
            {"id":1,"title":"Подготовить презентацию для форума","assignee":2,"points":40,"due":"2026-04-10","done":False},
            {"id":2,"title":"Собрать список участников субботника","assignee":2,"points":20,"due":"2026-04-03","done":False},
            {"id":3,"title":"Разместить анонс в соцсетях","assignee":2,"points":15,"due":"2026-04-01","done":True},
            {"id":4,"title":"Обзвонить волонтёров лагеря","assignee":2,"points":25,"due":"2026-04-15","done":False},
            {"id":5,"title":"Написать отчёт о субботнике","assignee":3,"points":30,"due":"2026-03-25","done":True},
            {"id":6,"title":"Материалы для форума","assignee":4,"points":50,"due":"2026-04-08","done":False},
        ],
        "announcements": [
            {"id":1,"title":"📌 Регистрация на Форум открыта","text":"Зарегистрируйтесь до 1 апреля. Участникам +120 баллов.","date":"25 марта 2026","pinned":True},
            {"id":2,"title":"Изменение системы баллов","text":"С 1 апреля коэффициент ×1.2 за городские мероприятия.","date":"20 марта 2026","pinned":False},
            {"id":3,"title":"Топ-волонтёры марта","text":"1 место — Нурланова Асель, 2 место — Жаксыбеков Берик.","date":"18 марта 2026","pinned":False},
        ],
        "documents": [
            {"id":1,"name":"Устав МДК Мугунгхва","icon":"📄","size":"1.2 МБ","date":"01.01.2026"},
            {"id":2,"name":"Инструкция волонтёра","icon":"📝","size":"845 КБ","date":"15.01.2026"},
            {"id":3,"name":"Положение Staff Academy","icon":"📄","size":"620 КБ","date":"10.01.2026"},
            {"id":4,"name":"Планы на 2026 год","icon":"📊","size":"2.1 МБ","date":"05.01.2026"},
        ],
        "tests": [{"id":1,"title":"Экзамен на Активиста","passScore":4,"active":True,"questions":[
            {"q":"Что является главной ценностью волонтёра МДК?","opts":["Личная выгода","Служение обществу","Карьера","Баллы"],"correct":1},
            {"q":"Сколько мероприятий нужно посетить кандидату?","opts":["1","2","3","5"],"correct":2},
            {"q":"Что такое Staff Academy?","opts":["Внешний курс","Внутренняя программа МДК","Экзамен","Рейтинг"],"correct":1},
            {"q":"Сколько мероприятий нужно ОРГАНИЗОВАТЬ для Активиста?","opts":["1","2","3","5"],"correct":2},
            {"q":"Чем отличается Активист от Волонтёра?","opts":["Только баллами","Высший ранг, прошёл все этапы","Зарплатой","Ничем"],"correct":1},
        ]}],
    }

db      = {}
db_lock = threading.Lock()

def load_db():
    global db
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                db = json.load(f)
            print('✅ База данных загружена из db.json')
            return
        except Exception as e:
            print(f'⚠️  Ошибка чтения db.json: {e} — создаём заново')
    db = default_db()
    _save()
    print('✅ База данных создана с демо-данными')

def _save():
    """Только под db_lock!"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def safe_db():
    import copy
    d = copy.deepcopy(db)
    for u in d.get('users', []):
        u.pop('pw', None)
    return d

# ── WebSocket ────────────────────────────────────────────────────────────────
ws_clients = set()
ws_lock    = threading.Lock()

def _ws_frame(text):
    payload = text.encode('utf-8')
    n = len(payload)
    if n < 126:
        hdr = bytes([0x81, n])
    elif n < 65536:
        hdr = bytes([0x81, 126]) + struct.pack('>H', n)
    else:
        hdr = bytes([0x81, 127]) + struct.pack('>Q', n)
    return hdr + payload

def ws_broadcast(data):
    frame = _ws_frame(json.dumps(data, ensure_ascii=False))
    dead  = set()
    with ws_lock:
        for s in list(ws_clients):
            try:
                s.sendall(frame)
            except Exception:
                dead.add(s)
        ws_clients.difference_update(dead)

def _ws_handshake(sock, key):
    magic  = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    accept = base64.b64encode(hashlib.sha1((key + magic).encode()).digest()).decode()
    sock.sendall((
        'HTTP/1.1 101 Switching Protocols\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        f'Sec-WebSocket-Accept: {accept}\r\n\r\n'
    ).encode())

def _ws_read(sock):
    """Один фрейм → str | 'ping' | None(закрыть)"""
    try:
        def exact(n):
            b = b''
            while len(b) < n:
                c = sock.recv(n - len(b))
                if not c:
                    raise ConnectionError
                b += c
            return b
        b1, b2 = exact(2)
        op, masked, length = b1 & 0xF, bool(b2 & 0x80), b2 & 0x7F
        if length == 126: length = struct.unpack('>H', exact(2))[0]
        elif length == 127: length = struct.unpack('>Q', exact(8))[0]
        if length > 5_000_000: return None
        mk   = exact(4) if masked else b'\x00'*4
        data = exact(length)
        if masked:
            data = bytes(b ^ mk[i % 4] for i, b in enumerate(data))
        if op == 8: return None
        if op == 9: return 'ping'
        return data.decode('utf-8', errors='replace')
    except Exception:
        return None

def _ws_client_thread(sock):
    """Поток на каждую WS-вкладку."""
    with ws_lock:
        ws_clients.add(sock)
    # Шлём текущую БД сразу при подключении
    try:
        with db_lock:
            snap = safe_db()
        sock.sendall(_ws_frame(json.dumps({'type':'db_update','db':snap}, ensure_ascii=False)))
    except Exception:
        pass
    # Читаем фреймы (только ping/pong нужны)
    while True:
        frame = _ws_read(sock)
        if frame is None:
            break
        if frame == 'ping':
            try: sock.sendall(bytes([0x8A, 0]))
            except Exception: break
    with ws_lock:
        ws_clients.discard(sock)
    try: sock.close()
    except Exception: pass

# ── HTTP ─────────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        msg = str(args[0]) if args else ''
        if '/api/' in msg:
            code = str(args[1]) if len(args) > 1 else ''
            print(f'  [{code}] {msg}')

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type',   'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        # WebSocket upgrade — запускаем поток, сами возвращаемся НЕМЕДЛЕННО
        if self.headers.get('Upgrade','').lower() == 'websocket':
            key = self.headers.get('Sec-WebSocket-Key','')
            _ws_handshake(self.connection, key)
            threading.Thread(
                target=_ws_client_thread,
                args=(self.connection,),
                daemon=True
            ).start()
            # НЕ делаем t.join() — это была причина блокировки!
            return

        # index.html
        if path in ('/', '/index.html'):
            fp = os.path.join(BASE_DIR, 'public', 'index.html')
            if not os.path.exists(fp):
                self.send_response(404); self.end_headers()
                self.wfile.write(b'index.html not found in public/')
                return
            data = open(fp, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type',   'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # GET /api/db
        if path == '/api/db':
            with db_lock:
                snap = safe_db()
            self._json(200, snap)
            return

        self.send_response(404); self.end_headers()

    def do_POST(self):
        path   = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        raw    = self.rfile.read(length) if length else b'{}'
        try:    data = json.loads(raw.decode('utf-8'))
        except: data = {}

        # POST /api/login
        if path == '/api/login':
            uid = data.get('id','').strip()
            pw  = data.get('pw','').strip()
            with db_lock:
                user = next(
                    (u for u in db['users']
                     if (u.get('email')==uid or u.get('phone')==uid) and u.get('pw')==pw),
                    None
                )
            if not user:
                self._json(401, {'error':'Неверный логин или пароль'}); return
            self._json(200, {'ok':True, 'user':{k:v for k,v in user.items() if k!='pw'}})
            return

        # POST /api/register
        if path == '/api/register':
            name  = data.get('name','').strip()
            email = data.get('email','').strip()
            phone = data.get('phone','').strip()
            pw    = data.get('pw','').strip()
            if not all([name,email,phone,pw]):
                self._json(400,{'error':'Заполните все поля'}); return
            with db_lock:
                if any(u.get('email')==email for u in db['users']):
                    self._json(400,{'error':'Email уже используется'}); return
                nu = {
                    "id":int(time.time()*1000),"email":email,"phone":phone,"pw":pw,
                    "name":name,"age":"","district":"","school":"","work":"",
                    "points":0,"events":0,"tasks_done":0,
                    "joined":time.strftime('%Y-%m-%d'),
                    "avatar":name[0].upper(),"avatarData":None,"bio":"","warnings":[],
                    "rank":"candidate","positionId":"cand_pos","dept":"volunteers","perms":None,
                    "kpiMonth":0,"kpiGoal":50,"kpiArchive":[],"pointsLog":[],"notifications":[],
                    "tgChatId":"","tgEnabled":False,
                    "promoConditions":{"toVolunteer":{"onboarding":False,"staffAcademy":False,"events3":False,"active":False,"leaderApproval":False},"toActivist":{"staffAcademyFull":False,"events10":False,"organized3":False,"examPassed":False,"leaderApproval":False}},
                    "organizedEvents":[],"promoRequest":None,"examResult":None,
                    "examRetry":{"canRetry":True,"lastAttempt":None,"adminApproved":False}
                }
                db['users'].append(nu)
                _save()
                snap = safe_db()
            ws_broadcast({'type':'db_update','db':snap})
            self._json(200,{'ok':True,'user':{k:v for k,v in nu.items() if k!='pw'}})
            return

        # POST /api/sync-all
        if path == '/api/sync-all':
            with db_lock:
                pw_map = {u['id']:u.get('pw','') for u in db.get('users',[])}
                if 'users' in data:
                    for u in data['users']:
                        u['pw'] = pw_map.get(u.get('id'), u.get('pw',''))
                db.update(data)
                _save()
                snap = safe_db()
            ws_broadcast({'type':'db_update','db':snap})
            self._json(200,{'ok':True})
            return

        self._json(404,{'error':'not found'})


# ── main ─────────────────────────────────────────────────────────────────────

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    load_db()
    srv = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    ip  = get_ip()
    print()
    print('╔══════════════════════════════════════════╗')
    print('║     ВолонтёрМДК — Сервер запущен!        ║')
    print('╠══════════════════════════════════════════╣')
    print(f'║  Открой:  http://localhost:{PORT}            ║')
    print(f'║  Сеть:    http://{ip}:{PORT}         ║')
    print('╠══════════════════════════════════════════╣')
    print('║  admin@demo.kz      → admin123           ║')
    print('║  volunteer@demo.kz  → vol123             ║')
    print('║  asel / berik / alina → те же логины     ║')
    print('╠══════════════════════════════════════════╣')
    print('║  Ctrl+C — остановить                     ║')
    print('╚══════════════════════════════════════════╝')
    print()
    print('  Совет: открывай разные аккаунты в режиме')
    print('  инкогнито (Ctrl+Shift+N) — у каждой вкладки')
    print('  своя сессия, данные синхронизируются сразу.')
    print()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 Сервер остановлен. Данные сохранены в db.json')
