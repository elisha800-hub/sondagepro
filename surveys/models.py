import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Survey(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="surveys")
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    allow_anonymous = models.BooleanField(default=True, verbose_name="Réponses anonymes")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'expiration")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"

    def __str__(self):
        return self.title

    @property
    def status(self):
        if not self.is_active:
            return "clos"
        if self.expires_at and self.expires_at < timezone.now():
            return "expiré"
        return "actif"

    def can_respond(self):
        return self.status == "actif"


class Question(models.Model):
    SINGLE = "single"
    MULTIPLE = "multiple"
    TEXT = "text"
    BOOLEAN = "boolean"
    TYPES = [
        (SINGLE, "Choix unique"),
        (MULTIPLE, "Choix multiples"),
        (TEXT, "Texte libre"),
        (BOOLEAN, "Oui / Non"),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(verbose_name="Texte")
    type = models.CharField(max_length=20, choices=TYPES, default=SINGLE, verbose_name="Type")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    conditional_on = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conditional_questions",
        verbose_name="Conditionnée par",
    )
    conditional_value = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Valeur déclenchante",
        help_text="Pour Oui/Non, utilisez 'Oui' ou 'Non'. Pour les choix, le texte exact du choix.",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200, verbose_name="Texte")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Choix"
        verbose_name_plural = "Choix"

    def __str__(self):
        return self.text


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
    )
    respondent_email = models.EmailField(blank=True, verbose_name="Email")
    session_key = models.CharField(max_length=40, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"

    def __str__(self):
        return f"Réponse à {self.survey.title}"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField(blank=True, verbose_name="Texte")
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="answers")

    class Meta:
        unique_together = ["response", "question"]
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"

    def __str__(self):
        if self.question.type == "text":
            return self.text[:80]
        return ", ".join(c.text for c in self.selected_choices.all())

    def value_list(self):
        if self.question.type == "text":
            return [self.text]
        if self.question.type == "boolean":
            return ["Oui" if self.text == "true" else "Non"]
        return [c.text for c in self.selected_choices.all()]
