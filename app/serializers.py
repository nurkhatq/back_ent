# app/serializers.py (добавьте к существующим сериализаторам или создайте файл)
from rest_framework import serializers
from .models import QuestionImage, Test, Question, Option, TestResult, ContextTestResult
from context_questions.models import ContextQuestionSet
import random

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'letter', 'text']

class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ['id', 'url', 'type']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'number', 'text', 'options', 'has_images', 'images']

class TestListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = ['id', 'title', 'question_count', 'has_images', 'multiple_answers_allowed']
    
    def get_question_count(self, obj):
        return obj.total_questions

class TestWithQuestionsSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = ['id', 'title', 'questions', 'has_images', 'multiple_answers_allowed']
    
    def get_questions(self, obj):
        # Получаем все вопросы для теста
        all_questions = list(obj.questions.all().prefetch_related('options', 'images'))
        
        # Выбираем до 40 случайных вопросов
        if len(all_questions) > 40:
            random_questions = random.sample(all_questions, 40)
        else:
            random_questions = all_questions
        
        # Сортируем по номеру для последовательного отображения
        random_questions.sort(key=lambda q: q.number)
        
        return QuestionSerializer(random_questions, many=True).data

class TestResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    
    class Meta:
        model = TestResult
        fields = ['id', 'student_name', 'test', 'test_title', 'is_random_test', 'score', 
                 'total_questions', 'percentage', 'created_at']
        read_only_fields = ['percentage']
    
    def create(self, validated_data):
        # Рассчитываем процент правильных ответов
        if validated_data['total_questions'] > 0:
            percentage = (validated_data['score'] / validated_data['total_questions']) * 100
        else:
            percentage = 0
            
        validated_data['percentage'] = round(percentage, 2)
        return super().create(validated_data)

class TestResultListSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(read_only=True)
    
    class Meta:
        model = TestResult
        fields = ['id', 'student_name', 'test_title', 'is_random_test', 'percentage', 'created_at']
        
class ContextTestResultSerializer(serializers.ModelSerializer):
    context_title = serializers.CharField(source='context_set.title', read_only=True)
    
    class Meta:
        model = ContextTestResult
        fields = ['id', 'student_name', 'context_set', 'context_title', 
                 'score', 'total_questions', 'percentage', 'created_at']
        read_only_fields = ['percentage']
    
    def create(self, validated_data):
        # Рассчитываем процент правильных ответов
        if validated_data['total_questions'] > 0:
            percentage = (validated_data['score'] / validated_data['total_questions']) * 100
        else:
            percentage = 0
            
        validated_data['percentage'] = round(percentage, 2)
        return super().create(validated_data)

class ContextTestResultListSerializer(serializers.ModelSerializer):
    context_title = serializers.CharField(source='context_set.title', read_only=True)
    
    class Meta:
        model = ContextTestResult
        fields = ['id', 'student_name', 'context_title', 'percentage', 'created_at']