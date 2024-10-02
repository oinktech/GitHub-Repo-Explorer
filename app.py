from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        github_url = request.form.get('github_url')
        try:
            owner, repo = extract_repo_info(github_url)
            return list_files(owner, repo)
        except Exception as e:
            return render_template('error.html', error_message=str(e))
    return render_template('index.html')

def extract_repo_info(url):
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    else:
        raise ValueError("Invalid GitHub URL")

def list_files(owner, repo):
    url = GITHUB_API_URL.format(owner=owner, repo=repo, path="")
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        return render_template('files.html', files=files, owner=owner, repo=repo)
    else:
        return render_template('error.html', error_message=f"Error: {response.status_code}")

@app.route('/file/<owner>/<repo>/<path:filepath>', methods=['GET'])
def show_file(owner, repo, filepath):
    url = GITHUB_API_URL.format(owner=owner, repo=repo, path=filepath)
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_content = response.json().get('content', '').encode('utf-8').decode('utf-8')
        return render_template('file_viewer.html', content=file_content, filename=filepath)
    else:
        return render_template('error.html', error_message=f"Error: {response.status_code}")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
