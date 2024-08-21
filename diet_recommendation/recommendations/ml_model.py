import pandas as pd
import joblib
import os
import logging

logger = logging.getLogger(__name__)

try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR = os.path.join(BASE_DIR, 'recommendations', 'data')
    
    # Load the trained model and scaler/label encoder from disk
    # Assuming you're fetching these from a remote service, otherwise remove these lines.
    # model = tf.keras.models.load_model(os.path.join(MODEL_DIR, 'diet_recommendation_model.h5'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    label_encoder = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))

    file_path = os.path.join(MODEL_DIR, 'diet_dataset.csv')
    df = pd.read_csv(file_path)
except Exception as e:
    logger.error(f"Error loading model or data: {e}")
    raise

def recommend_diets(user_bmi, health_goal, n_recommendations=10):
    try:
        if health_goal == 'gain weight':
            target_categories = ['Normal weight', 'Overweight']
        elif health_goal == 'lose weight':
            target_categories = ['Underweight', 'Normal weight']
        elif health_goal == 'maintain weight':
            target_categories = ['Normal weight']
        else:
            raise ValueError("Health goal must be 'gain weight', 'lose weight', or 'maintain weight'.")

        filtered_df = df[df['BMI Category'].isin(target_categories)]

        recommended_diets = filtered_df.groupby('Meal Type').apply(
            lambda x: x.sample(min(len(x), n_recommendations // len(filtered_df['Meal Type'].unique())))
        ).reset_index(drop=True)

        if len(recommended_diets) < n_recommendations:
            additional_diets = filtered_df.sample(n_recommendations - len(recommended_diets))
            recommended_diets = pd.concat([recommended_diets, additional_diets], ignore_index=True)

        # X_test_sample = scaler.transform(recommended_diets[['Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'BMI']])
        # y_pred_sample = model.predict(X_test_sample)
        # y_pred_classes_sample = y_pred_sample.argmax(axis=1)

        # Mock predictions if TensorFlow is not available
        recommended_diets['Predicted Diet'] = 'Mocked Diet'  # or any mock function

        return recommended_diets.head(n_recommendations)
    except Exception as e:
        logger.error(f"Error during diet recommendation: {e}")
        raise
