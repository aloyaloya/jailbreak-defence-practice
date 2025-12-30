# -*- coding: utf-8 -*-
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("Проверка офлайн режима:")
print(f"  Модель: {'OK' if os.path.exists('models/models--cointegrated--rubert-tiny2/snapshots') else 'MISSING'}")
print(f"  Классификатор: {'OK' if os.path.exists('classifier.pkl') else 'MISSING'}")
print(f"  База данных: {'OK' if os.path.exists('chroma_db') else 'MISSING'}")
print(f"  signatures.json: {'OK' if os.path.exists('signatures.json') else 'MISSING'}")

all_ok = (
    os.path.exists('models/models--cointegrated--rubert-tiny2/snapshots') and
    os.path.exists('classifier.pkl') and
    os.path.exists('chroma_db')
)

if all_ok:
    print("\nВсе компоненты на месте. Система готова к офлайн работе!")
else:
    print("\nНекоторые компоненты отсутствуют. Запустите:")
    print("  - train_classifier.py (для создания classifier.pkl)")
    print("  - ingest.py (для создания chroma_db)")

