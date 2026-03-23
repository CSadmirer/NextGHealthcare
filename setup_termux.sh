#!/data/data/com.termux/files/usr/bin/bash
pkg update -y && pkg upgrade -y
pkg install python git -y
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
echo "Copy .env.example to .env and edit the values."
