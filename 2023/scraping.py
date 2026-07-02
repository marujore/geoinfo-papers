from urllib.robotparser import RobotFileParser

#essa função verifica se o robo está pronto para realizar seu trabalho de checagem e extração dos dados
def check_robots(url):
    """Check if scraping is allowed"""
    rp = RobotFileParser()
    rp.set_url('http://mtc-m16c.sid.inpe.br/robots.txt')
    rp.read()
    return rp.can_fetch('*', url)

if check_robots('http://mtc-m16c.sid.inpe.br/ibi/8JMKD2USPTW34P/4DKC4FB'):
    print("✅ Scraping allowed")
else:
    print("❌ Scraping blocked by robots.txt")

import json
import re
import requests
from bs4 import BeautifulSoup

#aqui chama o endereço do site para que o robo vasculhe o metadado do artigo e extraia as informações solicitadas
urls = [
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.14.35&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.05.59&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.21.29&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.32.02&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.50.45&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.30.08&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.16.42&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.37.32&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.33.56&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.11.10&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.23.28&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.28.31&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.35.23&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.18.54&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.22.35&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.14.25.05&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.45.36&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.26.35&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.21.17&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.26.32&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.44.39&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.54.55&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.41.46&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.46.02&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.30.23&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.53.26&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.08.55&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.20.02&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.35.32&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.04.42&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.06.50&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.01.41&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.32.55&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.32.40&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.36.54&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.15.31&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.23.06&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.12.11&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.27.15&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.59.40&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.40.37&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.34.27&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.07.59&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.13.24&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.14.18&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.15.58.23&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.16.47.52&choice=full&languagebutton=en",
    "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi?metadatarepository=sid.inpe.br/mtc-m16c/2022/12.16.17.29.24&choice=full&languagebutton=en"
]

#cabeçalho de requisição do meu navegador, na aba metadados basta clicar em f12, depois f5 para atualizar as páginas, clicar na primeira linha e pegar os dados do cabeçalho de requisição
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0)"
         "Gecko/20100101" 
         "Firefox/152.0"
    )
}

dados = []

for url in urls:

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    response.raise_for_status()

    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    def get_field(name):
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            key = cells[0].get_text(" ", strip=True)
            if key == name:
                return cells[1].get_text(" ", strip=True)
        return None

    title = get_field("Title")
    abstract = get_field("Abstract")
    article_type = get_field("Tertiary Type")
    language = get_field("Language")
    conference_name = get_field("Conference Name")
    author = get_field("Author")
    affiliations = get_field("Affiliation")

    edition = None
    if conference_name:
        m = re.search(r",\s*(\d+)\s*\(", conference_name)
        if m:
            edition = int(m.group(1))

    metadata = {
        "title": title,
        "abstract": abstract,
        "article_type": article_type,
        "language": language,
        "event_edition": edition,
        "author": author,
        "affiliation": affiliations
    }

    print(metadata)

    if metadata["article_type"] == "Full paper":
        metadata["article_type"] = "full"
    if metadata["article_type"] == "Short paper":
        metadata["article_type"] = "short"
    if metadata["language"] == "en":
        metadata["language"] = "english"
    if metadata["language"] == "pt":
        metadata["language"] = "portuguese"

    raw_authors = re.findall(r'\d+\s+(.*?)(?=\s+\d+\s+|$)', metadata["author"])
    raw_authors = [name.strip() for name in raw_authors]
    # Convert "Last, First" to "First Last"
    formatted_authors = [
        f"{first_name.strip()} {last_name.strip()}" 
        if ',' in author 
        else author
        for author in raw_authors
        for last_name, first_name in [author.split(',', 1)] if ',' in author
    ]
    metadata["author"] = formatted_authors

    raw_affiliations = re.findall(r'\d+\s+(.*?)(?=\s+\d+\s+|$)', metadata["affiliation"])
    raw_affiliations = [aff.strip() for aff in raw_affiliations]
    # Clean up encoding issues (replace \ufffd with –)
    formatted_affiliations = [
        aff.replace('\ufffd', '–').replace('�', '–') 
        for aff in raw_affiliations
    ]

    metadata["affiliation"] = formatted_affiliations
    dados.append(metadata)
    print(json.dumps(metadata, indent=4))

print(f"\nTotal de artigos: {len(dados)}")

import os
#para saber onde o arquivo.csv foi salvo no pc
print(os.getcwd())

import pandas as pd

df = pd.DataFrame(dados)
df.to_csv("artigos.csv", index=False, encoding="utf-8-sig")