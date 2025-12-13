#!/usr/bin/env python3
"""
MagicMirror Scheduler mit Discord Logging
- Startet MagicMirror zwischen 8-20 Uhr
- Um 7:00-7:05 Uhr: iCloud Foto-Sync
- Ab 20:00 Uhr: MagicMirror sicher beenden
- Stündliches System-Monitoring via Discord
- Error Detection & Auto-Restart
"""

import subprocess
import os
import time
import json
import psutil
from datetime import datetime
import requests
from pathlib import Path

# ========== KONFIGURATION ==========
DISCORD_WEBHOOK = ""
MM_DIR = "/home/pi/MagicMirror"
MM_START_CMD = f'cd {MM_DIR} && NODE_OPTIONS="--dns-result-order=ipv4first" node --run start'
ICLOUD_SCRIPT = "/home/pi/icloud/icloud_photo.sh"
ICLOUD_URL = ""
ICLOUD_DIR = "/home/pi/icloud/images"
ICLOUD_LOG = "/home/pi/icloud/log.txt"
STATE_FILE = "/tmp/magicmirror_scheduler.state"
MM_LOG_FILE = "/tmp/magicmirror.log"  # NEU: Log-Datei für MagicMirror Output

# ========== DISCORD FUNKTIONEN ==========
def send_discord(message, title="MagicMirror Scheduler"):
    """Sendet Nachricht an Discord Webhook"""
    try:
        data = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 3447003,  # Blau
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "Raspberry Pi"}
            }]
        }
        response = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        if response.status_code != 204:
            print(f"Discord webhook error: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

def send_system_stats():
    """Sendet System-Statistiken an Discord"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        temp = get_cpu_temp()

        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        uptime_str = str(uptime).split('.')[0]  # Ohne Millisekunden

        message = (
            f"**CPU:** {cpu_percent}%\n"
            f"**RAM:** {memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)\n"
            f"**Disk:** {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)\n"
            f"**Temperature:** {temp}°C\n"
            f"**Uptime:** {uptime_str}\n"
            f"**MagicMirror:** {'Running ✅' if is_magicmirror_running() else 'Stopped ⛔'}"
        )
        send_discord(message, title="📊 System Status")
    except Exception as e:
        send_discord(f"Error getting system stats: {e}", title="⚠️ Error")

def get_cpu_temp():
    """Liest CPU Temperatur aus"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
            return round(temp, 1)
    except:
        return "N/A"

def turn_display_off():
    """Schaltet HDMI Display aus"""
    try:
        subprocess.run(['sudo', 'tee', '/sys/class/drm/card0-HDMI-A-1/status'],
                      input=b'off', check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error turning display off: {e}")
        return False

def turn_display_on():
    """Schaltet HDMI Display ein"""
    try:
        subprocess.run(['sudo', 'tee', '/sys/class/drm/card0-HDMI-A-1/status'],
                      input=b'on', check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error turning display on: {e}")
        return False

def is_display_on():
    """Prüft ob Display an ist"""
    try:
        result = subprocess.run(['cat', '/sys/class/drm/card0-HDMI-A-1/status'],
                               capture_output=True, text=True, check=True)
        return 'on' in result.stdout.lower()
    except:
        return None

# ========== MAGICMIRROR FUNKTIONEN ==========
def is_magicmirror_running():
    """Prüft ob MagicMirror läuft"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('MagicMirror' in str(arg) for arg in cmdline):
                if 'node' in str(cmdline).lower():
                    return True
        return False
    except Exception as e:
        print(f"Error checking MagicMirror status: {e}")
        return False

def check_magicmirror_errors():
    """Prüft ob MagicMirror Fehler im Log hat - NEU"""
    try:
        if not os.path.exists(MM_LOG_FILE):
            return None
        
        # Lese nur die letzten 100 Zeilen
        result = subprocess.run(
            ['tail', '-n', '100', MM_LOG_FILE],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        log_content = result.stdout
        
        # Suche nach ERROR oder FATAL in den letzten Zeilen
        error_lines = []
        for line in log_content.split('\n'):
            if '[ERROR]' in line or '[FATAL]' in line:
                error_lines.append(line)
        
        if error_lines:
            # Gib die letzten 5 Fehler zurück
            return '\n'.join(error_lines[-5:])
        
        return None
    except Exception as e:
        print(f"Error checking MagicMirror logs: {e}")
        return None

def start_magicmirror():
    """Startet MagicMirror in einer screen Session"""
    if is_magicmirror_running():
        return False

    try:
        # Prüfe ob screen Session bereits existiert
        check_screen = subprocess.run(
            ['screen', '-list'],
            capture_output=True,
            text=True
        )

        if 'magicmirror' in check_screen.stdout.lower():
            # Alte screen Session killen
            subprocess.run(['screen', '-S', 'magicmirror', '-X', 'quit'],
                         stderr=subprocess.DEVNULL)
            time.sleep(2)

        # Start in screen session MIT Log-Redirect - GEÄNDERT
        screen_cmd = f'screen -dmS magicmirror bash -c "{MM_START_CMD} 2>&1 | tee -a {MM_LOG_FILE}"'
        subprocess.run(screen_cmd, shell=True, cwd=MM_DIR)
        time.sleep(5)  # Warte 5 Sekunden

        if is_magicmirror_running():
            turn_display_on()
            send_discord("MagicMirror gestartet ✅ + Display an (Screen: `magicmirror`)", title="🚀 Start")
            save_state("running")
            print("✅ MagicMirror started successfully")
            return True
        else:
            send_discord("MagicMirror Start fehlgeschlagen ❌", title="⚠️ Error")
            print("❌ MagicMirror failed to start")
            return False
    except Exception as e:
        send_discord(f"Error starting MagicMirror: {e}", title="⚠️ Error")
        print(f"❌ Exception starting MagicMirror: {e}")
        return False

def stop_magicmirror():
    """Stoppt MagicMirror"""
    if not is_magicmirror_running():
        #print("MagicMirror is not running")
        return False

    try:
        #print("Stopping MagicMirror...")
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('MagicMirror' in str(arg) for arg in cmdline):
                if 'node' in str(cmdline).lower():
                    proc.terminate()
                    killed = True

        time.sleep(3)

        # Force kill falls noch läuft
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('MagicMirror' in str(arg) for arg in cmdline):
                if 'node' in str(cmdline).lower():
                    proc.kill()
                    killed = True

        if killed:
            turn_display_off()  # NEU
            send_discord("MagicMirror gestoppt 🛑 + Display aus 📺", title="⏹️ Stop")
            save_state("stopped")
            return True
        else:
            return False
    except Exception as e:
        send_discord(f"Error stopping MagicMirror: {e}", title="⚠️ Error")
        return False

# ========== ICLOUD SYNC ==========
def run_icloud_sync():
    """Führt iCloud Foto-Sync aus"""
    try:
        print("Starting iCloud sync...")
        send_discord("iCloud Foto-Sync gestartet...", title="☁️ iCloud Sync")

        with open(ICLOUD_LOG, 'a') as log_file:
            log_file.write(f"\n=== Sync started at {datetime.now()} ===\n")
            result = subprocess.run(
                [ICLOUD_SCRIPT, ICLOUD_URL, ICLOUD_DIR],
                stdout=log_file,
                stderr=log_file,
                timeout=600  # 10 Minuten Timeout
            )

        if result.returncode == 0:
            send_discord("iCloud Foto-Sync erfolgreich ✅", title="☁️ iCloud Sync")
        else:
            send_discord(f"iCloud Foto-Sync fehlgeschlagen (Exit: {result.returncode}) ❌", title="⚠️ iCloud Error")
        try:
            if os.path.exists(ICLOUD_LOG):
                with open(ICLOUD_LOG, 'r') as f:
                    log_content = f.read()[-1800:]  # nur die letzten 1800 Zeichen, damit es nicht zu groß wird
                send_discord(f"```\n{log_content}\n```", title="📄 iCloud Log")
            else:
                send_discord("⚠️ Keine Log-Datei gefunden unter /home/pi/icloud/log.txt", title="📄 iCloud Log")
        except Exception as e:
            send_discord(f"Fehler beim Senden der Log-Datei: {e}", title="⚠️ iCloud Log Error")


        return result.returncode == 0
    except subprocess.TimeoutExpired:
        send_discord("iCloud Foto-Sync Timeout (>10min) ⏱️", title="⚠️ iCloud Timeout")
        return False
    except Exception as e:
        send_discord(f"iCloud Sync Error: {e}", title="⚠️ Error")
        return False

# ========== STATE MANAGEMENT ==========
def save_state(state):
    """Speichert aktuellen Zustand"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'state': state,
                'timestamp': datetime.now().isoformat()
            }, f)
    except Exception as e:
        print(f"Error saving state: {e}")

def load_state():
    """Lädt gespeicherten Zustand"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('state', 'unknown')
    except:
        pass
    return 'unknown'

def get_last_action_time():
    """Gibt letzte Aktion zurück (für Debugging)"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('timestamp', 'unknown')
    except:
        pass
    return 'unknown'

# ========== HAUPTLOGIK ==========
def main():
    """Hauptlogik - wird jede Minute von Cron aufgerufen"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    #print(f"Running scheduler at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    #print(f"Hour: {hour}, Minute: {minute}")
    #print(f"MagicMirror running: {is_magicmirror_running()}")

    # Um 7:00-7:15 Uhr: iCloud Sync (nur einmal im Zeitfenster)
    if hour == 7 and minute == 0:
        run_icloud_sync()

    # Um 8:00 Uhr: MagicMirror starten
    if hour == 8 and minute == 0:
        if not is_magicmirror_running():
            start_magicmirror()
        #else:
            #print("MagicMirror already running at 8:00")

    # Zwischen 8-19 Uhr: Stelle sicher dass MM läuft (watchdog) + Error Detection - ERWEITERT
    if 8 <= hour < 20:
        if not is_magicmirror_running():
            saved_state = load_state()
            # Nur auto-restart wenn nicht manuell gestoppt
            if saved_state != 'stopped_manually':
                send_discord("MagicMirror war nicht aktiv, starte neu...", title="🔄 Watchdog Restart")
                start_magicmirror()
        else:
            # NEU: Prüfe auf Fehler im Log (alle 5 Minuten)
            if minute % 5 == 0:
                errors = check_magicmirror_errors()
                if errors:
                    # Sende Fehler an Discord
                    error_preview = errors[:1500]  # Maximal 1500 Zeichen
                    send_discord(f"**Fehler erkannt:**\n```\n{error_preview}\n```\n\nNeustart wird durchgeführt...", 
                               title="⚠️ MagicMirror Error Detected")
                    
                    # Stoppe und starte neu
                    stop_magicmirror()
                    time.sleep(3)
                    start_magicmirror()

    # Ab 20:00 Uhr bis 7:59 Uhr: Stelle sicher dass MM NICHT läuft
    if hour >= 20 or hour < 8:
        if is_magicmirror_running():
            #print(f"MagicMirror should not be running at {hour}:00 - stopping it")
            send_discord(f"MagicMirror läuft außerhalb der Betriebszeiten ({hour}:{minute:02d}) - wird gestoppt",
                        title="⚠️ Auto-Stop")
            stop_magicmirror()

        if is_display_on():
            turn_display_off()
            if minute == 0:  # Nur zur vollen Stunde melden
                send_discord("Display war an, wurde ausgeschaltet 📺", title="🌙 Display Off")

    # Stündlich: System-Stats senden (zur vollen Stunde, nur zwischen 8-20 Uhr)
    if minute == 0 and 8 <= hour <= 20:
        send_system_stats()

if __name__ == "__main__":
    main()
