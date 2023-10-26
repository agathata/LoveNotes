from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.urls import reverse_lazy

# Create your views here.
class MainView(View):
    def get(self, request):
        return render(request, "LoveNotes/home.html", {})