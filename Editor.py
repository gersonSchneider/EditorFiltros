import os
import cv2
from tkinter import Tk, Button, filedialog, Label, Canvas, Listbox
from PIL import Image, ImageTk
import numpy as np

# tamanho fixo pra redimensionar a imagem
LARGURA_CANVAS = 800
ALTURA_CANVAS = 600

# editor

def carregar_imagem():
    caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
    if caminho:
        img = cv2.imread(caminho)
        return redimensionar_imagem(img, LARGURA_CANVAS, ALTURA_CANVAS)
    return None

# não tenho webcam pra testar a captura =(

def redimensionar_imagem(img, largura_max, altura_max):
    altura, largura = img.shape[:2]
    proporcao_largura = largura_max / largura
    proporcao_altura = altura_max / altura
    proporcao = min(proporcao_largura, proporcao_altura)
    nova_largura = int(largura * proporcao)
    nova_altura = int(altura * proporcao)
    img_redimensionada = cv2.resize(img, (nova_largura, nova_altura), interpolation=cv2.INTER_AREA)
    return img_redimensionada

# criar a pasta antes vvvvvvv

def salvar_imagem(img, caminho="salvas/imagem_editada.png"):
    if not os.path.exists("salvas"):
        os.makedirs("salvas")                                       # <<<<<<<  lembrou de criar a pasta?
    cv2.imwrite(caminho, img)

# criar a pasta antes ^^^^^^^

def aplicar_filtro(img, filtro):
    if filtro == "Cinza":
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif filtro == "Inverter Cores":
        return cv2.bitwise_not(img)
    elif filtro == "Desfoque":
        return cv2.GaussianBlur(img, (15, 15), 0)
    elif filtro == "Bordas":
        return cv2.Canny(img, 100, 200)
    elif filtro == "Brilho +":
        return cv2.convertScaleAbs(img, alpha=1.2, beta=50)
    elif filtro == "Brilho -":
        return cv2.convertScaleAbs(img, alpha=1.0, beta=-50)
    elif filtro == "Contraste +":
        return cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    elif filtro == "Contraste -":
        return cv2.convertScaleAbs(img, alpha=0.7, beta=0)
    elif filtro == "Sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        return cv2.transform(img, kernel)
    elif filtro == "Espelhado":
        return cv2.flip(img, 1)
    return img

def adicionar_sticker(img, sticker_path, posicao):
    sticker = Image.open(sticker_path).convert("RGBA")
    imagem_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGBA))
    imagem_pil.paste(sticker, posicao, sticker)
    return cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGBA2BGR)

def carregar():
    global imagem
    imagem = carregar_imagem()
    if imagem is not None:
        mostrar_imagem(imagem)

def aplicar_e_mostrar(filtro):
    global imagem
    if imagem is not None:
        imagem_filt = aplicar_filtro(imagem, filtro)
        mostrar_imagem(imagem_filt)

def salvar_arquivo():
    if imagem is not None:
        salvar_imagem(imagem)

def mostrar_imagem(img):
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk

# webcam
def capturar_pela_webcam():
    global imagem
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return

    print("Pressione 's' para salvar uma imagem ou 'q' para sair.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o quadro.")
            break

        cv2.imshow("Webcam - Pressione 's' para salvar ou 'q' para sair", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            frame_redimensionado = redimensionar_imagem(frame, LARGURA_CANVAS, ALTURA_CANVAS)
            imagem = frame_redimensionado
            mostrar_imagem(imagem)
            print("Imagem capturada pela webcam.")
            break
        elif key == ord('q'):
            print("Captura pela webcam cancelada.")
            break

    cap.release()
    cv2.destroyAllWindows()

def carregar_stickers():
    global stickers_disponiveis
    if os.path.exists(PASTA_STICKERS):
        stickers_disponiveis = [os.path.join(PASTA_STICKERS, f) for f in os.listdir(PASTA_STICKERS) if f.endswith(".png")]
        atualizar_lista_stickers()
    else:
        print(f"A pasta '{PASTA_STICKERS}' não foi encontrada!")

def atualizar_lista_stickers():
    listbox_stickers.delete(0, "end")
    for sticker in stickers_disponiveis:
        listbox_stickers.insert("end", os.path.basename(sticker))

def selecionar_sticker(event):
    global sticker_path
    selecao = listbox_stickers.curselection()
    if selecao:
        sticker_path = stickers_disponiveis[selecao[0]]
        print(f"Sticker selecionado: {sticker_path}")

def adicionar_sticker_na_imagem(event):
    global imagem, sticker_path
    if imagem is not None and sticker_path:
        x, y = event.x, event.y
        x -= 50                      # tentei fazer ficar no centro da imagem mas quando dividia por 2 dava erro
        y -= 50                      # :(
        imagem = adicionar_sticker(imagem, sticker_path, (x, y))
        mostrar_imagem(imagem)

def atualizar_lista_filtros():
    filtros = ["Cinza", "Inverter Cores", "Desfoque", "Bordas", "Brilho +", "Brilho -",
               "Contraste +", "Contraste -", "Sepia", "Espelhado"]
    listbox_filtros.delete(0, "end")
    for filtro in filtros:
        listbox_filtros.insert("end", filtro)

def aplicar_filtro_selecionado(event):
    selecao = listbox_filtros.curselection()
    if selecao:
        filtro = listbox_filtros.get(selecao[0])
        aplicar_e_mostrar(filtro)

# janela
# revisar

PASTA_STICKERS = "stickers"
janela = Tk()
janela.title("Editor de Imagens Grau B")
janela.geometry("900x700")

imagem = None
sticker_path = None
stickers_disponiveis = []

canvas = Canvas(janela, width=LARGURA_CANVAS, height=ALTURA_CANVAS, bg="gray")
canvas.pack()
canvas.bind("<Button-1>", adicionar_sticker_na_imagem)

listbox_stickers = Listbox(janela, height=10)
listbox_stickers.pack(side="left", fill="y")
listbox_stickers.bind("<<ListboxSelect>>", selecionar_sticker)

listbox_filtros = Listbox(janela, height=10)
listbox_filtros.pack(side="right", fill="y")
listbox_filtros.bind("<<ListboxSelect>>", aplicar_filtro_selecionado)

btn_carregar = Button(janela, text="Carregar Imagem", command=carregar)
btn_carregar.pack()

btn_carregar_stickers = Button(janela, text="Carregar Stickers", command=carregar_stickers)
btn_carregar_stickers.pack()

btn_capturar_webcam = Button(janela, text="Capturar pela Webcam", command=capturar_pela_webcam)
btn_capturar_webcam.pack()

btn_salvar = Button(janela, text="Salvar Imagem", command=salvar_arquivo)
btn_salvar.pack()

carregar_stickers()
atualizar_lista_filtros()

janela.mainloop()

# lembrar da pasta salvas