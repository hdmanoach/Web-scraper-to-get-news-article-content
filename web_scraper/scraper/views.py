from django.shortcuts import render
import requests
from django.http import HttpResponse
from bs4 import BeautifulSoup
from .forms import NewsArticleForm
# Create your views here.

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .forms import NewsArticleForm  # Assure-toi que ce formulaire est bien défini

def scrape_article(request):
    message_title= None
    message_content = None
    message_footer = None
    error = None

    if request.method == 'POST':
        form = NewsArticleForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36'
            }

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                response.encoding = 'utf-8'  # Forcer l'encodage UTF-8

                soup = BeautifulSoup(response.text, 'html.parser')  # Utiliser .text pour respecter l'encodage

                # Extraire le titre et le contenu
                title = soup.title.string.strip() if soup.title and soup.title.string else 'No title found'
                content = soup.get_text(separator=' ', strip=True)
                footer = soup.footer
                if footer:
                    footer_text = footer.get_text(separator=' ', strip=True)
                    content = content.replace(footer_text, '').strip()
        

                message_title = title
                message_content = content
                message_footer = footer_text if footer else 'No footer found'
                #message = f"Title: {message_title}\n\nContent: {message_content[:500]}..."  # Afficher un extrait du contenu
            except requests.RequestException as e:
                error = f"An error occurred while fetching the article: {e}"
        else:
            error = "Please provide a valid URL."
    else:
        form = NewsArticleForm()

    return render(request, 'champs.html', {
        'form': form,
        'message_title': message_title,
        'message_content': message_content,
        'message_footer': message_footer,
        'error': error
    })
