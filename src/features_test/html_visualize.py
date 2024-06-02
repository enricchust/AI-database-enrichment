import os
import openai
import requests
from bs4 import BeautifulSoup
import time
import logging
import streamlit as st
import pandas as pd
import random

model = "gpt-3.5-turbo"

# Lista de diferentes User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def ensure_http(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

def get_web_content(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levantar una excepción para códigos de estado HTTP no exitosos
        return response.text
    except requests.RequestException as e:
        st.error(f"Error al obtener el contenido de la página: {e}")
        return None

def parse_html(html_content):
    if html_content is None:
        raise ValueError("El contenido HTML es None, no se puede analizar.")
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def extract_text(soup):
    texts = soup.stripped_strings
    full_text = ' '.join(texts)
    return full_text




# URL to be analyzed
url = "https://www.grupohastinik.com/"

# Fetch and process the web content
html_content = get_web_content(url)
if html_content:
    parsed_html = parse_html(html_content)
    html_view = extract_text(parsed_html)
    print(html_view)
else:
    print("Error fetching content")
