import os

import requests
from flask import Flask
from tchan import ChannelScraper


TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]
JSON_KEY_FILE = os.environ["JSON_KEY_FILE"]
app = Flask(__name__)

import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# define the Telegram bot
bot = telebot.TeleBot(token_telegram)

# define the Google Sheets credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('/content/insperautomacao-joao-2f50fd8a490f.json', ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive'])

# define the Google Sheets client
client = gspread.authorize(creds)

# define the Google Sheets document URL
doc_url = 'https://docs.google.com/spreadsheets/d/1bmLZIrWU1GG_ikJKRcZNtmmFELcYrBK2dMYqFQIV0Gs/edit#gid=0'

# define the bot command
@bot.message_handler(commands=['classificar'])
def classify(message):
    # open the Google Sheets document
    sheet = client.open_by_url(doc_url).sheet1

    # get the values from the cells and create a pandas DataFrame
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    # Classify the data
    modalidades = df['Modalidade'].value_counts()
    finalidades = df['Finalidade/Objeto/Serviço'].value_counts()
    situacoes = df['Situação'].value_counts()

    dispensa = modalidades.get('Dispensa de Licitacao', 0)
    chamada = modalidades.get('Chamada Publica', 0)
    convite = modalidades.get('Convite', 0)

    andamento = situacoes.get('andamento', 0)
    aberto = situacoes.get('em aberto', 0)
    encerrada = situacoes.get('encerrada', 0)

    # send the response to the user
    response = f"Dispensa de Licitação: {dispensa}\n"
    response += f"Chamada Pública: {chamada}\n"
    response += f"Convite: {convite}\n"
    response += f"-----------------------------------\n"
    response += f"Andamento: {andamento}\n"
    response += f"Em aberto: {aberto}\n"
    response += f"Encerrada: {encerrada}"
    bot.send_message(message.chat.id, response)

# define the bot command
@bot.message_handler(commands=['search'])
def search_data(message):
    # ask for the search query
    bot.send_message(message.chat.id, "Please enter your search query:")
    bot.register_next_step_handler(message, process_search_query)

def process_search_query(message):
    query = message.text.lower()
    # open the Google Sheets document
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1bmLZIrWU1GG_ikJKRcZNtmmFELcYrBK2dMYqFQIV0Gs/edit#gid=0').sheet1

    # get the values from the cells and create a pandas DataFrame
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    # filter the DataFrame based on the search query
    filtered_df = df[df.apply(lambda x: x.astype(str).str.contains(query).any(), axis=1)]

    # send the response to the user
    response = filtered_df.to_string(index=False)
    bot.send_message(message.chat.id, response)

# define the bot command
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Olá, para classificar a sua planilha digite classificar")


# start the bot
bot.polling()
# até aqui tudo deu certo
