import pandas as pd
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from app.vector_engine import VectorEngine
from app.preprocessor import TextPreprocessor

def main():
    print("Загрузка датасета...")
    df = pd.read_csv("dataset.csv")
    
    print(f"Всего записей: {len(df)}")
    print(f"Атаки (label=1): {len(df[df['label'] == 1])}")
    print(f"Безопасные (label=0): {len(df[df['label'] == 0])}")
    
    print("Инициализация компонентов...")
    vector_engine = VectorEngine()
    preprocessor = TextPreprocessor()
    
    print("Предобработка и векторизация...")
    texts = df['text'].tolist()
    labels = df['label'].tolist()
    
    processed_texts = [preprocessor.preprocess(text) for text in texts]
    vectors = vector_engine.encode_batch(processed_texts)
    
    print("Разделение на train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        vectors, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print("Обучение классификатора...")
    classifier = LogisticRegression(random_state=42, max_iter=1000)
    classifier.fit(X_train, y_train)
    
    print("Оценка качества...")
    y_pred = classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Точность: {accuracy:.4f}")
    print("\nОтчет по классификации:")
    print(classification_report(y_test, y_pred))
    
    print("Сохранение модели...")
    model_path = "classifier.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(classifier, f)
    
    file_size = os.path.getsize(model_path) / 1024
    print(f"Модель сохранена в {model_path} (размер: {file_size:.2f} Кб)")

if __name__ == "__main__":
    main()


