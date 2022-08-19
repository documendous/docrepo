from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import ExampleView

# urlpatterns = []

urlpatterns = [
    path(
        "custom/example/",
        login_required(ExampleView.as_view()),
        name="ui-example-view",
    )
]
