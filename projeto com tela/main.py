import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import time

def iniciar_automacao():
    caminhoPerfilNav = perfil_entry.get()
    valor_subtracao = float(lance_entry.get())
    horario_inicio_str = horario_inicio_entry.get()
    duracao_minutos = int(duracao_entry.get())
    
    if not caminhoPerfilNav:
        messagebox.showerror("Erro", "Por favor, insira o caminho do perfil do navegador.")
        return

    if not lance_entry.get():
        messagebox.showerror("Erro", "Por favor, insira o valor de subtração do lance.")
        return
    
    if not horario_inicio_str:
        messagebox.showerror("Erro", "Por favor, insira o horário de início do leilão.")
        return
    
    if duracao_minutos <= 0:
        messagebox.showerror("Erro", "A duração do leilão deve ser maior que zero minutos.")
        return
    
    # Convertendo horário de início para objeto datetime
    horario_inicio = datetime.strptime(horario_inicio_str, "%H:%M")
    
    # Calculando tempo restante até o início do leilão
    agora = datetime.now()
    tempo_restante = horario_inicio - agora
    
    # Esperar até faltar 2 minutos para o fim do leilão
    tempo_espera_segundos = (tempo_restante + timedelta(minutes=duracao_minutos) - timedelta(minutes=2)).total_seconds()
    if tempo_espera_segundos > 0:
        print(f"Aguardando até faltar 2 minutos para o fim do leilão...")
        time.sleep(tempo_espera_segundos)
    else:
        print("Iniciando automação imediatamente.")
    
    # URL do site
    url_bllcompras = "https://bllcompras.com/"
    
    # Configurações do navegador
    options = webdriver.FirefoxOptions()
    options.add_argument('-profile')
    options.add_argument(caminhoPerfilNav)
    
    # Inicializar o driver do Firefox
    driver = webdriver.Firefox(options=options)
    driver.get(url_bllcompras)
    
    def clicar_elemento(xpath, descricao, tempo_espera=10):
        try:
            element = WebDriverWait(driver, tempo_espera).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            print(f'Clicou em {descricao}')
            return element
        except Exception as e:
            print(f'Erro ao clicar em {descricao}: {e}')
            return None
    
    def digitar_elemento(xpath, texto):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.click()
            element.send_keys(texto)
            # element.send_keys(Keys.RETURN)
        except Exception as e:
            print(f'Erro ao digitar "{texto}": {e}')
    
    # Clicar em processos
    clicar_elemento("/html/body/div[1]/nav[1]/div[2]/ul[1]/li[1]", "processos")
    
    # Clicar em Propostas
    clicar_elemento('//*[@id="navbarColor01"]/ul[1]/li[1]/div/a[2]', "propostas")
    
    # Digitar "DISPUTA" e pressionar Enter
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="fkStatus"]'))
        )
        element.click()
        element.send_keys('DISPUTA')
        element.send_keys(Keys.RETURN)
    except Exception as e:
        print(f'Erro ao digitar "DISPUTA": {e}')
    
    # Clicar na lupa de pesquisa
    clicar_elemento('//*[@id="btnProposalSearch"]', "lupa pesquisar")
    
    # Clicar na caixa à direita (disputa)
    clicar_elemento('/html/body/div[2]/div[2]/table/tbody/tr[2]/td/div/div/table/tbody/tr/td[11]', "disputa")
    
    janelas = driver.window_handles
    driver.switch_to.window(janelas[-1])
    
    # Clicar no botão "DISPUTA" dentro da div "scrollmenu"
    clicar_elemento('//*[@id="7"]' , 'btn disputa')
    time.sleep(2)
    clicar_elemento('//*[@id="7"]' , 'btn disputa')
    
    # Clicar no botão Lance rápido
    clicar_elemento('//*[@id="ButtonFastBid"]', 'Lance rápido')
    
    # Loop principal para verificar lance quando faltar 2 minutos para o fim do leilão
    while True:
        # Pegar valor do "melhor lance atual"
        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/b'))
            )
            lanceAtual = float(element.text.strip().replace(',', '.'))  # Converter para float
            print(f'Lance atual encontrado: {lanceAtual}')
        except Exception as e:
            print(f'Erro ao obter lance atual: {e}')
            continue
        
        # Pegar valor do "seu melhor lance"
        try:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/div[1]/text/b'))
            )
            seuLance = float(element.text.strip().replace(',', '.'))  # Converter para float
            print(f'Seu Lance atual encontrado: {seuLance}')
        except Exception as e:
            print(f'Erro ao obter seu lance atual: {e}')
            continue
        
        # Verificar condições de lance quando faltar 2 minutos para o fim do leilão
        if tempo_restante <= timedelta(minutes=2):
            if seuLance < lanceAtual:
                print('Ganhando!')
                # Implemente a lógica para voltar à tela anterior se necessário
            elif seuLance > lanceAtual:
                valorDeLance = lanceAtual - valor_subtracao
                print(f'Perdendo, vou fazer um novo lance de {valorDeLance}')
                valorDeLanceStr = str(valorDeLance).replace('.', ',')
                print(valorDeLanceStr)
                digitar_elemento('//*[@id="Value"]', valorDeLanceStr)
                clicar_elemento('//*[@id="PerformBidBtn"]', 'Btn efetuar lance')
        
        # Verificar se o leilão já terminou
        if tempo_restante <= timedelta(minutes=0):
            print("Leilão terminou.")
            break
        
        # Aguardar antes de verificar novamente
        time.sleep(10)  # Verificar a cada 10 segundos

# Criar a interface gráfica
root = tk.Tk()
root.title("Automação de Navegador")
root.configure(bg="#486d5c")

frame = tk.Frame(root, bg="#486d5c")
frame.pack(pady=20, padx=20, expand=True)

tk.Label(frame, text="Caminho do perfil do navegador:", bg="#486d5c", fg="white").pack(pady=10)
perfil_entry = tk.Entry(frame, width=50)
perfil_entry.pack(pady=5)

tk.Label(frame, text="Valor de subtração do lance:", bg="#486d5c", fg="white").pack(pady=10)
lance_entry = tk.Entry(frame, width=50)
lance_entry.pack(pady=5)

tk.Label(frame, text="Horário de início do leilão (HH:MM):", bg="#486d5c", fg="white").pack(pady=10)
horario_inicio_entry = tk.Entry(frame, width=50)
horario_inicio_entry.pack(pady=5)

tk.Label(frame, text="Duração do leilão (minutos):", bg="#486d5c", fg="white").pack(pady=10)
duracao_entry = tk.Entry(frame, width=50)
duracao_entry.pack(pady=5)

tk.Button(frame, text="Iniciar Automação", command=iniciar_automacao).pack(pady=20)

root.mainloop()
