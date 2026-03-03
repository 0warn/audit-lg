import joblib
import pandas as pd
import os
import time
import json
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich import print as rprint

console = Console()

# Professional Label Mapping
ATTACK_TYPES = {
    0: "✅ SAFE",
    1: "🚨 SQL Injection",
    2: "🚨 XSS (Cross-Site Scripting)",
    3: "🚨 RCE/Command Injection",
    4: "🚨 Path Traversal",
    5: "🚨 Brute Force Attempt"
}

def open_editor(file_path):
    """Open the file in an editor. Uses sudo vim if root permission is needed."""
    # Check if we have write access to the file or the directory if file doesn't exist
    path_to_check = file_path if os.path.exists(file_path) else os.path.dirname(os.path.abspath(file_path))
    needs_root = not os.access(path_to_check, os.W_OK)

    if needs_root:
        console.print("[bold red]🔐 Access Denied: Root permissions required.[/bold red]")
        console.print("[bold yellow]Launching 'sudo vim' for secure editing...[/bold yellow]")
        try:
            # subprocess.run with sudo will allow the user to enter their password in the terminal
            subprocess.run(['sudo', 'vim', file_path])
            return
        except Exception as e:
            console.print(f"[bold red]❌ Critical Error launching sudo: {e}[/bold red]")
            return

    # Normal user editing
    editors = ['kate', 'gedit', 'pluma', 'vim', 'nano']
    opened = False
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("# --- AUDIT-LG INPUT BUFFER ---\n# Paste your logs below, save, and close the editor.\n")

    for editor in editors:
        try:
            subprocess.run(['which', editor], capture_output=True, check=True)
            console.print(f"[bold blue]🖥️  Opening {editor}... [/bold blue][dim]Save and close to begin analysis.[/dim]")
            subprocess.run([editor, file_path])
            opened = True
            break
        except subprocess.CalledProcessError:
            continue
    
    if not opened:
        console.print("[bold yellow]⚠️  No suitable editor found. Please manually edit audit-lg/put_logs_here.txt[/bold yellow]")

def load_model():
    with console.status("[bold green]🛡️  Initializing Neural Security Core...", spinner="dots"):
        model_path = "audit-lg/models/security_model.pkl"
        if not os.path.exists(model_path):
            console.print(f"[bold red][❌] Model not found at {model_path}. Run train.py first.")
            exit()
        return joblib.load(model_path)

model, vectorizer = load_model()

def save_report_json(results, file_path):
    os.makedirs("audit-lg/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = os.path.splitext(os.path.basename(file_path))[0]
    report_filename = f"report_{clean_name}_{timestamp}.json"
    report_path = os.path.join("../reports", report_filename)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)
    return report_path

def live_monitor(file_path):
    if not os.path.exists(file_path):
        console.print(f"[bold red]❌ Error: {file_path} not found.")
        return

    # Check for permission before starting
    use_sudo = False
    if not os.access(file_path, os.R_OK):
        console.print("[bold red]🔐 Access Denied: Root permissions required to tail this file.[/bold red]")
        confirm = Prompt.ask("Attempt to monitor with sudo?", choices=["y", "n"], default="y")
        if confirm == "y":
            use_sudo = True
        else:
            return

    console.print(Panel(f"🕵️  [bold green]REAL-TIME THREAT MONITORING[/bold green]\nTarget: [cyan]{file_path}[/cyan]\n[dim]Press Ctrl+C to terminate session[/dim]", border_style="blue"))
    
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Timestamp", style="dim", width=12)
    table.add_column("Classification", width=25)
    table.add_column("Event Log Source Data")

    try:
        if use_sudo:
            # Use sudo tail -f for live monitoring
            process = subprocess.Popen(['sudo', 'tail', '-n', '0', '-f', file_path], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     text=True)
            with Live(table, refresh_per_second=4, vertical_overflow="visible"):
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line: continue
                    
                    vec = vectorizer.transform([line])
                    res = model.predict(vec)[0]
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    status = f"[bold red]{ATTACK_TYPES[res]}[/bold red]" if res != 0 else "[bold green]✅ SAFE[/bold green]"
                    table.add_row(timestamp, status, line)
                    if len(table.rows) > 15: table.rows.pop(0)
        else:
            with open(file_path, "r") as f:
                f.seek(0, os.SEEK_END)
                with Live(table, refresh_per_second=4, vertical_overflow="visible"):
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                        line = line.strip()
                        if not line: continue
                        
                        vec = vectorizer.transform([line])
                        res = model.predict(vec)[0]
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        status = f"[bold red]{ATTACK_TYPES[res]}[/bold red]" if res != 0 else "[bold green]✅ SAFE[/bold green]"
                        table.add_row(timestamp, status, line)
                        if len(table.rows) > 15: table.rows.pop(0)
                        
    except KeyboardInterrupt:
        if use_sudo: process.terminate()
        console.print("\n[bold yellow]Monitoring Session Terminated.[/bold yellow]")

