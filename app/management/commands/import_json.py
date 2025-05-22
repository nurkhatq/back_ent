from django.core.management.base import BaseCommand
from app.models import Test, Question, QuestionImage, Option
import json
import os

class Command(BaseCommand):
    help = 'Import JSON data to database'

    def handle(self, *args, **options):
        json_dir = "/code/json_output"  # путь к JSON файлам внутри контейнера
        
        for filename in os.listdir(json_dir):
            if not filename.endswith('.json'):
                continue
                
            self.stdout.write(f'Processing {filename}...')
            
            with open(os.path.join(json_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            test = Test.objects.create(
                title=data['title'],
                total_questions=data['total_questions'],
                multiple_answers_allowed=data['multiple_answers_allowed'],
                has_images=data.get('has_images', False)
            )
            
            for q_data in data['questions']:
                question = Question.objects.create(
                    test=test,
                    number=q_data['number'],
                    text=q_data['text'],
                    has_images=bool(q_data.get('images'))
                )
                
                for img_data in q_data.get('images', []):
                    QuestionImage.objects.create(
                        question=question,
                        url=img_data['url'],
                        type=img_data['type']
                    )
                
                for opt_data in q_data['options']:
                    Option.objects.create(
                        question=question,
                        letter=opt_data['letter'],
                        text=opt_data['text'],
                        is_correct=opt_data['is_correct']
                    )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {filename}'))