# context_questions/management/commands/import_context_questions.py
import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from context_questions.models import (
    ContextQuestionSet, Context, ContextImage,
    Question, QuestionImage, QuestionOption
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import context questions from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            default='context_questions_json',
            help='Directory with JSON files',
        )

    def handle(self, *args, **options):
        json_dir = options['dir']
        
        if not os.path.exists(json_dir):
            self.stderr.write(f"Directory {json_dir} does not exist!")
            return

        for filename in os.listdir(json_dir):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(json_dir, filename)
            self.stdout.write(f"Processing {filename}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                with transaction.atomic():
                    self._import_question_set(data)
                    
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {filename}"))
            except Exception as e:
                self.stderr.write(f"Error processing {filename}: {str(e)}")
                logger.exception(f"Error details for {filename}:")

    def _import_question_set(self, data):
        """Import one context question set"""
        # Create question set
        question_set, created = ContextQuestionSet.objects.update_or_create(
            title=data['title'],
            defaults={
                'description': data.get('description', '')
            }
        )
        
        # Create context
        context_data = data.get('context', {})
        context, _ = Context.objects.update_or_create(
            question_set=question_set,
            defaults={
                'text': context_data.get('text', '')
            }
        )
        
        # Create context images
        context.images.all().delete()  # Remove old images
        for idx, img_data in enumerate(context_data.get('images', [])):
            ContextImage.objects.create(
                context=context,
                url=img_data['url'],
                image_type=img_data.get('type', 'image/png'),
                order=idx
            )
        
        # Create questions
        question_set.questions.all().delete()  # Remove old questions
        for q_data in data.get('questions', []):
            question = Question.objects.create(
                question_set=question_set,
                number=q_data['number'],
                text=q_data['text'],
                correct_answers=q_data.get('correct_answers', [])
            )
            
            # Create question images
            for idx, img_data in enumerate(q_data.get('images', [])):
                QuestionImage.objects.create(
                    question=question,
                    url=img_data['url'],
                    image_type=img_data.get('type', 'image/png'),
                    order=idx
                )
            
            # Create question options
            for opt_data in q_data.get('options', []):
                QuestionOption.objects.create(
                    question=question,
                    letter=opt_data['letter'],
                    text=opt_data['text'],
                    is_correct=opt_data.get('is_correct', False)
                )