def scan_any_file(file_path):
    if not os.path.exists(file_path):
        console.print(Panel(f"[bold red][❌] ERROR: File '{file_path}' not found.", title="Scan Error", border_style="red"))
        return
    
    console.print(f"\n[bold blue]📂 Investigating:[/bold blue] [cyan]{file_path}[/cyan]...")
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip()]
    except PermissionError:
        console.print("[bold red]🔐 Access Denied: Root permissions required.[/bold red]")
        confirm = Prompt.ask("Attempt to read with sudo?", choices=["y", "n"], default="y")
        if confirm == "y":
            try:
                result = subprocess.run(['sudo', 'cat', file_path], capture_output=True, text=True, check=True)
                lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            except Exception as e:
                console.print(f"[bold red][❌] Sudo read failed: {e}")
                return
        else:
            return
    except Exception as e:
        console.print(f"[bold red][❌] Could not read file: {e}")
        return
    
    # Filter out comment lines
    lines = [l for l in lines if not l.startswith("#")]
    
    if not lines:
        console.print("[yellow][⚠️] Target file is empty or only contains comments.")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Processing {len(lines)} log vectors...", total=None)
        vec_batch = vectorizer.transform(lines)
        results = model.predict(vec_batch)
    
    attacks = [(i, res) for i, res in enumerate(results) if res != 0]
    
    # Advanced Dashboard Layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    
    summary_table = Table(title=f"DETECTION SUMMARY: {os.path.basename(file_path)}", expand=True, border_style="cyan")
    summary_table.add_column("Metric", style="bold cyan")
    summary_table.add_column("Count", justify="right")
    
    summary_table.add_row("Total Vectors Scanned", str(len(lines)))
    summary_table.add_row("Benign Activity", str(len(lines) - len(attacks)))
    summary_table.add_row("[bold red]Anomalies Detected[/bold red]", str(len(attacks)))
    
    console.print(summary_table)
    
    if attacks:
        attack_breakdown = {}
        for _, res in attacks:
            attack_breakdown[res] = attack_breakdown.get(res, 0) + 1
            
        breakdown_table = Table(title="THREAT CLASSIFICATION BREAKDOWN", border_style="red", expand=True)
        breakdown_table.add_column("Attack Vector", style="bold red")
        breakdown_table.add_column("Occurrences", justify="right")
        for label, count in attack_breakdown.items():
            breakdown_table.add_row(ATTACK_TYPES[label], str(count))
        console.print(breakdown_table)

        attack_list = Table(title="DETAILED INCIDENT SAMPLES (Top 5)", box=None, expand=True)
        attack_list.add_column("Line", style="dim", width=6)
        attack_list.add_column("Classification", style="bold red", width=25)
        attack_list.add_column("Evidence")
        for idx, res in attacks[:5]:
            attack_list.add_row(str(idx+1), ATTACK_TYPES[res], lines[idx])
        console.print(attack_list)
        
        export = Prompt.ask("\nGenerate Professional JSON Report?", choices=["y", "n"], default="n")
        if export == "y":
            data = {
                "file": file_path,
                "timestamp": str(datetime.now()),
                "metrics": {"total": len(lines), "attacks": len(attacks)},
                "incidents": [{"line": i+1, "type": ATTACK_TYPES[r], "content": lines[i]} for i, r in attacks]
            }
            path = save_report_json(data, file_path)
            console.print(f"[bold green]✅ Report Published: [cyan]{path}[/cyan][/bold green]")
    else:
        console.print(Panel("[bold green]✅ SYSTEM SECURE: No malicious vectors identified.[/bold green]", border_style="green"))

