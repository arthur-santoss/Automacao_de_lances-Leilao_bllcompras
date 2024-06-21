from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from time import sleep

# URL do site
url_bllcompras = "https://bllcompras.com/"

# Configurações do navegador
options = webdriver.FirefoxOptions()
options.add_argument('-profile')

# Pedir o caminho do perfil do navegador
caminhoPerfilNav = input('Digite o caminho do perfil do navegador: ')
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
        print(f'Erro ao digitar "DISPUTA": {e}')

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
sleep(2)
clicar_elemento('//*[@id="7"]' , 'btn disputa')


# Clicar no botão Lance rápido
clicar_elemento('//*[@id="ButtonFastBid"]', 'Lance rápido')



#pegar valor do "melhor lance atual"
element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/b'))
    )
lanceAtual = element.text.strip()

# Converter para número (float)
lanceAtual = float(lanceAtual.replace(',', '.'))  # Substitui ',' por '.' para o formato numérico

# Exibir o valor obtido como número
print(f'Lance atual encontrado: {lanceAtual}')


#pegar valor do "seu melhor lance"
element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[6]/div/div/div/div[3]/form/div[1]/text/b'))
    )
seuLance = element.text.strip()

# Converter para número (float)
seuLance = float(seuLance.replace(',', '.'))  # Substitui ',' por '.' para o formato numérico

# Exibir o valor obtido como número
print(f'Seu Lance atual encontrado: {seuLance}')

if(seuLance < lanceAtual):
    print('ganhando!')
    #voltar para a tela anterior

elif (seuLance > lanceAtual):
    valorDeLance = lanceAtual - 1
    print(f'Perdendo, vou fazer um novo lance de {valorDeLance}')
    valorDeLanceStr = str(valorDeLance).replace('.', ',')
    print(valorDeLanceStr)
    digitar_elemento('//*[@id="Value"]', valorDeLanceStr )
    clicar_elemento('//*[@id="PerformBidBtn"]', 'Btn efetuar lance')




