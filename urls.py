from django.urls import path
from .views import *
# from django.views.generic import TemplateView

app_name = 'LoveNotes'

urlpatterns = [
    path('', MainView.as_view(), name='home'),
    path('settings', SettingsView.as_view(), name='settings'),
    path('chest/<int:chest_id>', ChestView.as_view(), name='chest-content'),
    path('chest/create', ChestCreate.as_view(), name='create-chest'),
    path('chest/<int:chest_id>/accept', ChestAccept.as_view(), name='accept-chest'),
    path('chest/<int:chest_id>/delete', ChestDelete.as_view(), name='delete-chest'),
    path('picture/<int:chest_id>/create', PictureCreate.as_view(), name='picture-create'),
    path('picture/<int:picture_id>', stream_file, name='picture'),
    path('note/<int:chest_id>/create', NoteCreate.as_view(), name='note-create'),
    path('note/<int:note_id>/update', NoteUpdate.as_view(), name='note-update'),
    path('item/<int:item_id>/delete', ItemDelete.as_view(), name='item-delete'),
]
