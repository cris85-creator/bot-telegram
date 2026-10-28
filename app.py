import os
import threading
import time
import requests
from flask import Flask

TELEGRAM_TOKEN = '8933786182:AAH3T3EkFOoQ5wVer77G7G5JE5vONEQ2i3A'
GEMINI_API_KEY = 'AQ.Ab8RN6JY_k2epSLuyJh7moLp3VWa5GV0me3MZaxVew_bRUN9A'

PROMPT_SISTEMA = (
    'Eres el coach de ciclismo de alto rendimiento de un atleta de 41 años, '
    '76 kg, FTP de 302W. Trabajas a turnos rotativos (semana de mañana '
    '06:00-14:00 y semana de tarde 14:00-22:00). Estás especializado en '
    'competición virtual en Zwift (ZRL, WZRL, TTT) y MTB, optimizando '
    'entrenamientos con datos de Wahoo, Strava e Intervals.icu. Tus '
    'respuestas son directas, científicas, basadas en métricas de potencia y '
    'enfocadas en la gestión de la fatiga según sus turnos laborales.'
)

app = Flask(__name__)


@app.route('/')
def home():
  return 'Bot de Telegram activo y funcionando 24/7'


def obtener_respuesta_gemini(mensaje_usuario):
  url = (
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?'
      f'key={GEMINI_API_KEY}'
  )
  payload = {
      'contents': [{
          'parts': [{
              'text': f'{PROMPT_SISTEMA}\n\nAtleta dice: {mensaje_usuario}'
          }]
      }]
  }
  try:
    response = requests.post(url, json=payload)
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']
  except Exception as e:
    return f'⚠️ Error al conectar con Gemini: {str(e)}'


def enviar_telegram(chat_id, texto):
  url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
  payload = {'chat_id': chat_id, 'text': texto}
  requests.post(url, json=payload)


def bot_loop():
  print('🤖 Bot de Telegram autónomo iniciado en segundo plano...')
  offset = 0
  while True:
    try:
      url = (
          f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30'
      )
      response = requests.get(url).json()

      if 'result' in response:
        for update in response['result']:
          offset = update['update_id'] + 1
          if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            texto_usuario = update['message']['text']
            print(f'Mensaje recibido de {chat_id}: {texto_usuario}')
            respuesta_ia = obtener_respuesta_gemini(texto_usuario)
            enviar_telegram(chat_id, respuesta_ia)
    except Exception as e:
      print(f'Error en el bucle del bot: {e}')
      time.sleep(5)


if __name__ == '__main__':
  hilo_bot = threading.Thread(target=bot_loop, daemon=True)
  hilo_bot.start()

  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)
