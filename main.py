import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL base sem o número da página
base_url = 'https://convention.bio.org/exhibitors/participating-companies?&page='
sufixo_url = "&categories=cb0aaf0e-4c13-11ee-bff906bd0f937899&categories=cb0abaa8-4c13-11ee-bff906bd0f937899&searchgroup=7CFEA488-exhibitors"
# Lista para armazenar os dados de todas as páginas
all_data = []

# Loop para percorrer as páginas (ajuste o intervalo conforme necessário)
for page in range(1, 35):  # De 1 a 34 (inclusive)
    # Concatena o número da página na URL
    url = f'{base_url}{page}{sufixo_url}'
    print(f'Processando página {page}...')

    # Faz a requisição HTTP
    response = requests.get(url)
    response.raise_for_status()  # Garante que a requisição foi bem-sucedida

    # Analisa o HTML com BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra os elementos de cada card
    cards = soup.find_all('li', class_='m-exhibitors-list__items__item')

    # Extrai dados de cada card
    for card in cards:
        # Tenta capturar o nome da empresa usando a classe principal
        company_name_tag = card.find('a', class_='m-exhibitors-list__items__item__header__title__link js-librarylink-entry')
        if not company_name_tag:
            # Fallback: tenta capturar usando o atributo `href` ou outros atributos
            company_name_tag = card.find('a', {'href': 'javascript:return false;', 'data-feathr-click-track': 'true'})

        # Captura o nome da empresa
        company_name = company_name_tag.get_text(strip=True) if company_name_tag else 'No company name'

        # Todas as categorias da empresa
        categories_divs = card.find_all('div', class_='m-exhibitors-list__items__item__category')
        categories = ' | '.join([category.get_text(strip=True) for category in categories_divs]) if categories_divs else 'No category'

        # País da empresa
        country_div = card.find('div', class_='m-exhibitors-list__items__item__body__location__text')
        country = country_div.get_text(strip=True) if country_div else 'No country'

        # Depuração: verifica se o card foi processado corretamente
        if not company_name_tag:
            print(f'Card não processado: {card.prettify()}')

        # Adiciona os dados à lista
        all_data.append({'Company Name': company_name, 'Categories': categories, 'Country': country})

# Cria um DataFrame com os dados coletados de todas as páginas
df = pd.DataFrame(all_data)

# Salva os resultados em um arquivo Excel
df.to_excel(r'..\webscrapping bioconvention2025\bio_convention_2025.xlsx', index=False)


# # Exibe os 100 primeiros registros ordenados pelo nome da empresa
# df.sort_values(by='Company Name', ascending=True)
