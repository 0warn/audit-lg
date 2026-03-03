import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os

print("🚀 Loading Multi-Class SOC Dataset...")
df = pd.read_csv("data/master_security_dataset.csv")

print("🧠 Extracting High-Dimensional Features (Character-Level TF-IDF)...")
# Character-level n-grams are crucial for security as they catch snippets like "' OR '1'='1" 
# even if there are no spaces or standard words.
vectorizer = TfidfVectorizer(max_features=5000, analyzer='char', ngram_range=(3, 5), min_df=2)
X = vectorizer.fit_transform(df['log_text']) # Keep it sparse! No .toarray()
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

print("🏗️  Building Ultra-Efficient AI (SGD Classifier)...")
# SGDClassifier is ideal for sparse text data and extremely fast for 1M+ rows
model = SGDClassifier(loss='modified_huber', max_iter=100, tol=1e-3, random_state=42)
model.fit(X_train, y_train)

print("🧪 Testing Advanced Accuracy...")
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"\n✅ SUCCESS: Enhanced Training complete!")
print(f"📊 Final Robust Accuracy: {acc * 100:.2f}%")
print("\nDetailed Report:")
print(classification_report(y_test, preds))

os.makedirs("audit-lg/models", exist_ok=True)
joblib.dump((model, vectorizer), "models/security_model.pkl")
print("✅ Saved Future-Proof Model to models/security_model.pkl")
