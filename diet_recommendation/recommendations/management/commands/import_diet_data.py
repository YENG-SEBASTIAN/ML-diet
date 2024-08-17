import csv
import os
from django.core.management.base import BaseCommand
from recommendations.models import DietRecommendationDataset

class Command(BaseCommand):
    help = 'Import diet recommendation data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The relative path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Construct the full path to the CSV file relative to the Django project root
        csv_file_path = os.path.join(os.getcwd(), csv_file)

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
            return

        with open(csv_file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                DietRecommendationDataset.objects.create(
                    recommended_diet=row['Recommended Diet'],
                    calories_kcal=int(row['Calories (kcal)']),
                    protein_g=int(row['Protein (g)']),
                    carbs_g=int(row['Carbs (g)']),
                    fat_g=int(row['Fat (g)']),
                    health_benefits=row['Health Benefits'],
                    suitable_age_group=row['Suitable Age Group'],
                    meal_type=row['Meal Type'],
                    bmi=float(row['BMI']),
                    bmi_category=row['BMI Category']
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
