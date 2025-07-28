import json
import time

import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def start():
    point = 0

    print('В этой игре вам предстоит угадать цену акций российских компаний на следующий день. \n'
          'Чтобы вам было проще, перед каждым раундом будет показан график изменения цены за последний период — это поможет сделать более обоснованное предположение.')

    print('Как это работает?\n'
          'Выбирается акция (например, Сбербанк, Газпром, Яндекс).\n'

          'Вам показывают исторический график её цены.\n'

          'Вы предсказываете, вырастет цена на следующий день или упадёт.\n'

          'После вашего выбора открывается реальный результат, и вы узнаёте, угадали ли вы!\n'

          'Готовы проверить свою интуицию и аналитические навыки? Давайте начнём! 🚀')

    answer = input()
    if answer.lower() == 'да':
        basis(point)


def basis(point):
    with open('tickers.json', encoding='utf-8') as f:
        tiker = json.load(f)

    print('Для начала давайте выберем акцию одной из возможных российских компаний:\n'
          'Сбербанк, Газпром, Лукойл, Роснефть, Новатэк, Магнит, Московская биржа, МТС, Алроса и Ростелеком\n')

    name = input('Введите название компании:')

    if name not in tiker:
        print("Такой компании нет в списке!")
        return basis(point)

    ticker = tiker[name]

    print('Выберите дату начала построения графика')
    year_1 = input('Введите год с 2011 по 2021: ')
    month_1 = input('Введите номер месяца: ')
    day_1 = input('Введите день: ')
    date_1 = f"{year_1}-{month_1.zfill(2)}-{day_1.zfill(2)}"

    print('Выберите дату для предсказывания')
    year_2 = input('Введите год с 2011 по 2021: ')
    month_2 = input('Введите номер месяца: ')
    day_2 = input('Введите день: ')
    date_2 = f"{year_2}-{month_2.zfill(2)}-{day_2.zfill(2)}"

    # Получаем данные для графика
    data = yf.download(ticker, start=date_1, end=date_2)
    time.sleep(5)
    if data.empty:
        print("Нет данных для построения графика!")
        return basis(point)

    # Получаем цены с учетом ближайших дат
    closing_price, actual_prev_date = get_nearest_price(ticker, date_2, 'before')
    unknown_price, actual_next_date = get_nearest_price(ticker, date_2, 'after')

    if closing_price is None or unknown_price is None or actual_prev_date is None or actual_next_date is None:
        print("Не удалось получить данные для выбранных дат!")
        return basis(point)

    # Построение графика
    data['Close'].plot(label=f'{name} - цена закрытия')
    plt.title('Цена акций')
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.legend()
    plt.show()

    print(f'Цена на {actual_prev_date}: {closing_price:.2f}')
    forecast = input('Если вы считаете, что будет рост, введите 1, в ином случае 0: ')

    if forecast == '1' and unknown_price > closing_price:
        print(f'Превосходно! Вы угадали! Цена на {actual_next_date} составила {unknown_price:.2f}')
        point += 10
        print('Вам начислено 10 очков!\n')
    elif forecast == '1' and unknown_price < closing_price:
        print(f'К сожалению, вы ответили неверно. Цена на {actual_next_date} составила {unknown_price:.2f}')
    elif forecast == '0' and unknown_price < closing_price:
        print(f'Превосходно! Вы угадали! Цена на {actual_next_date} составила {unknown_price:.2f}')
        point += 10
        print('Вам начислено 10 очков!')
    else:
        print(f'К сожалению, вы ответили неверно. Цена на {actual_next_date} составила {unknown_price:.2f}')

    print('Суммарное количество очков:', point)
    question = input('Хотите попробовать ещё раз? ')
    if question.lower() == 'да':
        basis(point)
    else:
        print('Спасибо, что были с нами. До скорых встреч!')


def get_nearest_price(ticker, target_date, direction='before'):
    # Функция для получения цены на ближайшую доступную дату
    try:
        # Загружаем данные с запасом в 10 дней
        if direction == 'before':
            start_date = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=10)).strftime('%Y-%m-%d')
            end_date = target_date
        else:
            start_date = target_date
            end_date = (datetime.strptime(target_date, '%Y-%m-%d') + timedelta(days=10)).strftime('%Y-%m-%d')

        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            return None, None

        if direction == 'before':
            # Берем последнюю доступную дату до target_date
            available_dates = data.index[data.index <= pd.to_datetime(target_date)]
            if len(available_dates) == 0:
                return None, None
            nearest_date = available_dates.max()
        else:
            # Берем первую доступную дату после target_date
            available_dates = data.index[data.index >= pd.to_datetime(target_date)]
            if len(available_dates) == 0:
                return None, None
            nearest_date = available_dates.min()

        # Извлекаем конкретное числовое значение цены
        price = float(data.loc[nearest_date, 'Close'])
        return price, nearest_date.strftime('%Y-%m-%d')

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None, None


start()