def main_menu():
    while True:
        console.print("\n")
        console.print(Panel.fit(
            "   [bold cyan]🛡️  AUDIT-LG: ADVANCED AI SECURITY SUITE v5.5[/bold cyan]   \n"
            "   [dim]Enterprise-Grade Log Analysis & Threat Intelligence[/dim]",
            border_style="bright_blue", padding=(1, 4)
        ))
        
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_row("[bold cyan]1.[/bold cyan] 📂 [bold]Deep Scan Custom File[/bold]")
        menu_table.add_row("[bold cyan]2.[/bold cyan] 📝 [bold yellow]Rapid Paste Audit (Auto-Editor)[/bold yellow]")
        menu_table.add_row("[bold cyan]3.[/bold cyan] ⚡ [bold magenta]Live Threat Intel (tail -f)[/bold magenta]")
        menu_table.add_row("[bold cyan]4.[/bold cyan] ⌨️  [bold]Analyze Single Log Vector[/bold]")
        menu_table.add_row("[bold cyan]5.[/bold cyan] 📁 [bold]Explore Intel Reports[/bold]")
        menu_table.add_row("[bold cyan]6.[/bold cyan] 🚪 [bold red]Terminate Session[/bold red]")
        
        console.print(Panel(menu_table, title="OPERATIONAL COMMANDS", border_style="dim", expand=False))
        
        choice = Prompt.ask("\n[bold]Execute Command[/bold]", choices=["1", "2", "3", "4", "5", "6"], default="1")
        
        if choice == "1":
            path = Prompt.ask("Path to target file")
            scan_any_file(path)
        elif choice == "2":
            log_file = "core/put_logs_here.txt"
            # Check if file has content other than our header/comments
            has_content = False
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                    if lines: has_content = True
            
            if has_content:
                console.print("\n[bold cyan]📝 Existing logs found in buffer.[/bold cyan]")
                console.print("[1] ➕ Add New Logs (Opens editor)")
                console.print("[2] 🚀 Scan Existing (Runs AI on current buffer)")
                action = Prompt.ask("Select action", choices=["1", "2"], default="1")
                
                if action == "1":
                    open_editor(log_file)
            else:
                open_editor(log_file)
            
            scan_any_file(log_file)
        elif choice == "3":
            path = Prompt.ask("Path to monitor", default="audit-lg/logs/soc_app.log")
            live_monitor(path)
        elif choice == "4":
            user_input = Prompt.ask("Enter log vector")
            vec = vectorizer.transform([user_input])
            res = model.predict(vec)[0]
            if res != 0:
                console.print(Panel(f"[bold red]THREAT DETECTED: {ATTACK_TYPES[res]}[/bold red]\nVector: {user_input}", border_style="red"))
            else:
                console.print(Panel(f"[bold green]VECTOR CLEAN[/bold green]\nVector: {user_input}", border_style="green"))
        elif choice == "5":
            os.system("ls -lh audit-lg/reports/ | head -n 10")
        elif choice == "6":
            console.print("[bold yellow]Security Core Deactivated. Goodbye. 🔒[/bold yellow]")
            break

if __name__ == "__main__":
    main_menu()
