import datetime
from matplotlib import pyplot as plt
import numpy as np

def draw_graph1(start_period, end_period):
    print(datetime.datetime())
    start_period = date_pickerW.split('-')
    date_start_period = datetime.date(*map(int, start_date))
    end_period = date_pickerB.split('-')
    date_end_period = datetime.date(*map(int, end_date))
    period = date_end_period-date_start_period
    print(period)
    # Creating dataset
    cars = ['Нет дефекта', 'Есть дефект']
    #?можно взять модельку и сделать ещё распределение на классы
    all = Shpon.query.filter(date_time >= date_start_period , date_time <= date_end_period).all()
    print(all)
    data = [100000, 1000]

    # Creating plot
    fig = plt.figure(figsize=(10, 7))
    plt.pie(data, labels=cars,  autopct='%1.1f%%')
    plt.title(f'Распределение дефекта шпона с {start_period} по {end_period}')
    # show plot
    plt.show()


def draw_graph2(start_period = "01.02.24", end_period="08.02.24"):
    # Creating dataset
    cars = ['Определено правильно', 'Ошибся']
    #?можно взять модельку и сделать ещё распределение на классы
    data = [100000, 1000]

    # Creating plot
    fig = plt.figure(figsize=(10, 7))
    plt.pie(data, labels=cars,  autopct='%1.1f%%')
    plt.title(f'Погрешность определения ИИ дефекта у шпона с {start_period} по {end_period}')
    # show plot
    plt.show()


def draw_graph3(start_period = "01.02.24", end_period="08.02.24"):

    x = np.linspace(0, 10, 10)  # 20 точек по оси X
    y = [5,4,3,5,5,5,4,4,4,6]

    # Построение графика точек и соединение их линией
    plt.plot(x, y, marker='o', linestyle='-', color='blue', label='Точки и соединение')

    # Построение средней линии
    y_mean = np.mean(y)  # Среднее значение по Y
    plt.axhline(y_mean, color='red', linestyle='--', label='Среднее значение')

    # Настройка графика
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('График 20 точек с соединением и средней линией')
    plt.legend()
    plt.grid(True)

    # Показ графика
    plt.show()

draw_graph3()
#draw_graph1(start_date, end_date)