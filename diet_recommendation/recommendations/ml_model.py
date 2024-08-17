import pandas as pd
import tensorflow as tf
import joblib
import os

# Load the saved model, scaler, and label encoder from the data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'recommendations', 'data')

model = tf.keras.models.load_model(os.path.join(MODEL_DIR, 'diet_recommendation_model.h5'))
scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
label_encoder = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))

# Load CSV data for recommendations
file_path = os.path.join(MODEL_DIR, 'diet_dataset.csv')
df = pd.read_csv(file_path)


def recommend_diets(user_bmi, health_goal, n_recommendations=10):
    # Determine the target BMI categories based on health goal
    if health_goal == 'gain weight':
        target_categories = ['Normal weight', 'Overweight']
    elif health_goal == 'lose weight':
        target_categories = ['Underweight', 'Normal weight']
    elif health_goal == 'maintain weight':
        target_categories = ['Normal weight']
    else:
        raise ValueError("Health goal must be 'gain weight', 'lose weight', or 'maintain weight'.")

    # Filter diets based on the target BMI categories
    filtered_df = df[df['BMI Category'].isin(target_categories)]

    # Ensure a combination of meal types
    recommended_diets = filtered_df.groupby('Meal Type').apply(
        lambda x: x.sample(min(len(x), n_recommendations // len(filtered_df['Meal Type'].unique())))
    ).reset_index(drop=True)

    # If the number of recommended diets is less than requested, sample additional diets
    if len(recommended_diets) < n_recommendations:
        additional_diets = filtered_df.sample(n_recommendations - len(recommended_diets))
        recommended_diets = pd.concat([recommended_diets, additional_diets], ignore_index=True)

    # Prepare data for model prediction
    X_test_sample = scaler.transform(recommended_diets[['Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'BMI']])
    y_pred_sample = model.predict(X_test_sample)
    y_pred_classes_sample = y_pred_sample.argmax(axis=1)

    # Decode the predictions
    y_pred_decoded_sample = label_encoder.inverse_transform(y_pred_classes_sample)

    # Add predictions to the DataFrame
    recommended_diets['Predicted Diet'] = y_pred_decoded_sample

    return recommended_diets.head(n_recommendations)
