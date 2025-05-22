# context_questions/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField

class ContextQuestionSet(models.Model):
    """Набор контекстных вопросов (один вариант)"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Context(models.Model):
    """Контекст для вопросов"""
    question_set = models.OneToOneField(
        ContextQuestionSet, 
        related_name='context',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Контекст для {self.question_set.title}"

class ContextImage(models.Model):
    """Изображение для контекста"""
    context = models.ForeignKey(
        Context, 
        related_name='images',
        on_delete=models.CASCADE
    )
    url = models.URLField(max_length=500)
    image_type = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Изображение {self.order} для {self.context.question_set.title}"

class Question(models.Model):
    """Вопрос к контексту"""
    question_set = models.ForeignKey(
        ContextQuestionSet, 
        related_name='questions',
        on_delete=models.CASCADE
    )
    number = models.IntegerField()
    text = models.TextField()
    correct_answers = ArrayField(models.CharField(max_length=1))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Вопрос {self.number} из {self.question_set.title}"

class QuestionImage(models.Model):
    """Изображение для вопроса"""
    question = models.ForeignKey(
        Question, 
        related_name='images',
        on_delete=models.CASCADE
    )
    url = models.URLField(max_length=500)
    image_type = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Изображение {self.order} для вопроса {self.question.number}"

class QuestionOption(models.Model):
    """Вариант ответа на вопрос"""
    question = models.ForeignKey(
        Question, 
        related_name='options',
        on_delete=models.CASCADE
    )
    letter = models.CharField(max_length=1)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['letter']

    def __str__(self):
        return f"Вариант {self.letter} для вопроса {self.question.number}"