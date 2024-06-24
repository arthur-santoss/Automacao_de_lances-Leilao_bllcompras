import tkinter as tk
import os
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from time import sleep

def clicar_elemento(driver, xpath, descricao, tempo_espera=10):
    try:
        element = WebDriverWait(driver, tempo_espera).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        print(f'{datetime.now()} - Clicou em {descricao}')
        return element
    except Exception as e:
        print(f'{datetime.now()} - Erro ao clicar em {descricao}: {e}')
        return None

def digitar_elemento(driver, xpath, texto):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        element.clear()  # Limpar campo antes de digitar
        element.send_keys(texto)
        print(f'{datetime.now()} - Digitou o valor do lance: {texto}')
    except Exception as e:
        print(f'{datetime.now()} - Erro ao digitar "DISPUTA": {e}')

def main(url, caminho_perfil_nav, log_text, hora_prevista_termino):
    # Configurações do navegador
    options = webdriver.FirefoxOptions()
    options.add_argument('-profile')
    options.add_argument(caminho_perfil_nav)

    # Inicializar o driver do Firefox
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Clicar no botão "DISPUTA" dentro da div "scrollmenu"
    clicar_elemento(driver, '//*[@id="7"]', 'btn disputa')
    sleep(2)
    clicar_elemento(driver, '//*[@id="7"]', 'btn disputa')

    # Clicar no botão Lance rápido
    clicar_elemento(driver, '//*[@id="ButtonFastBid"]', 'Lance rápido')

    # Pegar valor do "melhor lance atual"
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/b'))
    )
    lanceAtual = element.text.strip()
    lanceAtual = float(lanceAtual.replace(',', '.'))  # Substitui ',' por '.' para o formato numérico
    log_text.insert(tk.END, f'{datetime.now()} - Lance atual encontrado: {lanceAtual}\n')
    log_text.see(tk.END)

    # Pegar valor do "seu melhor lance"
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/div[1]/text/b'))
    )
    seuLance = element.text.strip()
    seuLance = float(seuLance.replace(',', '.'))  # Substitui ',' por '.' para o formato numérico
    log_text.insert(tk.END, f'{datetime.now()} - Seu Lance atual encontrado: {seuLance}\n')
    log_text.see(tk.END)

    if seuLance < lanceAtual:
        print(tk.END, f'{datetime.now()} - Ganhando!\n')
    elif seuLance > lanceAtual:
        valorDeLance = lanceAtual - 1
        log_text.insert(tk.END, f'{datetime.now()} - Perdendo, vou fazer um novo lance de {valorDeLance}\n')
        valorDeLanceStr = str(valorDeLance).replace('.', ',')
        print(tk.END, f'{datetime.now()} - Novo lance: {valorDeLanceStr}\n')
        digitar_elemento(driver, '//*[@id="Value"]', valorDeLanceStr)
        # Aguardar até que o valor seja digitado antes de clicar no botão
        sleep(2)  # Tempo necessário para garantir que o valor seja digitado corretamente
        clicar_elemento(driver, '//*[@id="PerformBidBtn"]', 'Btn efetuar lance')
    log_text.see(tk.END)

    # Verificar e exibir o tempo restante até o término do leilão a cada 20 segundos
    now = datetime.now()
    remaining_time = hora_prevista_termino - now
    if remaining_time.total_seconds() > 20:
        hours, remainder = divmod(remaining_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        # Formatando a data e hora sem milissegundos
        log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Tempo restante até o término do leilão: {int(hours)} horas, {int(minutes)} minutos e {int(seconds)} segundos\n')
        log_text.see(tk.END)
        # Chamar novamente após 20 segundos
        log_text.after(20000, main, url, caminho_perfil_nav, log_text, hora_prevista_termino)
    else:
        log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Menos de 20 segundos restantes. Efetuando lance...\n')
        log_text.see(tk.END)
        if driver:
            clicar_elemento(driver, '//*[@id="PerformBidBtn"]', 'Btn efetuar lance')
            log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Lance efetuado.\n')
            log_text.see(tk.END)
        else:
            log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Driver não definido. Não foi possível efetuar o lance.\n')
            log_text.see(tk.END)

def calculate_end_time(start_time_str, duration_minutes):
    # Obter a hora de início do leilão
    hora_inicio_leilao = datetime.strptime(start_time_str, "%H:%M").time()

    # Obter a data e hora atual
    now = datetime.now()

    # Combinar a data atual com a hora de início do leilão
    data_hora_inicio_leilao = datetime.combine(now.date(), hora_inicio_leilao)

    # Verificar se a hora de início já passou no dia atual
    if data_hora_inicio_leilao < now:
        # Adicionar um dia se já passou
        data_hora_inicio_leilao += timedelta(days=1)

    # Calcular a hora de término do leilão
    hora_termino_leilao = data_hora_inicio_leilao + timedelta(minutes=duration_minutes)

    # Se a hora de término for após 24 horas, ajustar para o mesmo dia
    if hora_termino_leilao > data_hora_inicio_leilao + timedelta(days=1):
        hora_termino_leilao -= timedelta(days=1)

    # Subtrair 24 horas se necessário
    if hora_termino_leilao > now + timedelta(days=1):
        hora_termino_leilao -= timedelta(days=1)

    return hora_termino_leilao

def verificar_arquivo():
    # Define o caminho do arquivo no diretório de documentos do usuário
    caminho_arquivo = os.path.join(os.path.expanduser("~"), "Documents", "automacao.txt")
    
    # Verifica se o arquivo existe
    if os.path.exists(caminho_arquivo):
        print(f"O arquivo {caminho_arquivo} existe.")
        with open(caminho_arquivo, 'r') as arquivo:
            caminho_perfil_nav = arquivo.readline().strip()
            if caminho_perfil_nav:
                print(f"Caminho do perfil do navegador lido do arquivo: {caminho_perfil_nav}")
                return caminho_perfil_nav
            else:
                print("Nenhum caminho de perfil encontrado no arquivo.")
                return solicitar_caminho_perfil_nav(caminho_arquivo)
    else:
        print(f"O arquivo {caminho_arquivo} não existe. Criando um novo...")
        caminho_perfil_nav = solicitar_caminho_perfil_nav(caminho_arquivo)
        return caminho_perfil_nav

def solicitar_caminho_perfil_nav(caminho_arquivo):
    try:
        # Solicitar caminho do perfil do navegador
        caminho_perfil_nav = simpledialog.askstring("Input", "Digite o caminho do perfil do navegador:")

        # Salvar o caminho no arquivo
        if caminho_perfil_nav:
            with open(caminho_arquivo, 'w') as arquivo:
                arquivo.write(caminho_perfil_nav)
            print(f"Caminho do perfil do navegador salvo em {caminho_arquivo}")
            return caminho_perfil_nav
        else:
            print("Nenhum caminho fornecido. Não foi possível salvar no arquivo.")
            return solicitar_caminho_perfil_nav(caminho_arquivo)
    except Exception as e:
        print(f"Ocorreu um erro ao criar o arquivo: {e}")
        return None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Leilão Automático")
    
    log_text = tk.Text(root, height=20, width=120)
    log_text.pack()

    log_text.insert(tk.END, f'{datetime.now()} - Iniciando script...\n')
    log_text.see(tk.END)

    url_bllcompras = simpledialog.askstring("Input", "Digite o link da página:")
    caminhoPerfilNav = verificar_arquivo()
    hora_inicio_leilao_str = simpledialog.askstring("Input", "Digite a hora de início do leilão (HH:MM):")
    duracao_leilao_str = simpledialog.askstring("Input", "Digite a duração do leilão em minutos:")

    if url_bllcompras and caminhoPerfilNav and hora_inicio_leilao_str and duracao_leilao_str:
        log_text.insert(tk.END, f'{datetime.now()} - Configurações obtidas:\n')
        log_text.insert(tk.END, f'{datetime.now()} - Link da página: {url_bllcompras}\n')
        log_text.insert(tk.END, f'{datetime.now()} - Caminho do perfil do navegador: {caminhoPerfilNav}\n')
        log_text.insert(tk.END, f'{datetime.now()} - Hora de início do leilão: {hora_inicio_leilao_str}\n')
        log_text.insert(tk.END, f'{datetime.now()} - Duração do leilão: {duracao_leilao_str} minutos\n')
        log_text.see(tk.END)

        # Calcular a hora de término do leilão
        hora_termino_leilao = calculate_end_time(hora_inicio_leilao_str, int(duracao_leilao_str))

        # Exibir o tempo restante até o término do leilão
        now = datetime.now()
        remaining_time = hora_termino_leilao - now
        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            # Formatando a data e hora sem milissegundos
            log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Tempo restante até o término do leilão: {int(hours)} horas, {int(minutes)} minutos e {int(seconds)} segundos\n')
            log_text.see(tk.END)
            # Chamar a função principal (main) após 20 segundos se o leilão ainda não começou
            root.after(20000, main, url_bllcompras, caminhoPerfilNav, log_text, hora_termino_leilao)
        else:
            log_text.insert(tk.END, f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Iniciando script imediatamente...\n')
            log_text.see(tk.END)
            main(url_bllcompras, caminhoPerfilNav, log_text, hora_termino_leilao)

    root.mainloop()
