# ml_model.py

import os
import pandas as pd
import tensorflow as tf
import joblib
from django.conf import settings

# Define the data directory path
DATA_DIR = os.path.join(settings.BASE_DIR, 'recommendations', 'data')

# Load the trained model, scaler, and label encoder
model_path = os.path.join(DATA_DIR, 'diet_recommendation_model.h5')
scaler_path = os.path.join(DATA_DIR, 'scaler.pkl')
label_encoder_path = os.path.join(DATA_DIR, 'label_encoder.pkl')

model = tf.keras.models.load_model(model_path)
scaler = joblib.load(scaler_path)
label_encoder = joblib.load(label_encoder_path)

# Load the CSV data for diet recommendations
csv_path = os.path.join(DATA_DIR, 'diet_dataset.csv')
df = pd.read_csv(csv_path)

def recommend_diets(user_bmi, health_goal, n_recommendations=10):
    if health_goal == 'gain weight':
        target_categories = ['Normal weight', 'Overweight']
    elif health_goal == 'lose weight':
        target_categories = ['Underweight', 'Normal weight']
    elif health_goal == 'maintain weight':
        target_categories = ['Normal weight']
    else:
        raise ValueError("Health goal must be 'gain weight', 'lose weight', or 'maintain weight'.")

    # Filter based on target BMI categories
    filtered_df = df[df['BMI Category'].isin(target_categories)]

    # Ensure diverse meal types in recommendations
    recommended_diets = (
        filtered_df.groupby('Meal Type')
        .apply(lambda x: x.sample(min(len(x), n_recommendations // len(filtered_df['Meal Type'].unique()))))
        .reset_index(drop=True)
    )

    if len(recommended_diets) < n_recommendations:
        additional_diets = filtered_df.sample(n_recommendations - len(recommended_diets))
        recommended_diets = pd.concat([recommended_diets, additional_diets], ignore_index=True)

    return recommended_diets.head(n_recommendations)

def predict_diets(recommended_diets):
    features = ['Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'BMI']
    
    # Ensure the DataFrame has the correct feature names
    recommended_diets = recommended_diets.rename(columns={
        'Calories_kcal': 'Calories (kcal)',
        'Protein_g': 'Protein (g)',
        'Carbs_g': 'Carbs (g)',
        'Fat_g': 'Fat (g)',
        'BMI': 'BMI',
    })

    if not set(features).issubset(recommended_diets.columns):
        raise ValueError("DataFrame does not contain all required features")

    X_test_sample = scaler.transform(recommended_diets[features])

    # Predict diet types using the trained model
    y_pred_sample = model.predict(X_test_sample)
    y_pred_classes_sample = y_pred_sample.argmax(axis=1)

    # Decode the predictions to get diet names
    y_pred_decoded_sample = label_encoder.inverse_transform(y_pred_classes_sample)

    # Add the predicted diet type to the recommended_diets DataFrame
    recommended_diets['Predicted_Diet'] = y_pred_decoded_sample

    return recommended_diets[['Predicted_Diet', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'BMI']]
