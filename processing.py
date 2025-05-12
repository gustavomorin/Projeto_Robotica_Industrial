import cv2
import turtle
import numpy as np

# Configurações iniciais
image_path = 'img/fotopessoa2.png'  # Substitua pelo caminho da sua imagem
dot_size = 5  # Tamanho dos pontos
gap = 10      # Espaço entre os pontos

# Carregar e processar a imagem
img = cv2.imread(image_path)
img = cv2.resize(img, (100, 100))  # Redimensiona para facilitar o processamento
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte de BGR para RGB

# Configurar a tela do Turtle
screen = turtle.Screen()
screen.setup(width=img.shape[1]*gap, height=img.shape[0]*gap)
screen.bgcolor('white')
screen.title('Arte Pontilhista com Turtle')

# Configurar o Turtle
t = turtle.Turtle()
t.speed(0)
t.penup()
t.hideturtle()

# Desenhar os pontos
start_x = -img.shape[1]*gap/2
start_y = img.shape[0]*gap/2

for y in range(img.shape[0]):
    for x in range(img.shape[1]):
        pixel = img[y][x]
        t.goto(start_x + x*gap, start_y - y*gap)
        t.dot(dot_size, (pixel[0]/255, pixel[1]/255, pixel[2]/255))  # Normaliza as cores para o Turtle

# Manter a janela aberta
turtle.done()
