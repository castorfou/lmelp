- [Google services🚀](#google-services)
  - [Create a Google project🌟](#create-a-google-project)
  - [Dashboard📊](#dashboard)
  - [API key🔑](#api-key)
  - [Quotas📈](#quotas)

# Google services🚀

To use Gemini or Search, I followed these steps 😎

## Create a Google project🌟

Set it up on [Google Cloud Console](https://console.cloud.google.com) 🖥️.  
My project is named `lmelp` 🔒 (please verify if this info is sensitive).

## Dashboard📊

Check out an [overview](https://console.cloud.google.com/home/dashboard) of your project. 🔍  
I have pinned a few awesome products that might be really useful 💪

![](img/consolegooglecloud-pinnedproducts.png)

## API key🔑

From the dashboard, navigate to generate your API key 🚀:  
Dashboard > APIs & Services > [Credentials](https://console.cloud.google.com/apis/credentials) 👉

![](img/APIs-Credentials-Keys.png)

I configured one with: ✅
- Restricted IP access (my two homes 🏠)
- Restricted API access 🔐
    - Custom Search API 🔍
    - Gemini for Google Cloud API 🌌

Then, I added this key in `.env` to be used by the project under two entries: `GEMINI_API_KEY` and `GOOGLE_CUSTOM_SEARCH_API_KEY` 🔑

## Quotas📈

APIs have quotas and they can be accessed at ℹ️

Dashboard > IAMs & Admin > [Quotas](https://console.cloud.google.com/iam-admin/quotas) ➡️

Or dedicated page per API: 👇

[Custom Search API 🔍](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas)

![](img/customsearchquotas.png)

[Gemini for Google Cloud API 🌌](https://console.cloud.google.com/apis/api/cloudaicompanion.googleapis.com/quotas)

When **out of quotas** (rateLimitExceeded), service will answer **Error 429** ⚠️:

```log
Erreur lors de la recherche Google: <HttpError 429 when requesting https://customsearch.googleapis.com/customsearch/v1?q=B%C3%A9n%C3%A9dicte+Lacapria&cx=c2af590ab41ca4fac&key=AIzaSyCE59lk7YhoSSL7T4vDRAPMv7yhYfWZTHg&alt=json returned "Quota exceeded for quota metric 'Queries' and limit 'Queries per day' of service 'customsearch.googleapis.com' for consumer 'project_number:my_project_number'.". Details: "[{'message': "Quota exceeded for quota metric 'Queries' and limit 'Queries per day' of service 'customsearch.googleapis.com' for consumer 'project_number:my_project_number'.", 'domain': 'global', 'reason': 'rateLimitExceeded'}]">
```

Will find a way to properly handle this case. 👍
