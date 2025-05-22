# context_questions/views.py (обновите существующий файл)
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ContextQuestionSet, Question
from app.models import ContextTestResult  # Добавляем импорт
from .serializers import (
    ContextQuestionSetSerializer, 
    ContextQuestionSetWithAnswersSerializer,
    ContextQuestionSetListSerializer
)

class ContextQuestionSetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для наборов контекстных вопросов
    """
    queryset = ContextQuestionSet.objects.all().prefetch_related(
        'context', 'context__images', 'questions', 
        'questions__images', 'questions__options'
    )
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContextQuestionSetListSerializer
        
        # Для администраторов возвращаем сериализатор с ответами
        if self.request.user.is_staff:
            return ContextQuestionSetWithAnswersSerializer
        return ContextQuestionSetSerializer
    
    @action(detail=True, methods=['post'])
    def check_answers(self, request, pk=None):
        """
        Проверить ответы пользователя и сохранить результат
        
        Формат данных:
        {
            "student_name": "Ученик",
            "answers": [
                {"question_id": 1, "selected_options": ["A"]},
                {"question_id": 2, "selected_options": ["B", "C"]}
            ]
        }
        """
        question_set = self.get_object()
        student_name = request.data.get('student_name')
        answers_data = request.data.get('answers', [])
        
        if not student_name:
            return Response({"error": "student_name is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not answers_data:
            return Response({"error": "No answers provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        total_correct = 0
        total_questions = len(answers_data)
        
        for answer in answers_data:
            question_id = answer.get('question_id')
            selected_options = answer.get('selected_options', [])
            
            try:
                question = Question.objects.get(id=question_id, question_set=question_set)
                
                # Проверяем ответ
                is_correct = sorted(selected_options) == sorted(question.correct_answers)
                if is_correct:
                    total_correct += 1
                
                results.append({
                    'question_id': question_id,
                    'is_correct': is_correct,
                    'correct_answers': question.correct_answers if request.user.is_staff else None
                })
                
            except Question.DoesNotExist:
                results.append({
                    'question_id': question_id,
                    'error': 'Question not found'
                })
        
        # Рассчитываем процент правильных ответов
        score_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Сохраняем результат
        test_result = ContextTestResult.objects.create(
            student_name=student_name,
            context_set=question_set,
            score=total_correct,
            total_questions=total_questions,
            percentage=score_percentage
        )
        
        return Response({
            'result_id': test_result.id,
            'student_name': student_name,
            'total_questions': total_questions,
            'correct_answers': total_correct,
            'score_percentage': round(score_percentage, 2),
            'results': results
        })
        
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Получить рейтинг (топ 50) по конкретному контекстному тесту"""
        question_set = self.get_object()
        results = ContextTestResult.objects.filter(context_set=question_set).order_by('-percentage', '-created_at')[:50]
        
        return Response([{
            'id': r.id,
            'student_name': r.student_name, 
            'percentage': r.percentage,
            'created_at': r.created_at
        } for r in results])