import json
import requests
import os

# Set up authentication credentials
zendesk_url = 'https://panoteam.zendesk.com'
username = os.environ.get('ZD_EMAIL')+'/token'
password = os.environ.get('ZD_TOKEN')
auth = (username, password)
available_locales = ['en-us', 'fr', 'de', 'it', 'ja', 'ko', 'pt', 'ru', 'es']

# Set up the API endpoint to retrieve all articles
articles_endpoint = f'{zendesk_url}/api/v2/help_center/articles.json'
articles_params = {'per_page': 100, 'page': 1}

# Create a session with your API credentials
session = requests.Session()
session.auth = (username, password)

# Make the initial API request to retrieve the first page of articles
response = session.get(articles_endpoint, params=articles_params)
articles = response.json()['articles']

# Loop through each page of results until all articles have been retrieved
while response.json()['next_page'] is not None:
    articles_params['page'] += 1
    response = session.get(articles_endpoint, params=articles_params)
    articles.extend(response.json()['articles'])

# Identify articles that are missing translations in any available language
missing_translations = []
for article in articles:
    # Make the API request to retrieve the translations for the article
    translations_endpoint = f'{zendesk_url}/api/v2/help_center/articles/{article["id"]}/translations.json'
    response = session.get(translations_endpoint)
    translations = response.json()['translations']

    # Check if the article has translations in all available languages
    article_locales = [translation['locale'] for translation in translations]
    if sorted(article_locales) != sorted(available_locales):
        # If the article doesn't have translations in all available languages, add it to the missing_translations list
        missing_translations.append(article['id'])
        print(article['id'])

# Translate articles that are missing translations in any available language
for article_id in missing_translations:
    # Make the API request to retrieve the English version of the article to use as the basis for the translations
    get_url = f'{zendesk_url}/api/v2/help_center/articles/{article_id}/translations/en-us'
    response = requests.get(get_url, auth=auth)
    if response.status_code != 200:
        continue
    article_json = json.loads(response.text)

    # Translate the article to all available languages
    for loc in available_locales:
        print(article_json)
        article_json['translation']['locale'] = loc
        translation_json = json.dumps(article_json)

        # Make the API request to create the translation
        set_url = f'{zendesk_url}/api/v2/help_center/articles/{article_id}/translations'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(set_url, auth=auth, data=translation_json, headers=headers)
        print(response.status_code)

print('Done Translating')