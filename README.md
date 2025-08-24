# Web-scraper-to-get-news-article-content
Ce projet est un **web scraper** développé en Python permettant d’extraire automatiquement le **contenu d’articles d’actualité** à partir de sources en ligne. Il utilise des bibliothèques comme `requests`, `BeautifulSoup` ou `Newspaper3k` pour récupérer les titres, dates, auteurs et corps des articles.
## ⚙️ Fonctionnalité
- L'utilisateur saisit l'**URL d’un article** dans une barre de recherche.
- En cliquant sur le bouton, le scraper tente de récupérer le contenu de la page.
- Si **aucune restriction** n'est détectée sur le site web, l'article est affiché.
- En cas de restriction (ex : protection contre les bots), un **message d’erreur** est affiché à l'utilisateur.

- ## 🚀 Installation

> Ce projet est une application Django. Voici les étapes pour l’installer et le lancer en local :

### 1. Cloner le dépôt

```bash
git clone https://github.com/hdmanoach/Web-scraper-to-get-news-article-content.git
cd Web-scraper-to-get-news-article-content
```
2.Créer et activer un environnement virtuel
python3 -m venv venv
source venv/bin/activate        # Sur Windows : venv\Scripts\activate

3. Installer les dépendances
pip install -r requirements.txt

4. Lancer le serveur Django
python manage.py runserver


Accède à l'application dans ton navigateur :
http://127.0.0.1:8000/

# Auteur

[Manoach HOSSOU DODO] (https://github.com/hdmanoach)
