import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

def crawl_website(url, max_pages=20, interval=1):
    crawled_pages = 0
    queue = [url]
    visited = set()
    results = []
    
    while queue and crawled_pages < max_pages:
        current_url = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else 'No title found'
        title_length = 'قصير' if len(title) < 30 else 'طويل' if len(title) > 60 else 'عادي'
        
        results.append({
            'url': current_url,
            'title': title,
            'length': title_length
        })
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                full_url = urljoin(current_url, href)
                if full_url not in visited:
                    queue.append(full_url)
        
        crawled_pages += 1
        time.sleep(interval)
    
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        return redirect(url_for("results", url=url))
    return render_template("index.html")

@app.route("/results")
def results():
    url = request.args.get("url")
    crawled_data = crawl_website(url)
    return render_template("results.html", results=crawled_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
