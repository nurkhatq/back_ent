# context_questions/serializers.py
from rest_framework import serializers
from .models import (
    ContextQuestionSet, Context, ContextImage,
    Question, QuestionImage, QuestionOption
)

class ContextImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextImage
        fields = ['id', 'url', 'image_type', 'order']

class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ['id', 'url', 'image_type', 'order']

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'letter', 'text']
        
class QuestionOptionWithAnswerSerializer(serializers.ModelSerializer):
    """Сериализатор с информацией о правильности ответа (для админов)"""
    class Meta:
        model = QuestionOption
        fields = ['id', 'letter', 'text', 'is_correct']

class ContextSerializer(serializers.ModelSerializer):
    images = ContextImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Context
        fields = ['id', 'text', 'images']

class QuestionSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(many=True, read_only=True)
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'number', 'text', 'images', 'options']

class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Сериализатор с правильными ответами (для админов)"""
    images = QuestionImageSerializer(many=True, read_only=True)
    options = QuestionOptionWithAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'number', 'text', 'images', 'options', 'correct_answers']

class ContextQuestionSetSerializer(serializers.ModelSerializer):
    context = ContextSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ContextQuestionSet
        fields = ['id', 'title', 'description', 'context', 'questions']

class ContextQuestionSetWithAnswersSerializer(serializers.ModelSerializer):
    """Сериализатор с правильными ответами (для админов)"""
    context = ContextSerializer(read_only=True)
    questions = QuestionWithAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = ContextQuestionSet
        fields = ['id', 'title', 'description', 'context', 'questions']

class ContextQuestionSetListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка наборов вопросов (без вопросов)"""
    class Meta:
        model = ContextQuestionSet
        fields = ['id', 'title', 'description']