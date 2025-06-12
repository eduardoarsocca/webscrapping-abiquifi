# Script para coletar dados de expositores da Bio Convention 2025
#Contabilizar o tempo de execução do processo
#imporando bibliotecas necessárias
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Início da contagem do tempo de execução
start_time = time.time()
hora_atual = time.strftime("%H:%M:%S", time.localtime(start_time))
#imprimindo o horário de inicio.
print(f"Horário de início: {hora_atual}")

# Script para coletar dados de expositores da Bio Convention 2025
# URL base sem o número da página
base_url = 'https://convention.bio.org/exhibitors?&page='
sufixo_url = "&categories=cb0aaf0e-4c13-11ee-bff906bd0f937899&categories=cb0abaa8-4c13-11ee-bff906bd0f937899&searchgroup=7CFEA488-exhibitors"
url_investors = 'https://convention.bio.org/partner/participating-investors?&prefilter_categories=9747CF69-9348-54A3-2C499E78B5F11EE0%2C974AC15B-E1C3-EEA8-72E5401DD2A0BD8B%2C974CAAF6-CBA0-1F69-DE7D70DBDC145459%2C975341BD-E00B-1D87-6C87ECCD48B5A1CE%2CFDBA78AD-F91A-27E3-E88F4CD949438B2E%2Ccb0ab42b-4c13-11ee-bff906bd0f937899%2Ccb0ab647-4c13-11ee-bff906bd0f937899%2C9768741E-CED1-2D63-13571AA9E794804F%2C976AF051-DBAC-DE98-16BDA38F9820AC80%2CB3FB84A9-ADC2-C2CE-839A844E1CD1BED5%2C976D9E41-994C-48D0-516CC679053A8A79&page='
sufixo_investors = '&searchgroup=0D1C8829-exhibitors'
# Lista para armazenar os dados de todas as páginas
all_data = []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def slugify_exhibitor_name(raw_title: str) -> str:
    """
    1) Remove colchetes (se houver);
    2) Corta a string antes de ' - ' (se existir);
    3) Substitui espaços por traço;
    4) Remove tudo que não for letra, dígito ou traço;
    5) Converte para minúsculas.
    """
    # 1) Remove colchetes
    nome = re.sub(r"[\[\]]", "", raw_title).strip()
    # 2) Corta antes de " - "
    if " - " in nome:
        nome = nome.split(" - ")[0].strip()
    # 3) Substitui qualquer sequência de espaços por um único traço
    nome_com_traco = re.sub(r"\s+", "-", nome)
    # 4) Remove caracteres que não sejam letras, dígitos ou traço
    slug = re.sub(r"[^a-zA-Z0-9\-]+", "", nome_com_traco)
    # 5) Converte para minúsculas
    return slug.lower()

def fetch_website_from_detail(slug: str, numeric_id: str) -> str | None:
    """
    Tenta primeiro acessar via slug; se der erro ou não encontrar, tenta usar o numeric_id.
    Retorna o href encontrado em
      div.m-exhibitor-entry__item__body__contacts__additional__website a
    ou None se não encontrar.
    """
    # 1) Tenta com slug (texto amigável)
    if slug:
        detail_url_slug = f"https://convention.bio.org/exhibitors/{slug}"
        resp = requests.get(detail_url_slug, headers=HEADERS)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            site_a = soup.select_one(
                "div.m-exhibitor-entry__item__body__contacts__additional__website a"
            )
            if site_a and site_a.get("href"):
                return site_a.get("href").strip()

    # 2) Se não encontrou por slug ou retornou 404, tenta com numeric_id
    if numeric_id:
        detail_url_id = f"https://convention.bio.org/exhibitors/{numeric_id}"
        resp = requests.get(detail_url_id, headers=HEADERS)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            site_a = soup.select_one(
                "div.m-exhibitor-entry__item__body__contacts__additional__website a"
            )
            if site_a and site_a.get("href"):
                return site_a.get("href").strip()

    return None

