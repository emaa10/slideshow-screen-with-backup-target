#!/bin/bash
# ========================================
# iCloud Diashow Automatisierung Raspberry Pi
# mit Git-Autocommit um 20 Uhr
# ========================================

ICLOUD_URL="https://www.icloud.com/sharedalbum/#B2FGrq0zw8zaKSC"
BASE_DIR="$HOME/icloud"
IMG_DIR="$BASE_DIR/images"
LOG_FILE="$BASE_DIR/log.txt"
SCRIPT_PATH="$BASE_DIR/icloud_photo.sh"

# Log-Funktion
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ----------------------------------------
# 1. iCloud Bilder täglich um 20 Uhr aktualisieren
# ----------------------------------------
update_photos() {
  log "Starte iCloud-Bilder-Update ..."
  cd "$BASE_DIR" || exit 1
  "$SCRIPT_PATH" "$ICLOUD_URL" "$IMG_DIR" >> "$LOG_FILE" 2>&1
  log "Update abgeschlossen."
}

# ----------------------------------------
# 2. Git-Autocommit & Push
# ----------------------------------------
git_push() {
  cd "$BASE_DIR" || exit 1

  if [ ! -d .git ]; then
    log "Kein Git-Repository gefunden. Überspringe Git-Push."
    return
  fi

  log "Führe Git-Commit & Push aus ..."
  git add . >> "$LOG_FILE" 2>&1
  git commit -am "Auto-Update $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1 || log "Keine Änderungen zu committen."
  git pull --rebase >> "$LOG_FILE" 2>&1
  git push >> "$LOG_FILE" 2>&1
  log "Git-Push abgeschlossen."
}

# ----------------------------------------
# 3. Diashow-Funktion mit Zeitsteuerung
# ----------------------------------------
start_slideshow() {
  log "Starte Diashow zwischen 12:00 und 18:00 Uhr ..."
  mkdir -p "$IMG_DIR"

  while true; do
    HOUR=$(date +%H)
  
    # Beende Skript nach 20 Uhr
    if (( HOUR >= 20 )); then
      log "Beende Diashow, da es 20 Uhr oder später ist."
      #xset dpms force off
      killall pqiv
      exit 0
    fi

    if (( HOUR >= 12 && HOUR < 18 )); then
      log "Starte Diashow ..."
      pqiv --fullscreen --slideshow --slideshow-interval=30 --fade --fade-duration=1.0 --hide-info-box --scale-images-up --background-pattern=black --shuffle --watch-directories --wait-for-images-to-appear /home/pi/icloud/images/
    else
      log "Außerhalb 12–18 Uhr – Bildschirm dunkel."
      killall pqiv
      #xset dpms force off
      sleep 300
    fi
  done

}

# ----------------------------------------
# Hauptlogik
# ----------------------------------------
case "$1" in
  update)
    update_photos
    git_push
    ;;
  run)
    start_slideshow
    ;;
  *)
    echo "Verwendung: $0 {update|run}"
    ;;
esac

