from django.shortcuts import render
from django.views import View


class ExampleView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return render(
            request, "ui/custom-example.html", {"message": "This is a custom example"}
        )
