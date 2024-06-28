from django.shortcuts import render

# Create your views here.
import requests
from base64 import b64decode

class GithubRepo():
    def fetch_github_repos(username):
        repos_url = f'https://api.github.com/users/{username}/repos'
        repos_response = requests.get(repos_url)
        repos = repos_response.json()

        repo_details = []

        for repo in repos:
            readme_url = f'https://api.github.com/repos/{username}/{repo["name"]}/readme'
            languages_url = f'https://api.github.com/repos/{username}/{repo["name"]}/languages'

            readme_response = requests.get(readme_url)
            readme_description = ''
            if readme_response.ok:
                readme_json = readme_response.json()
                readme_description = b64decode(readme_json['content']).decode('utf-8')

            languages_response = requests.get(languages_url)
            languages = languages_response.json()
            #print(languages)
            total_bytes = sum(languages.values())
            language_percentages = {language: f'{(bytes / total_bytes) * 100:.2f}' for language, bytes in languages.items()}

            repo_details.append({
                'name': repo['name'],
                'description': readme_description or repo.get('description', ''),
                'languages': language_percentages
            })

        return repo_details

    repos = fetch_github_repos('BoraKostem')
    for repo in repos:
        print(repo)