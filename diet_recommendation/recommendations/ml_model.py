
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load CSV data
df = pd.read_csv('data/ghanaian_foods.csv')



# Preprocess data
X = df[['Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)']]
y = df['Recommended Diet']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model Accuracy: {accuracy * 100:.2f}%')

# Save the model
joblib.dump(model, 'data/diet_recommendation_model.pkl')
