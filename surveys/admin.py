from django.contrib import admin
from .models import Survey, Question, Choice, Response, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class AnswerInline(admin.TabularInline):
    model = Answer.selected_choices.through
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "status", "created_at"]
    list_filter = ["is_active", "allow_anonymous"]
    search_fields = ["title"]
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "survey", "type", "order"]
    list_filter = ["type"]
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["text", "question"]


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ["survey", "respondent", "submitted_at"]
    list_filter = ["survey"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["question", "response", "text"]
