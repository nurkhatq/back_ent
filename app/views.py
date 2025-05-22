# app/views.py (добавьте к существующим views или создайте файл)
import random
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.models import Count

from context_questions.models import ContextQuestionSet
from .models import Test, Question, Option, TestResult, ContextTestResult
from .serializers import (
    QuestionSerializer, TestListSerializer, TestWithQuestionsSerializer, 
    TestResultSerializer, TestResultListSerializer,
    ContextTestResultSerializer, ContextTestResultListSerializer
)
from app import models

class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тестов"""
    queryset = Test.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestWithQuestionsSerializer
        return TestListSerializer
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Получить рейтинг (топ 50) по конкретному тесту"""
        test = self.get_object()
        results = TestResult.objects.filter(test=test).order_by('-percentage', '-created_at')[:50]
        serializer = TestResultListSerializer(results, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def random_test_leaderboard(self, request):
        """Получить рейтинг (топ 50) для пробного ЕНТ"""
        results = TestResult.objects.filter(is_random_test=True).order_by('-percentage', '-created_at')[:50]
        serializer = TestResultListSerializer(results, many=True)
        return Response(serializer.data)
    
    # Обновленный action в TestViewSet для создания смешанного рандомного теста

    @action(detail=False, methods=['get'])
    def random_test(self, request):
        """
        Создает тест с вопросами в следующей структуре:
        - 1-25: вопросы с одним ответом (из обычных тестов)
        - 26-30: контекстные вопросы (из контекстных тестов)
        - 31-40: вопросы с множественным выбором (из обычных тестов)
        """
        from context_questions.models import Question as ContextQuestion
        
        # Получаем вопросы с одним ответом (1-25)
        single_answer_questions = list(
            Question.objects.filter(
                options__is_correct=True
            ).annotate(
                correct_count=Count('options', filter=Q(options__is_correct=True))
            ).filter(correct_count=1).distinct()
        )
        
        # Получаем вопросы с множественным выбором (31-40)
        multiple_answer_questions = list(
            Question.objects.filter(
                options__is_correct=True
            ).annotate(
                correct_count=Count('options', filter=Q(options__is_correct=True))
            ).filter(correct_count__gt=1).distinct()
        )
        
        # Получаем контекстные вопросы (26-30)
        context_questions = list(ContextQuestion.objects.all().select_related('question_set', 'question_set__context').prefetch_related('options', 'images'))
        
        # Проверяем, достаточно ли вопросов
        if len(single_answer_questions) < 25:
            return Response({"error": f"Недостаточно вопросов с одним ответом. Найдено: {len(single_answer_questions)}"}, status=400)
            
        if len(multiple_answer_questions) < 10:
            return Response({"error": f"Недостаточно вопросов с множественным выбором. Найдено: {len(multiple_answer_questions)}"}, status=400)
            
        if len(context_questions) < 5:
            return Response({"error": f"Недостаточно контекстных вопросов. Найдено: {len(context_questions)}"}, status=400)
        context_sets = list(ContextQuestionSet.objects.all().prefetch_related('questions', 'context', 'questions__options', 'questions__images'))
        # Выбираем случайные вопросы из каждой категории
        selected_single = random.sample(single_answer_questions, 25)
        selected_multiple = random.sample(multiple_answer_questions, 10)
        selected_context_set = random.choice(context_sets)
        selected_context = list(selected_context_set.questions.all())
        
        # Сериализуем обычные вопросы
        single_serialized = QuestionSerializer(selected_single, many=True).data
        multiple_serialized = QuestionSerializer(selected_multiple, many=True).data
        
        # Сериализуем контекстные вопросы (требуется адаптация)
        from context_questions.serializers import QuestionSerializer as ContextQuestionSerializer
        context_serialized = []
        
        for question in selected_context:
            # Получаем контекст
            context = question.question_set.context
            context_data = {
                "text": context.text,
                "images": []  # Здесь можно добавить обработку изображений контекста
            }
            
            # Сериализуем вопрос
            question_data = ContextQuestionSerializer(question).data
            # Добавляем контекст к вопросу
            question_data["context"] = context_data
            # Добавляем флаг, что это контекстный вопрос
            question_data["is_context_question"] = True
            
            context_serialized.append(question_data)
        
        # Объединяем все вопросы в правильном порядке
        all_questions = single_serialized + context_serialized + multiple_serialized
        
        # Возвращаем результат
        return Response({
            "id": 9999,  # Специальный ID для случайного теста
            "title": "Пробный ЕНТ (Смешанный тест)",
            "description": "Тест содержит 25 вопросов с одним ответом, 5 контекстных вопросов и 10 вопросов с множественным выбором",
            "questions": all_questions,
            "multiple_answers_allowed": True,  # Поддерживаем мультивыбор
            "has_images": any(q.get('has_images', False) for q in all_questions),
            "has_context_questions": True
        })

    @action(detail=True, methods=['post'])
    def check_answers(self, request, pk=None):
        """
        Проверить ответы и сохранить результат теста с новой системой оценивания
        """
        test = self.get_object()
        student_name = request.data.get('student_name')
        answers_data = request.data.get('answers', [])
        
        if not student_name:
            return Response({"error": "student_name is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not answers_data:
            return Response({"error": "No answers provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Для случайного теста
        if int(pk) == 9999:
            # Получаем все вопросы из ответов
            questions_ids = [answer.get('question_id') for answer in answers_data]
            
            # Проверяем ответы
            results = []
            total_score = 0
            total_questions = len(answers_data)
            
            for answer in answers_data:
                question_id = answer.get('question_id')
                selected_options = answer.get('selected_options', [])
                is_context_question = answer.get('is_context_question', False)
                
                try:
                    if is_context_question:
                        # Обработка контекстного вопроса
                        from context_questions.models import Question as ContextQuestion
                        question = ContextQuestion.objects.get(id=question_id)
                        
                        # Получаем правильные варианты ответов
                        correct_options = question.correct_answers
                        
                        # Проверяем совпадение (у контекстных вопросов всегда 1 правильный ответ)
                        is_correct = sorted(selected_options) == sorted(correct_options)
                        
                        # За правильный ответ даем 2 балла
                        score = 1 if is_correct else 0
                        
                    else:
                        # Обработка обычного вопроса
                        question = Question.objects.get(id=question_id)
                        
                        # Получаем правильные и неправильные варианты ответов
                        correct_options = list(
                            question.options.filter(is_correct=True).values_list('letter', flat=True)
                        )
                        
                        # Количество правильных ответов у вопроса
                        correct_count = len(correct_options)
                        
                        # Количество выбранных правильных ответов
                        selected_correct = len([opt for opt in selected_options if opt in correct_options])
                        
                        # Количество выбранных неправильных ответов
                        selected_incorrect = len(selected_options) - selected_correct
                        
                        # Расчет баллов по новой системе оценивания
                        score = 0
                        
                        if correct_count == 1:
                            # Вопрос с одним правильным ответом
                            if selected_correct == 1 and selected_incorrect == 0:
                                score = 1  # Выбран один правильный ответ
                            elif selected_correct == 1 and selected_incorrect == 1:
                                score = 1  # Выбран один правильный и один неправильный
                        
                        elif correct_count == 2:
                            # Вопрос с двумя правильными ответами
                            if selected_correct == 2 and selected_incorrect == 0:
                                score = 2  # Выбраны два правильных ответа
                            elif selected_correct == 1 and selected_incorrect <= 1:
                                score = 1  # Выбран один правильный (с/без неправильного)
                            elif selected_correct == 2 and selected_incorrect == 1:
                                score = 1  # Выбраны два правильных и один неправильный
                        
                        elif correct_count == 3:
                            # Вопрос с тремя правильными ответами
                            if selected_correct == 3 and selected_incorrect == 0:
                                score = 2  # Выбраны все три правильных ответа
                            elif selected_correct == 2 and selected_incorrect <= 1:
                                score = 1  # Выбраны два правильных (с/без неправильного)
                    
                    # Добавляем результат проверки
                    results.append({
                        'question_id': question_id,
                        'score': score,
                        'max_score': 2,  # Максимальный балл за вопрос
                        'correct_options': correct_options
                    })
                    
                    # Суммируем баллы
                    total_score += score
                    
                except Exception as e:
                    results.append({
                        'question_id': question_id,
                        'error': str(e)
                    })
            
            # Максимально возможный балл: 40 вопросов * 2 балла = 80
            max_possible_score = 50
            
            # Вычисляем процент
            percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
            
            # Создаем тестовый результат
            test_result = TestResult.objects.create(
                student_name=student_name,
                test=test,
                test_title="Пробный ЕНТ (Смешанный тест)",
                is_random_test=True,
                score=total_score,
                total_questions=total_questions,
                max_score=max_possible_score,
                percentage=percentage
            )
            
            return Response({
                'result_id': test_result.id,
                'student_name': student_name,
                'score': total_score,
                'max_score': max_possible_score,
                'total_questions': total_questions,
                'percentage': percentage,
                'results': results
            })
        
        else:
            # Получаем все вопросы теста
            all_test_questions = Question.objects.filter(test=test)
            total_questions = all_test_questions.count()  # Общее количество вопросов в тесте
            
            # Создаем словарь ответов для быстрого доступа
            answer_map = {answer.get('question_id'): answer.get('selected_options', []) for answer in answers_data}
            
            # Проверяем ответы на все вопросы теста
            results = []
            correct_count = 0
            
            for question in all_test_questions:
                selected_options = answer_map.get(question.id, [])
                
                # Получаем правильные варианты ответов
                correct_options = list(
                    question.options.filter(is_correct=True).values_list('letter', flat=True)
                )
                
                # Проверяем совпадение
                is_correct = sorted(selected_options) == sorted(correct_options)
                if is_correct:
                    correct_count += 1
                
                results.append({
                    'question_id': question.id,
                    'is_correct': is_correct,
                    'correct_options': correct_options
                })
            
            # Вычисляем процент правильных ответов от общего числа вопросов
            percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
            # Создаем тестовый результат
            test_result = TestResult.objects.create(
                student_name=student_name,
                test=test,
                test_title=test.title,
                is_random_test=False,
                score=correct_count,
                total_questions=total_questions,
                percentage=percentage
            )
        
            return Response({
                'result_id': test_result.id,
                'student_name': student_name,
                'score': correct_count,
                'total_questions': total_questions,
                'percentage': percentage,
                'results': results
            })


class TestResultViewSet(mixins.CreateModelMixin, 
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """API для результатов тестов"""
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TestResultListSerializer
        return TestResultSerializer

class ContextTestResultViewSet(mixins.CreateModelMixin, 
                              mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    """API для результатов контекстных тестов"""
    queryset = ContextTestResult.objects.all()
    serializer_class = ContextTestResultSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContextTestResultListSerializer
        return ContextTestResultSerializer