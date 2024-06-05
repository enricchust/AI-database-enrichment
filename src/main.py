import os
from dotenv import load_dotenv
import openai
import requests
from bs4 import BeautifulSoup
import time
import logging
import streamlit as st
import pandas as pd
import random

# Cargar las variables de entorno
load_dotenv() 
client = openai.OpenAI()
# Configurar la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Definir el modelo a utilizar
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

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.
    :param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                return run
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        time.sleep(sleep_interval)

def ask_gpt4(prompt, assis_id):
    thread = client.beta.threads.create()
    thread_id = thread.id
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assis_id,
        instructions=prompt
    )
    run = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)
    if run:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        last_message = messages.data[0]
        response = last_message.content[0].text.value
        return response
    else:
        return "Error"

def analyze_url(url, row, question, assisId, expected_output):
    url_search = ensure_http(url)
    web_content = get_web_content(url_search)
    if web_content is not None:
        soup = parse_html(web_content)
        full_text = extract_text(soup)
        prompt = f"""From the data of the next row, and the website provided, response to the user question.\n\n
        The row: {row}\n\n The website: {full_text}\n\n{question}\n\n Your response output must be in the form {expected_output}"""
        response = ask_gpt4(prompt, assisId)
        return response
    else:
        return "Error"

def extract_url_from_row(row):
    for item in row:
        if isinstance(item, str) and (item.startswith("http://") or item.startswith("https://") or item.startswith("www.")):
            return item
    return None

def process_file(uploaded_file, question, assisId, expected_output, new_column_name):
    df = pd.read_csv(uploaded_file)
    
    # Crear una lista para almacenar los resultados
    results = []
    
    # Crear barra de progreso
    progress_bar = st.progress(0)
    total_rows = len(df)
    
    # Analizar cada fila del DataFrame
    for index, row in df.iterrows():
        url = extract_url_from_row(row)
        if url:
            result = analyze_url(url, row, question, assisId, expected_output)
            results.append(result)
        else:
            results.append("No URL Found")
        
        # Actualizar la barra de progreso
        progress_bar.progress((index + 1) / total_rows)
    
    # Añadir los resultados al DataFrame original
    df[new_column_name] = results
    
    return df

def main():
    st.title("Web Analyzer")

    question_input = st.text_input("Enter your question:", "Dime la localidad donde se basan y luego hazme un resumen de que hacen las empresas(max 15 palabras)")
    new_column_name = st.text_input("Enter the name of the new column:", "Location,Summary")
    expected_output = st.text_input("Enter the expected output:", "Localidad,Descripción(max 10 palabras)")
    
    uploaded_file = st.file_uploader("Choose a CSV or TXT file", type=["csv", "txt"])

    if uploaded_file and st.button("Analyze File"):
        if question_input:
            assisId = "asst_xZNrnBaC0QctHoXlzhNIvFjs"  # ID del asistente
            result_df = process_file(uploaded_file, question_input, assisId, expected_output, new_column_name)
            st.write(result_df)

            # Descargar resultados como CSV
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name='ecommerce_results.csv',
                mime='text/csv',
            )
        else:
            st.error("Por favor, ingrese una pregunta.")

if __name__ == "__main__":
    main()
