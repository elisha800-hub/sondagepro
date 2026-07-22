import csv
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .forms import ChoiceFormSet, QuestionForm, RegisterForm, SurveyForm
from .models import Answer, Choice, Question, Response, Survey


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    surveys = Survey.objects.filter(owner=request.user)
    return render(request, "surveys/dashboard.html", {"surveys": surveys})


@login_required
def create_survey(request):
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.owner = request.user
            survey.save()
            return redirect("add_question", survey_id=survey.id)
    else:
        form = SurveyForm()
    return render(request, "surveys/create_survey.html", {"form": form})


@login_required
def add_question(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, owner=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST, survey=survey)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            if question.type in (Question.SINGLE, Question.MULTIPLE):
                formset = ChoiceFormSet(
                    request.POST, instance=question, prefix="choices"
                )
                if formset.is_valid():
                    formset.save()
                    return redirect("add_question", survey_id=survey.id)
            else:
                return redirect("add_question", survey_id=survey.id)
    else:
        form = QuestionForm(survey=survey)
        formset = ChoiceFormSet(prefix="choices")
    return render(
        request,
        "surveys/add_question.html",
        {"survey": survey, "form": form, "formset": formset, "questions": survey.questions.prefetch_related("choices")},
    )


@login_required
def delete_question(request, survey_id, question_id):
    survey = get_object_or_404(Survey, id=survey_id, owner=request.user)
    question = get_object_or_404(Question, id=question_id, survey=survey)
    question.delete()
    return redirect("add_question", survey_id=survey.id)


@login_required
def toggle_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, owner=request.user)
    survey.is_active = not survey.is_active
    survey.save()
    return redirect("dashboard")


def take_survey(request, token):
    survey = get_object_or_404(Survey, share_token=token)
    if not survey.can_respond():
        return render(request, "surveys/take_survey.html", {"survey": survey, "closed": True})
    if not survey.allow_anonymous and not request.user.is_authenticated:
        return redirect("{}?next={}".format(reverse("login"), request.path))
    questions = list(survey.questions.prefetch_related("choices"))
    if request.method == "POST":
        if not request.session.session_key:
            request.session.save()
        response = Response.objects.create(
            survey=survey,
            respondent=request.user if request.user.is_authenticated else None,
            respondent_email=request.POST.get("respondent_email", ""),
            session_key=request.session.session_key or "",
        )
        answered_values = {}
        for q in questions:
            if q.conditional_on:
                trigger_values = answered_values.get(q.conditional_on_id, [])
                if q.conditional_value not in trigger_values:
                    continue
            answer = _save_answer(response, q, request.POST)
            answered_values[q.id] = answer.value_list() if answer else []
        return redirect("survey_results", token=survey.share_token)
    return render(request, "surveys/take_survey.html", {"survey": survey, "questions": questions})


def _save_answer(response, question, post_data):
    key = f"question_{question.id}"
    if question.type == Question.TEXT:
        text = post_data.get(key, "").strip()
        if text:
            return Answer.objects.create(response=response, question=question, text=text)
        return None
    if question.type == Question.BOOLEAN:
        value = post_data.get(key)
        if value in ("true", "false"):
            return Answer.objects.create(response=response, question=question, text=value)
        return None
    choice_ids = post_data.getlist(key)
    if not choice_ids:
        return None
    choices = Choice.objects.filter(id__in=choice_ids, question=question)
    answer = Answer.objects.create(response=response, question=question)
    answer.selected_choices.set(choices)
    return answer


@login_required
def survey_results(request, token):
    survey = get_object_or_404(Survey, share_token=token)
    if survey.owner != request.user:
        return HttpResponseForbidden("Interdit")
    questions = list(survey.questions.prefetch_related("choices"))
    stats = []
    for q in questions:
        if q.type == Question.TEXT:
            answers = list(
                Answer.objects.filter(question=q)
                .exclude(text="")
                .values_list("text", flat=True)
            )
            stats.append({"question": q, "type": "text", "answers": answers})
        elif q.type == Question.BOOLEAN:
            yes_count = Answer.objects.filter(question=q, text="true").count()
            no_count = Answer.objects.filter(question=q, text="false").count()
            choices = [
                {"text": "Oui", "count": yes_count},
                {"text": "Non", "count": no_count},
            ]
            total = yes_count + no_count
            stats.append({"question": q, "type": q.type, "choices": choices, "total": total})
        else:
            choices = list(
                q.choices.annotate(count=Count("answers")).values("text", "count")
            )
            total = sum(c["count"] for c in choices)
            stats.append({"question": q, "type": q.type, "choices": choices, "total": total})
    responses = survey.responses.prefetch_related(
        "answers__question", "answers__selected_choices"
    )
    return render(
        request,
        "surveys/results.html",
        {"survey": survey, "responses": responses, "stats": stats},
    )


@login_required
def export_csv(request, token):
    survey = get_object_or_404(Survey, share_token=token)
    if survey.owner != request.user:
        return HttpResponseForbidden("Interdit")
    questions = list(survey.questions.all())
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{survey.title}.csv"'
    writer = csv.writer(response)
    header = ["Date", "Répondant"] + [q.text for q in questions]
    writer.writerow(header)
    for r in survey.responses.prefetch_related("answers__selected_choices"):
        row = [
            r.submitted_at.isoformat(),
            r.respondent.username if r.respondent else (r.respondent_email or "Anonyme"),
        ]
        for q in questions:
            try:
                answer = r.answers.get(question=q)
            except Answer.DoesNotExist:
                answer = None
            if answer:
                if q.type == Question.TEXT:
                    row.append(answer.text)
                elif q.type == Question.BOOLEAN:
                    row.append("Oui" if answer.text == "true" else "Non")
                else:
                    row.append(
                        ", ".join(c.text for c in answer.selected_choices.all())
                    )
            else:
                row.append("")
        writer.writerow(row)
    return response


def _answer_display(answer, question_type):
    if not answer:
        return ""
    if question_type == Question.TEXT:
        return answer.text
    if question_type == Question.BOOLEAN:
        return "Oui" if answer.text == "true" else "Non"
    return ", ".join(c.text for c in answer.selected_choices.all())
