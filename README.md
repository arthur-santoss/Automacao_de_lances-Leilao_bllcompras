# Automação de Lances — Leilão BLL Compras

Script em Python (Selenium) para automatizar o acompanhamento e o envio de lances em disputas realizadas na plataforma [BLL Compras](https://bllcompras.com/), monitorando o "melhor lance atual" e o "seu melhor lance" e enviando um novo lance automaticamente quando o usuário estiver perdendo.

> ⚠️ **Aviso importante:** este projeto interage com uma plataforma de compras públicas (pregão eletrônico). O uso de automação em sessões de disputa pode violar os Termos de Uso da BLL Compras e/ou as regras do edital do processo licitatório, podendo resultar em bloqueio da conta, desclassificação da proposta ou outras sanções. Use por sua conta e risco, revise o edital e os termos da plataforma antes de utilizar o script em uma disputa real, e prefira sempre testar em um ambiente controlado.

## Como funciona

O script usa o Selenium para controlar uma instância do Firefox já autenticada (via perfil do navegador), navega até a tela de disputa do processo, e em loop:

1. Lê o valor do **melhor lance atual** (de qualquer participante) na página.
2. Lê o valor do **seu melhor lance**.
3. Se o seu lance for maior (pior) que o lance atual, calcula um novo lance mais baixo e o envia automaticamente.
4. Se o seu lance já for o melhor, apenas informa que está "ganhando" e continua monitorando.

## Estrutura do repositório

Existem três versões do script, com níveis crescentes de recursos:

| Pasta / arquivo | Descrição |
|---|---|
| `main.py` (raiz) | Versão mais simples, sem interface gráfica. Pede o caminho do perfil do navegador no terminal, navega manualmente até a disputa e faz **uma única verificação/lance** (não fica em loop). |
| `somente pelo link/main.py` | Versão com interface gráfica simples (Tkinter), que recebe o **link direto da disputa**, o horário de início e a duração do leilão, calcula o horário de término e reagenda a verificação a cada 20 segundos até faltar pouco tempo para o fim. Também salva o caminho do perfil do navegador em `Documents/automacao.txt` para não precisar digitá-lo novamente. |
| `somente pelo link/tela_perdendo.html` | Página HTML auxiliar (referência de layout/tela usada durante os testes desta versão). |
| `projeto com tela/main.py` | Versão com interface gráfica (Tkinter) mais completa: o usuário informa perfil do navegador, valor de subtração do lance, horário de início e duração do leilão. O script aguarda até faltarem 2 minutos para o fim do leilão e então entra em loop de monitoramento/lance a cada 10 segundos até o horário de término. |

## Pré-requisitos

- Python 3.9+
- [Mozilla Firefox](https://www.mozilla.org/firefox/) instalado
- [geckodriver](https://github.com/mozilla/geckodriver/releases) compatível com a versão do Firefox, disponível no `PATH`
- Um **perfil do Firefox já logado** na plataforma BLL Compras (para que o Selenium reutilize a sessão autenticada)

Dependências Python:

```bash
pip install selenium
```

`tkinter` já acompanha a instalação padrão do Python na maioria dos sistemas (no Linux pode ser necessário instalar `python3-tk` separadamente).

### Como descobrir o caminho do perfil do Firefox

1. Abra o Firefox e acesse `about:profiles`.
2. Localize o perfil que você usa para acessar a BLL Compras (geralmente o "padrão").
3. Copie o valor de **"Pasta local"** — esse é o caminho que o script pede.

## Como usar

### 1. Versão simples (`main.py`)

```bash
python main.py
```

- Informe o caminho do perfil do navegador quando solicitado.
- Navegue manualmente pela interface do BLL Compras até a tela de disputa antes de deixar o script prosseguir (o fluxo de cliques em "processos" → "propostas" → busca por "DISPUTA" é automatizado, mas pressupõe que a estrutura da página não mudou).
- O script faz **uma verificação e, se necessário, um lance**, e depois termina — não fica monitorando continuamente.

### 2. Versão "somente pelo link"

```bash
python "somente pelo link/main.py"
```

- Informe o link direto da página de disputa, o caminho do perfil, o horário de início (`HH:MM`) e a duração do leilão em minutos.
- A interface gráfica mostra um log com os eventos e o tempo restante até o término.
- **Atenção:** nesta versão o clique no botão de efetuar lance (`PerformBidBtn`) está comentado no código (modo de teste/simulação) — o script imprime "Aqui eu iria clicar no Btn efetuar lance" mas não envia o lance de fato. Remova o comentário na linha correspondente quando quiser usá-la em uma disputa real.

### 3. Versão com tela completa (`projeto com tela/main.py`)

```bash
python "projeto com tela/main.py"
```

- Preencha os campos: caminho do perfil, valor de subtração do lance (quanto abaixo do lance atual seu novo lance deve ficar), horário de início e duração do leilão.
- O script aguarda até faltarem 2 minutos para o término e então monitora/dá lances automaticamente a cada 10 segundos.

## Correção aplicada nesta versão

Foi identificado e corrigido um bug em `projeto com tela/main.py`: a variável `tempo_restante` era calculada **uma única vez**, antes do `while True`, e nunca era atualizada dentro do loop. Isso fazia com que as condições "faltam 2 minutos" e "leilão terminou" nunca refletissem o tempo real durante a execução. Agora `tempo_restante` é recalculado a cada iteração do loop, com base no horário atual.

## Limitações conhecidas

- Os seletores (`XPath`) usados para clicar nos elementos da página são fixos e dependem da estrutura atual do site da BLL Compras. Qualquer mudança no layout do site pode quebrar o script.
- O script assume que os valores de lance são exibidos com vírgula como separador decimal (padrão brasileiro).
- Não há tratamento para captchas, timeouts de sessão ou desconexões durante o leilão — se a sessão expirar, o script pode falhar silenciosamente.
- A versão da raiz (`main.py`) não roda em loop contínuo; para monitoramento até o fim do leilão, use uma das versões com interface gráfica.

## Aviso legal

Este projeto foi criado para fins de estudo/uso pessoal. A automação de disputas em plataformas de compras públicas pode estar sujeita a regras específicas de cada edital e aos Termos de Uso da plataforma. O uso é de responsabilidade exclusiva de quem executa o script.
