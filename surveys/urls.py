from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("surveys/new/", views.create_survey, name="create_survey"),
    path("surveys/<int:survey_id>/questions/", views.add_question, name="add_question"),
    path(
        "surveys/<int:survey_id>/questions/<int:question_id>/delete/",
        views.delete_question,
        name="delete_question",
    ),
    path("surveys/<int:survey_id>/toggle/", views.toggle_survey, name="toggle_survey"),
    path("s/<uuid:token>/", views.take_survey, name="take_survey"),
    path("s/<uuid:token>/results/", views.survey_results, name="survey_results"),
    path("s/<uuid:token>/export/", views.export_csv, name="export_csv"),
]
