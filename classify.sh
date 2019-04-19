#/bin/bash
# arg 1: freq
# arg 2: name
timeout 60s python base_wifi_rx.py $1 2>/dev/null | python3 classi.py $2
