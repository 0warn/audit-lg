# 🛡️ AUDIT-LG: YOUR DIGITAL SECURITY GUARD (v5.5)
### *An Easy-to-Use AI Scanner for Finding Hackers and Security Threats*

---

## 🌟 What is AUDIT-LG?
Think of **AUDIT-LG** as a high-tech security guard for your computer's "log files" (the diary where your computer writes down everything that happens). 

Instead of a human reading thousands of lines of boring text, our **AI (Artificial Intelligence)** reads them in seconds. It can spot "bad guys" trying to break in, even if they try to hide their tracks.

---

## 🚀 Quick Start (The "I Just Want it to Work" Guide)

If you have Python installed, just copy and paste these lines into your terminal (one by one):

1.  **Prepare the environment:**
    ```bash
    python3 -m venv venv && source venv/bin/activate
    ```
2.  **Install the software:**
    ```bash
    pip install -r audit-lg/requirements.txt
    ```
3.  **Start the Guard:**
    ```bash
    python audit-lg/main.py
    ```

---

## 🛠️ Detailed Installation (Step-by-Step)

### 1. Open your Terminal
On Linux, you can usually do this by pressing `Ctrl + Alt + T`.

### 2. Set up a "Private Room" (Virtual Environment)
Programs sometimes fight with each other. We create a "Virtual Environment" (a private room) so AUDIT-LG has everything it needs without bothering your other apps.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the Tools
This command downloads the "brain" and the "user interface" libraries.
```bash
pip install -r audit-lg/requirements.txt
```

---

## 🖥️ How to Use the Dashboard

When you run `python audit-lg/main.py`, you will see a menu. Here is what the options mean in plain English:

*   **Option 1: 📂 Deep Scan File**
    *   *What it does:* You give it a file (like a history of your web server), and it tells you if any hackers visited in the past.
*   **Option 2: 📝 Rapid Paste Audit**
    *   *What it does:* It opens a text window. You paste a suspicious line you found, save it, and the AI tells you immediately if it's dangerous.
*   **Option 3: ⚡ Live Threat Intel**
    *   *What it does:* The "Security Camera" mode. It watches a file as it happens. If a hacker tries to break in *right now*, the screen will flash **RED**.
*   **Option 4: ⌨ Analyze Single Line**
    *   *What it does:* Just type one thing (like a weird web link) and get an instant "Safe" or "Danger" verdict.
*   **Option 6: 🚪 Terminate Session**
    *   *What it does:* Safely turns off the security suite.

---

## 🧠 How the AI "Thinks" (Simple Explanation)

Most security tools look for "Bad Words." But hackers are smart—they use "Secret Codes" or symbols to hide.

**AUDIT-LG is different.** It doesn't just look for words; it looks for **Patterns**. 
- It breaks every line into tiny 3-to-5 character chunks (we call these *N-grams*). 
- It has seen millions of examples of "Good" and "Bad" patterns.
- Even if a hacker changes a few letters, the "mathematical shape" of the attack stays the same, and our AI catches it.

---

## 🔧 "Help! Something is Wrong" (Troubleshooting)

### ❓ "It says 'Model not found'!"
**Fix:** The AI needs to "learn" first. Run this command:
```bash
cd audit-lg && python train.py && cd ..
```
This builds the "Brain" of the system.

### ❓ "It says 'Access Denied' when I try to scan a file!"
**Fix:** Some files are private (only the 'Root' or 'Admin' can see them). When the program asks, type `y` to use `sudo`. You will need to type your computer password.

### ❓ "Which command should I run to start?"
**Fix:** Always run this from the main folder:
```bash
python audit-lg/main.py
```

### ❓ "The screen is messy or text is overlapping!"
**Fix:** Make your terminal window larger. AUDIT-LG uses a "Pro" interface that looks best on a big screen.

---

## 📁 Where is everything?
- **reports/**: This is where the AI saves "Incident Reports" (proof of attacks it found).
- **data/**: The "library" of logs the AI used to study.
- **models/**: The actual "Brain" file (`security_model.pkl`).

---

**AUDIT-LG** is maintained by **zero warn**.
*Making Enterprise-Grade Security simple for everyone.*
*Licensed under the MIT License.*
