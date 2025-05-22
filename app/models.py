# models.py
from django.db import models

class Test(models.Model):
    title = models.CharField(max_length=255)
    total_questions = models.IntegerField()
    multiple_answers_allowed = models.BooleanField(default=False)
    has_images = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    number = models.IntegerField()
    text = models.TextField()
    has_images = models.BooleanField(default=False)

class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='images')
    url = models.URLField()
    type = models.CharField(max_length=50)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    letter = models.CharField(max_length=1)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


# apppp

class TestResult(models.Model):
    """Результаты прохождения обычного теста"""
    student_name = models.CharField(max_length=255)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='results', null=True, blank=True)
    test_title = models.CharField(max_length=255, null=True, blank=True)  # Добавьте это поле
    is_random_test = models.BooleanField(default=False)
    score = models.IntegerField()  # Количество правильных ответов
    total_questions = models.IntegerField()  # Общее количество вопросов
    percentage = models.FloatField()  # Процент правильных ответов
    created_at = models.DateTimeField(auto_now_add=True)
    max_score = models.IntegerField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['test', '-percentage']),  # Для быстрой сортировки по рейтингу
        ]
    
    def __str__(self):
        return f"{self.student_name} - {self.test.title if self.test else 'Без теста'} ({self.percentage}%)"

class ContextTestResult(models.Model):
    """Результаты прохождения контекстного теста"""
    student_name = models.CharField(max_length=255)
    context_set = models.ForeignKey('context_questions.ContextQuestionSet', 
                                    on_delete=models.CASCADE, 
                                    related_name='results')
    score = models.IntegerField()  # Количество правильных ответов
    total_questions = models.IntegerField()  # Общее количество вопросов (обычно 5)
    percentage = models.FloatField()  # Процент правильных ответов
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['context_set', '-percentage']),  # Для быстрой сортировки по рейтингу
        ]
    
    def __str__(self):
        return f"{self.student_name} - {self.context_set.title} ({self.percentage}%)"