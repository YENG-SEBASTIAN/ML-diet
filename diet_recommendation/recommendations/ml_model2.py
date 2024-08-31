import os
import joblib
import pandas as pd
import tensorflow as tf
from django.conf import settings

# Define the data directory path
DATA_DIR = os.path.join(settings.BASE_DIR, 'recommendations', 'data')

# Load the trained model
model_path = os.path.join(DATA_DIR, 'model.h5')
model = tf.keras.models.load_model(model_path)

# Load LabelEncoders from .pkl files
bmi_encoder_path = os.path.join(DATA_DIR, 'le_bmi_category.pkl')
meal_type_encoder_path = os.path.join(DATA_DIR, 'le_meal_type.pkl')

# Load the LabelEncoders
le_bmi_category = joblib.load(bmi_encoder_path)
le_meal_type = joblib.load(meal_type_encoder_path)

# Load the dataset for diet recommendations
data_file_path = os.path.join(DATA_DIR, 'food_diet.csv')
df = pd.read_csv(data_file_path)

def recommend_diets(bmi, bmi_category):
    """Recommend diets based on BMI and BMI category."""
    # Encode the BMI category using the loaded LabelEncoder
    bmi_category_encoded = le_bmi_category.transform([bmi_category])[0]
    
    # Create a DataFrame for prediction input
    prediction_input = pd.DataFrame({'BMI': [bmi], 'BMI_Category': [bmi_category_encoded]})
    
    # Predict the meal type using the loaded model
    prediction_input_values = prediction_input.values
    meal_type_pred = model.predict(prediction_input_values)
    meal_type_pred_class = meal_type_pred.argmax(axis=1)[0]
    
    # Decode the meal type to the original label
    meal_type_decoded = le_meal_type.inverse_transform([meal_type_pred_class])[0]
    
    # Filter the recommended diets for the BMI category
    recommended_diets = df[df['BMI Category'] == bmi_category]
    
    # Group by Meal Type and get at least 3 diets per meal type
    diets_by_meal_type = recommended_diets.groupby('Meal Type', group_keys=False).apply(lambda x: x.sample(n=min(3, len(x)), replace=True))
    
    # Reset the index for easier manipulation
    diets_by_meal_type.reset_index(drop=True, inplace=True)
    
    # Ensure a mix of all meal types
    unique_meal_types = recommended_diets['Meal Type'].unique()
    final_recommendations = pd.DataFrame()

    for meal_type in unique_meal_types:
        meal_diets = diets_by_meal_type[diets_by_meal_type['Meal Type'] == meal_type]
        
        # If there are less than 3, resample from the available diets
        if len(meal_diets) < 3:
            additional_diets = recommended_diets[recommended_diets['Meal Type'] == meal_type].sample(n=3 - len(meal_diets), replace=True)
            meal_diets = pd.concat([meal_diets, additional_diets])
        
        final_recommendations = pd.concat([final_recommendations, meal_diets])
    
    # Ensure to reset the index for final output
    final_recommendations.reset_index(drop=True, inplace=True)

    # Return the recommended diets
    return final_recommendations[['Meal Type', 'Recommended Diet', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Vitamins', 'Minerals', 'Health Benefits']]
