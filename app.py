"""Flask application for extracting the readable text of a news article."""

import time
import urllib.robotparser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request


app = Flask(__name__)

RATE_LIMIT_SECONDS = 3
last_request_by_ip: dict[str, float] = {}

HEADERS = {
    "User-Agent": "ClairvoyantBot/1.0 (article extraction; respectful access)",
}


class ScrapingBlockedError(Exception):
    """Raised when a website explicitly refuses automated access."""


def valid_url(value: str) -> bool:
    """Return whether value is an absolute HTTP(S) URL."""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def allowed_by_robots(url: str) -> bool:
    """Respect a site's robots.txt when it is available."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        robots_response = requests.get(robots_url, headers=HEADERS, timeout=5)
    except requests.RequestException:
        # A temporary robots.txt error should not hide a normally accessible page.
        return True

    if robots_response.status_code in {401, 403}:
        return False
    if robots_response.status_code == 404:
        return True
    if not robots_response.ok:
        return True

    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_response.text.splitlines())
    return parser.can_fetch(HEADERS["User-Agent"], url)


def metadata(soup: BeautifulSoup, *names: str) -> str | None:
    """Read the first matching standard metadata value."""
    for name in names:
        tag = soup.find("meta", attrs={"name": name}) or soup.find(
            "meta", attrs={"property": name}
        )
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def scrape_article(url: str) -> dict[str, str | None]:
    """Fetch an article while respecting the website's access rules."""
    if not allowed_by_robots(url):
        raise ScrapingBlockedError(
            "Ce site interdit l'accès automatisé dans son fichier robots.txt."
        )

    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code in {401, 403}:
        raise ScrapingBlockedError(
            "Ce site refuse les requêtes automatisées (accès interdit)."
        )
    if response.status_code == 429:
        raise ScrapingBlockedError(
            "Ce site limite temporairement les requêtes. Réessayez plus tard."
        )
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    title = metadata(soup, "og:title", "twitter:title")
    if not title and soup.title:
        title = soup.title.get_text(strip=True)
    title = title or "Titre introuvable"

    footer = soup.footer
    footer_text = footer.get_text(separator=" ", strip=True) if footer else "Pied de page introuvable"

    for element in soup(["script", "style", "noscript", "svg", "nav", "header", "aside", "form"]):
        element.decompose()
    content_root = soup.find("article") or soup.find("main") or soup.body or soup
    content = content_root.get_text(separator=" ", strip=True)

    if footer_text != "Pied de page introuvable":
        content = content.replace(footer_text, "").strip()

    lower_content = content[:5000].lower()
    if any(marker in lower_content for marker in ("captcha", "access denied", "just a moment")):
        raise ScrapingBlockedError(
            "Le site demande une vérification anti-robot. Utilisez son API ou son flux RSS."
        )

    return {
        "title": title,
        "content": content,
        "footer": footer_text,
        "author": metadata(soup, "author", "article:author"),
        "date": metadata(soup, "article:published_time", "date", "pubdate"),
        "description": metadata(soup, "description", "og:description"),
        "image": metadata(soup, "og:image", "twitter:image"),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    article = None
    error = None
    url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not valid_url(url):
            error = "L'URL doit être une adresse HTTP ou HTTPS valide."
        else:
            try:
                now = time.monotonic()
                client_ip = request.remote_addr or "unknown"
                elapsed = now - last_request_by_ip.get(client_ip, 0)
                if elapsed < RATE_LIMIT_SECONDS:
                    wait = RATE_LIMIT_SECONDS - int(elapsed)
                    raise ScrapingBlockedError(
                        f"Attendez encore {max(wait, 1)} seconde(s) avant une nouvelle requête."
                    )
                last_request_by_ip[client_ip] = now
                article = scrape_article(url)
            except ScrapingBlockedError as exc:
                error = str(exc)
            except requests.RequestException as exc:
                error = f"Impossible de récupérer l'article : {exc}"

    return render_template("champs.html", article=article, error=error, url=url)


if __name__ == "__main__":
    app.run(debug=True)
