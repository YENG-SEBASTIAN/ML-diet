from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import joblib
import pandas as pd
import os

# Define the path to the trained model
MODEL_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'diet_recommendation_model.pkl')

# Load the trained model
try:
    model = joblib.load(MODEL_FILE_PATH)
except FileNotFoundError:
    model = None
    print(f"Model file '{MODEL_FILE_PATH}' not found.")
except Exception as e:
    model = None
    print(f"Error loading model: {str(e)}")

class RecommendDiet(APIView):
    def post(self, request):
        if model is None:
            return Response({"error": "Model not found or failed to load."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = request.data
        try:
            input_data = pd.DataFrame([data])
            prediction = model.predict(input_data)[0]
            return Response({'Recommended Diet': prediction})
        except Exception as e:
            return Response({"error": f"Prediction error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
