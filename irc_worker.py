import socket, re, os, time, pymysql

DB_CONFIG = {
    'host':        os.environ.get('MYSQL_HOST', 'db'),
    'user':        os.environ.get('MYSQL_USER', 'xdcc'),
    'password':    os.environ.get('MYSQL_PASSWORD', 'tellofix'),
    'database':    os.environ.get('MYSQL_DATABASE', 'xdcc_test'),
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 10,
}

IRC_SERVER   = os.environ.get('IRC_SERVER',   'irc.abjects.net')
IRC_PORT     = int(os.environ.get('IRC_PORT', 6667))
IRC_NICKNAME = os.environ.get('IRC_NICKNAME', 'tellofix_bot')
IRC_CHANNELS = os.environ.get('IRC_CHANNELS', '#BEAST-XDCC').split(',')

def get_db():
    return pymysql.connect(**DB_CONFIG)

def init_db():
    sql = """CREATE TABLE IF NOT EXISTS irc_packs (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        network     VARCHAR(255),
        channel     VARCHAR(255),
        bot         VARCHAR(255),
        pack_number INT,
        file_size   VARCHAR(50),
        filename    VARCHAR(500),
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uniq_pack (network, channel, bot, pack_number)
    )"""
    for attempt in range(10):
        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            conn.close()
            print('[DB] Tabelle irc_packs bereit.')
            return True
        except Exception as e:
            print(f'[DB] Warte auf MariaDB... ({attempt+1}/10): {e}')
            time.sleep(5)
    return False

def save_pack(channel, bot, pack_number, file_size, filename):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO irc_packs (network, channel, bot, pack_number, file_size, filename)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE filename=%s, file_size=%s, created_at=CURRENT_TIMESTAMP
            """, (IRC_SERVER, channel, bot, pack_number, file_size, filename, filename, file_size))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'[DB] Fehler: {e}')

def scrape_channel(channel):
    print(f'[IRC] Verbinde {IRC_SERVER}:{IRC_PORT} -> {channel}')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((IRC_SERVER, IRC_PORT))
    except Exception as e:
        print(f'[IRC] Verbindungsfehler: {e}')
        time.sleep(15)
        return

    sock.send(f'USER {IRC_NICKNAME} 0 * :Tellofix\r\n'.encode())
    sock.send(f'NICK {IRC_NICKNAME}\r\n'.encode())

    buffer = ''
    joined = False
    start = time.time()
    pack_count = 0

    while time.time() - start < 300:
        try:
            sock.settimeout(10)
            data = sock.recv(4096).decode('utf-8', errors='ignore')
            if not data:
                break
            buffer += data
            lines = buffer.split('\r\n')
            buffer = lines.pop()
            for line in lines:
                if not line:
                    continue
                if line.startswith('PING'):
                    sock.send(line.replace('PING', 'PONG', 1).encode() + b'\r\n')
                    continue
                if (' 001 ' in line or ' 376 ' in line) and not joined:
                    sock.send(f'JOIN {channel}\r\n'.encode())
                    joined = True
                    print(f'[IRC] Gejoint: {channel}')
                    continue
                if 'PRIVMSG' in line and '#' in line:
                    bot_match  = re.match(r':([^!@ ]+)', line)
                    pack_match = re.search(r'#(\d+)', line)
                    if bot_match and pack_match:
                        bot_name  = bot_match.group(1)
                        pack_num  = int(pack_match.group(1))
                        parts = line.split(f'PRIVMSG {channel} :', 1)
                        raw   = parts[1].strip() if len(parts) > 1 else ''
                        clean = re.sub(r'[\x02\x1F\x0F\x16]|\x03(?:\d{1,2}(?:,\d{1,2})?)?', '', raw).strip()
                        size_match = re.search(r'\[?\s*([\d.,]+\s*[KMGkmg][Bb]?)\s*\]?', clean)
                        file_size  = size_match.group(1) if size_match else ''
                        save_pack(channel, bot_name, pack_num, file_size, clean)
                        pack_count += 1
                        if pack_count % 50 == 0:
                            print(f'[IRC] {pack_count} Pakete aus {channel}...')
        except socket.timeout:
            continue
        except Exception as e:
            print(f'[IRC] Fehler: {e}')
            break

    print(f'[IRC] {channel} fertig — {pack_count} Pakete gespeichert.')
    try:
        sock.send(b'QUIT :Tellofix\r\n')
        sock.close()
    except:
        pass

if __name__ == '__main__':
    print('[*] Tellofix IRC-Worker startet...')
    if not init_db():
        print('[!] DB nicht erreichbar.')
        exit(1)
    while True:
        for channel in IRC_CHANNELS:
            scrape_channel(channel.strip())
            time.sleep(10)
        print('[*] Pause 60s...')
        time.sleep(60)
