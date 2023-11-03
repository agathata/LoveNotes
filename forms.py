from django import forms
from django.contrib.auth import get_user_model
from .models import Settings, Chest, Picture, Note
from django.core.files.uploadedfile import InMemoryUploadedFile
from ads.humanize import naturalsize

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['light_dark_device']
        widgets = {
            'light_dark_device': forms.RadioSelect,
        }

class NewChestForm(forms.ModelForm):
    email = forms.EmailField(
        label='email',
        widget=forms.EmailInput(attrs={'placeholder': "Enter the email linked to your friend's account", 'style': 'width: 400px;'})
    )

    class Meta:
        model = Chest
        fields = ['email']

class PictureForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    content = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = Picture
        fields = ['content']  # Picture is manual

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('content')
        if pic is None:
            self.add_error('content', "Select a photo to upload.")
        elif len(pic) > self.max_upload_limit:
            self.add_error('content', "File must be < "+self.max_upload_limit_text+" bytes.")

    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(PictureForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.content   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.content = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            self.save_m2m()

        return instance

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["text"]