def fetch_website_description_from_detail(slug: str, numeric_id: str) -> str | None:
    """
    Tenta primeiro acessar via slug; se der erro ou não encontrar, tenta usar o numeric_id.
    Retorna a descrição encontrada em
      "div.m-exhibitor-entry__item__body__description a
    ou None se não encontrar.
    """
    #1) tentar com slug (texto amigável)
    if slug:
        description_url_slug = f"https://convention.bio.org/exhibitors/{slug}"
        resp = requests.get(description_url_slug, headers=HEADERS)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            site_description = soup.select_one(
                "div.m-exhibitor-entry__item__body__description"
            )
            if site_description and site_description.get_text(strip=True):
                return site_description.get_text(strip=True)
            
    #2) Se não encontrou por slug ou retornou 404, tenta com numeric_id
    if numeric_id:
        description_url_id = f"https://convention.bio.org/exhibitors/{numeric_id}"
        resp = requests.get(description_url_id, headers=HEADERS)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            site_description = soup.select_one(
                "div.m-exhibitor-entry__item__body__description"
            )
            if site_description and site_description.get_text(strip=True):
                return site_description.get_text(strip=True)
            
    return None
    

# Loop para percorrer as páginas (ajuste o intervalo conforme necessário)
for page in range(1, 5):  # De 1 a 34 (inclusive) 
    '''Executando somente uma página para exemplo. Ao total da url em questão serão 34 páginas (1,35)'''
    # Concatena o número da página na URL
    url = f'{url_investors}{page}{sufixo_investors}'
    print(f'Processando página {page}...')

    # Faz a requisição HTTP
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Garante que a requisição foi bem-sucedida

    # Analisa o HTML com BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra os elementos de cada card
    cards = soup.find_all('li', class_='m-exhibitors-list__items__item')

    # Extrai dados de cada card
    for card in cards:
        # (a) Captura o nome da empresa
        company_name_tag = card.find(
            'a',
            class_='m-exhibitors-list__items__item__header__title__link js-librarylink-entry'
        )
        if not company_name_tag:
            # Fallback: tenta capturar em outro seletor, se necessário
            company_name_tag = card.find('a', {'data-feathr-click-track': 'true'})

        company_name = company_name_tag.get_text(strip=True) if company_name_tag else 'No company name'

        # (b) Captura as categorias
        categories_divs = card.find_all(
            'div',
            class_='m-exhibitors-list__items__item__category'
        )
        categories = ' | '.join([c.get_text(strip=True) for c in categories_divs]) if categories_divs else 'No category'

        # (c) Captura o país
        country_div = card.find('div', class_='m-exhibitors-list__items__item__body__location__text')
        country = country_div.get_text(strip=True) if country_div else 'No country'

        # (d) Captura o data-content-i-d (ID numérico)
        numeric_id = card.get('data-content-i-d', '').strip()

        # (e) Gera slug a partir do nome da empresa (para tentativa de URL amigável)
        slug = slugify_exhibitor_name(company_name)

        # (f) Busca o website na página de detalhe
        website = fetch_website_from_detail(slug, numeric_id) or 'Não encontrado'
        
        #(g) Busca a descrição na página de detalhe
        description = fetch_website_description_from_detail(slug, numeric_id) or 'Não encontrado'

        # Adiciona os dados à lista
        all_data.append({
            'Company Name': company_name,
            'Categories': categories,
            'Country': country,
            'Website': website,
            'Description': description
        })

# Cria um DataFrame com os dados coletados de todas as páginas
df = pd.DataFrame(all_data)

# Salva os resultados em um arquivo Excel
df.to_excel(r'..\webscrapping bioconvention2025\bio_convention_investors.xlsx', index=False)

print("Scraping concluído! Excel gerado em 'bio_convention_investors.xlsx'.")

#interrompendo a contagem de tempo
stop_time = time.time()

#encerrando o tempo de execução
execution_time = stop_time - start_time
#Exibindo o tempo de execução em minutos
print(f"Tempo de execução: {execution_time / 60:.2f} minutos")