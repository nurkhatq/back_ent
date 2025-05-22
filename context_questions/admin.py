# context_questions/admin.py
from django.contrib import admin
from .models import (
    ContextQuestionSet, Context, ContextImage,
    Question, QuestionImage, QuestionOption
)

class ContextImageInline(admin.TabularInline):
    model = ContextImage
    extra = 1

class ContextAdmin(admin.ModelAdmin):
    inlines = [ContextImageInline]
    list_display = ['question_set', 'text_preview']
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    
    text_preview.short_description = 'Текст'

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4

class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline, QuestionImageInline]
    list_display = ['number', 'question_set', 'text_preview']
    list_filter = ['question_set']
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    
    text_preview.short_description = 'Текст'

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5
    show_change_link = True
    fields = ['number', 'text']

class ContextInline(admin.StackedInline):
    model = Context
    show_change_link = True

class ContextQuestionSetAdmin(admin.ModelAdmin):
    inlines = [ContextInline, QuestionInline]
    list_display = ['title', 'description_preview', 'question_count']
    search_fields = ['title', 'description']
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    
    def question_count(self, obj):
        return obj.questions.count()
    
    description_preview.short_description = 'Описание'
    question_count.short_description = 'Количество вопросов'

admin.site.register(ContextQuestionSet, ContextQuestionSetAdmin)
admin.site.register(Context, ContextAdmin)
admin.site.register(Question, QuestionAdmin)