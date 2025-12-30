import os
import sys

required_files = [
    "app/main.py",
    "app/scanner.py",
    "app/vector_engine.py",
    "app/vector_db.py",
    "app/preprocessor.py",
    "app/config.py",
    "app/logger.py",
    "signatures.json",
    "classifier.pkl",
    "main.py"
]

required_dirs = [
    "models",
    "chroma_db"
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

missing_dirs = []
for dir_path in required_dirs:
    if not os.path.exists(dir_path):
        missing_dirs.append(dir_path)

if missing_files or missing_dirs:
    print("ОШИБКА: Отсутствуют необходимые файлы/директории:")
    for item in missing_files + missing_dirs:
        print(f"  - {item}")
    sys.exit(1)

if not os.path.exists("chroma_db/chroma.sqlite3"):
    print("ПРЕДУПРЕЖДЕНИЕ: База данных ChromaDB не инициализирована.")
    print("Запустите: python ingest.py")
else:
    print("База данных ChromaDB найдена.")

if not os.path.exists("classifier.pkl"):
    print("ПРЕДУПРЕЖДЕНИЕ: Классификатор не обучен.")
    print("Запустите: python train_head.py")
else:
    print("Классификатор найден.")

print("\nВсе необходимые компоненты на месте!")
print("Система готова к работе.")






