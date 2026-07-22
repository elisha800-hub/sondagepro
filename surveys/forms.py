from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Survey, Question, Choice


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ["title", "description", "allow_anonymous", "expires_at"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "allow_anonymous": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "expires_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "allow_anonymous": "Autoriser les réponses sans compte",
            "expires_at": "Date d'expiration",
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "type", "order", "conditional_on", "conditional_value"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "conditional_on": forms.Select(attrs={"class": "form-select"}),
            "conditional_value": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Valeur déclenchante"}
            ),
        }
        labels = {
            "text": "Question",
            "type": "Type",
            "order": "Ordre",
            "conditional_on": "Question conditionnante",
            "conditional_value": "Valeur déclenchante",
        }

    def __init__(self, *args, survey=None, **kwargs):
        super().__init__(*args, **kwargs)
        if survey:
            qs = survey.questions.all()
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            self.fields["conditional_on"].queryset = qs
        else:
            self.fields["conditional_on"].queryset = Question.objects.none()


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "order"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "text": "Choix",
            "order": "Ordre",
        }


ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=3,
    can_delete=False,
)
