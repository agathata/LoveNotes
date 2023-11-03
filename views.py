from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Settings, Chest, Item, Note, Picture
from .forms import SettingsForm, NewChestForm, PictureForm, NoteForm

def get_notifications(request):
    logname_id = request.user.id
    notifications_list = Chest.objects.filter(user2__id=logname_id, confirmed=False).select_related()
    return notifications_list

# Home
class MainView(LoginRequiredMixin, View):
    def get(self, request):
        logname_id = request.user.id
        condition = Q(Q(user1__id=logname_id) | Q(user2__id=logname_id), confirmed=True)
        ctx = {
            "owned_chest_list": Chest.objects.filter(condition).select_related()
        }
        for chest in ctx["owned_chest_list"]:
            if chest.user1.id == logname_id:
                chest.other_user = chest.user2
            else:
                chest.other_user = chest.user1
        return render(request, "LoveNotes/home.html", ctx)

# Settings
class SettingsView(LoginRequiredMixin, View):
    def get(self, request):
        settings = Settings.objects.get(user=request.user)
        form = SettingsForm(instance=settings)

        return render(request, 'LoveNotes/settings.html', {'form': form})

    def post(self, request):
        settings = Settings.objects.get(user=request.user)
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('LoveNotes:settings')

        return render(request, 'LoveNotes/settings.html', {'form': form})

class SettingsAccountDelete(LoginRequiredMixin, DeleteView):
    pass

# Chest
class ChestView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        logname_id = request.user.id
        chest = Chest.objects.get(id=kwargs["chest_id"])
        if chest.confirmed:
            if chest.user1.id == logname_id or chest.user2.id == logname_id:
                if chest.user1.id == logname_id:
                    other_user = chest.user2
                else:
                    other_user = chest.user1
                item_list = chest.items.all()
                return render(request, "LoveNotes/chest.html", {"chest_id": kwargs["chest_id"], "item_list": item_list, "log_user": request.user, "other_user": other_user})
        return HttpResponseForbidden("You do not have permission to access this page.")


class ChestCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = NewChestForm()

        return render(request, 'LoveNotes/chest-create.html', {'form': form})

    def post(self, request):
        form = NewChestForm(request.POST)
        if form.is_valid():
            # make sure user exists
            user2_email = form.cleaned_data['email']
            User = get_user_model()
            try:
                requested_user2 = User.objects.get(email=user2_email)
            except User.DoesNotExist:
                form.add_error('email', 'This email is not registered to any users.')
            else:
                # make sure chest between these users doesn't already exist
                if Chest.objects.filter(user1=request.user, user2=requested_user2).exists():
                    form.add_error(None, 'A chest or request with these users already exists.')
                if Chest.objects.filter(user1=requested_user2, user2=request.user).exists():
                    form.add_error(None, 'A chest or request with these users already exists.')
                if not form.errors:
                    chest = Chest(user1=request.user, user2=requested_user2, confirmed=False)
                    chest.save()
                    return redirect('LoveNotes:home')
        return render(request, 'LoveNotes/chest-create.html', {'form': form})

class ChestAccept(LoginRequiredMixin, View):
    def post(self, request, chest_id):
        chest = Chest.objects.get(pk=chest_id)
        chest.confirmed = True
        chest.save()

        return redirect('LoveNotes:chest-content', chest_id=chest.id)

class ChestDelete(LoginRequiredMixin, View):
    def post(self, request, chest_id):
        chest = Chest.objects.get(pk=chest_id)
        chest.delete()

        return redirect('LoveNotes:home')

# Items
class PictureCreate(LoginRequiredMixin, CreateView):
    template_name = "LoveNotes/picture-create.html"
    def get_success_url(self):
        return reverse_lazy('LoveNotes:chest-content', kwargs={'chest_id': self.kwargs['chest_id']})

    def get(self, request, **kwargs):
        form = PictureForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        form = PictureForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        add_chest = get_object_or_404(Chest, id=kwargs['chest_id'])
        # Create and save item object, add link to picture then save
        fresh_item = Item(chest=add_chest, uploaded_by=request.user, is_picture=True)
        fresh_item.save()
        picture = form.save(commit=False)
        picture.item = fresh_item
        picture.save()
        form.save_m2m()
        return redirect(self.get_success_url())

def stream_file(request, picture_id):
    pic = get_object_or_404(Picture, item_id=picture_id)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.content)
    response.write(pic.content)
    return response

class NoteCreate(LoginRequiredMixin, CreateView):
    template_name = "LoveNotes/picture-create.html"
    def get_success_url(self):
        return reverse_lazy('LoveNotes:chest-content', kwargs={'chest_id': self.kwargs['chest_id']})

    def get(self, request, **kwargs):
        form = NoteForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, **kwargs):
        form = NoteForm(request.POST)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        add_chest = get_object_or_404(Chest, id=kwargs['chest_id'])
        # Create and save item object, add link to picture then save
        fresh_item = Item(chest=add_chest, uploaded_by=request.user, is_picture=False)
        fresh_item.save()
        note = form.save(commit=False)
        note.item = fresh_item
        note.save()
        return redirect(self.get_success_url())

class NoteUpdate(LoginRequiredMixin, UpdateView):
    model = Note

    def get_success_url(self):
        note = self.get_object()
        return reverse_lazy('LoveNotes:chest-content', kwargs={'chest_id': note.chest_id})

class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item

    def post(self, request, **kwargs):
        item = get_object_or_404(Item, id=kwargs["item_id"])
        chest_id = item.chest.id
        item.delete()

        return redirect(reverse_lazy('LoveNotes:chest-content', kwargs={'chest_id': chest_id}))
