#!/bin/bash

if [ ! -f "chroma_db/chroma.sqlite3" ]; then
    echo "Инициализация базы данных..."
    python ingest.py
fi

echo "Запуск сервера..."
python main.py






