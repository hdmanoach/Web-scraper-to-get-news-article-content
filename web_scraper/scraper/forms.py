from django import forms
from django.core.exceptions import ValidationError

class NewsArticleForm(forms.Form):
    url = forms.URLField(label="URL de l'article",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'URL de l\'article'}),
        required=True
    )

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("L'URL doit commencer par 'http://' ou 'https://'.")
        return url