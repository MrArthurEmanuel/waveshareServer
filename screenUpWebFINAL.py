###################################################################	                                                                                            
#Descrição  	: Script para escrever em display WaveShare V3 2.13                                                                                                                                                                                     
#Autor       	: Arthur Emanuel Alves Teixeira                                                
#Email         	: mrarthuremanuel@gmail.com   
#Data           : 24/04/2024                                     

'''
Esse código foi desenvolvido por mim com intuito de me ajudar a desenvolver um projeto futuro de exibir informações 
do Home Assistant (Dependendo da data, talvez esse projeto já tenha acontecido xD).
O código foi desenvolvido para me ajudar a entender como funciona a integração do display e como posso "escrever" 
informações no display, com isso, posso exibir informações de sensores e status de dispositivos inteligentes 
no display através do Raspberry Pi Zero W.
'''   
###################################################################


from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import sys
import time
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os


def display_message(message):
    try:
        # Função para verificar se o texto excede 138 caracteres, caso a verificação do Front-end falhe.
        if len(message) > 138:
            raise ValueError("A mensagem excede o limite de 138 caracteres.")

        # Inicializa o display
        epd = epd2in13_V3.EPD()
        epd.init()

        # Cria uma imagem
        image = Image.new('1', (epd.height, epd.width), 255)  # 255: Branco
        draw = ImageDraw.Draw(image)

        # Carrega a fonte
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)

        # Quebra o texto em linhas de no máximo 24 caracteres
        wrapped_message = textwrap.wrap(message, width=24)

        # Desenha cada linha da mensagem na imagem
        y_position = 1  # Define a posição inicial da linha
        for line in wrapped_message:
            draw.text((2, y_position), line, font=font, fill=0)  # 0: Preto
            y_position += font.getsize(line)[1]  # Incrementa a posição y para a próxima linha

        # Rotaciona a imagem do display em 180 graus. 
        image = image.rotate(180, expand=True)

        # Envia a imagem para o display
        epd.display(epd.getbuffer(image))
        
        print("Mensagem exibida com sucesso no display.")

    except ValueError as ve:
        print("Erro ao exibir a mensagem no display:", ve)
        raise ve

    except Exception as e:
        print("Erro ao exibir a mensagem no display:", e)
        raise e

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        message = data.get('message', [''])[0]
        print("Mensagem recebida:", message)
        try:
            display_message(message)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Message updated successfully.')
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        try:
            print("GET request received for path:", self.path)
            if self.path == '/':
            # Se a solicitação for para a página inicial, envie o arquivo HTML
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    content = f.read()
                    print("Sending HTML content:", content)
                    self.wfile.write(content)
            elif self.path == '/style.css':
            # Se a solicitação for para o arquivo CSS, envie-o
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                with open('style.css', 'rb') as f:
                    self.wfile.write(f.read())

            elif self.path.endswith('.png') or self.path.endswith('.png'):
            # Se a solicitação for para uma imagem PNG, envie-a
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(self.path[1:], 'rb') as f:
                    self.wfile.write(f.read())

            elif self.path.endswith('.svg'):
            # Se a solicitação for para um arquivo SVG, envie-o
                self.send_response(200)
                self.send_header('Content-type', 'image/svg+xml')
                self.end_headers()
                with open(self.path[1:], 'rb') as f:
                    self.wfile.write(f.read())
            else:
            # Se a solicitação for para qualquer outro recurso, retorne um erro 404
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 - Not Found')
        except Exception as e:
        # Lidar com exceções, se ocorrerem
            print("Error handling GET request:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        message = data.get('message', [''])[0]
        print("Mensagem recebida:", message)
        display_message(message)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Message updated successfully.')

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}")
    print("Diretório atual:", os.getcwd())
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_server()
