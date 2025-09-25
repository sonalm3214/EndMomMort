# model_training.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# --- Sample dataset with extra features ---
data = {
    'Age': [22,25,30,35,28,40,32,26,31,29],
    'DiastolicBP': [70,80,85,90,75,95,88,82,86,78],
    'BS': [12.0,15.0,10.5,18.0,14.0,20.0,16.0,13.5,17.0,14.5],
    'BodyTemp': [98.0,98.6,99.0,98.4,98.2,99.1,98.8,98.5,98.9,98.3],
    'BMI': [22, 25, 28, 30, 24, 32, 27, 23, 29, 26],
    'Pregnancies': [0,1,2,3,1,4,2,1,3,2],
    'Hypertension': ['No','No','Yes','Yes','No','Yes','No','No','Yes','No'],
    'Diabetes': ['No','Yes','No','Yes','No','Yes','No','No','Yes','No'],
    'RiskLevel': [0,1,0,2,1,2,1,0,2,1]
}

df = pd.DataFrame(data)

# Encode categorical features
le = LabelEncoder()
df['Hypertension'] = le.fit_transform(df['Hypertension'])  # No=0, Yes=1
df['Diabetes'] = le.fit_transform(df['Diabetes'])          # No=0, Yes=1

# Features and target
features = ['Age', 'DiastolicBP', 'BS', 'BodyTemp', 'BMI', 'Pregnancies', 'Hypertension', 'Diabetes']
X = df[features]
y = df['RiskLevel']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train RandomForest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Save model and scaler
joblib.dump(model, 'final_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("Model saved with extra features!")
