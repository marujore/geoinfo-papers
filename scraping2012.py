import csv
import json
import re
import requests
from bs4 import BeautifulSoup

# 1. Lista de dados brutos para o teste com segundos inclusos
dados_brutos = [
    "Repositório de Metadadossid.inpe.br/mtc-m16c/2015/11.26.17.42.49",
    "Repositório de Metadadossid.inpe.br/mtc-m16c/2015/11.26.17.39.41"
]


# Função para extrair apenas o ID limpo
def extrair_id(texto):
    match = re.search(r"(sid\.inpe\.br/mtc-m16c/\d{4}/[\d\.]+)", texto)
    return match.group(1) if match else None


# Filtrando e limpando a lista de testes
lista_de_repositorios = [extrair_id(item) for item in dados_brutos if extrair_id(item)]
todos_os_resultados = []

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

# 2. Execução do Scraping
for repositorio in lista_de_repositorios:
    URL = f"http://mtc-m16c.sid.inpe.br/col/urlib.net/www/2011/03.29.20.55/doc/mirrorget.cgi?languagebutton=en&metadatarepository={repositorio}&choice=full"

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.encoding = "iso-8859-1"
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Erro de conexão no repositório {repositorio}: {e}")
        continue

    # Função flexível para buscar os campos tanto em inglês quanto em português
    def get_field(name_en, name_pt):
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                key = cells[0].get_text(" ", strip=True).lower()
                if name_en.lower() in key or name_pt.lower() in key:
                    return cells[1].get_text(" ", strip=True)
        return ""

    # Captura dos dados básicos
    title = get_field("Title", "Título")
    conference_name = get_field("Conference Name", "Nome do Produtor")
    year = get_field("Year", "Ano")
    language = get_field("Language", "Idioma")
    area = get_field("Area", "Área")
    author_raw_string = get_field("Author", "Autor")
    affiliation_raw_string = get_field("Affiliation", "Afiliação")

    # Se a tabela falhar, busca nas Meta Tags ocultas da página como plano B
    if not title:
        title_tag = soup.find("meta", {"name": "citation_title"}) or soup.find(
            "title"
        )
        title = (
            title_tag["content"]
            if title_tag and title_tag.has_attr("content")
            else (title_tag.text if title_tag else "")
        )
    if not year:
        year_tag = soup.find("meta", {"name": "citation_publication_date"})
        year = year_tag["content"].split("/")[0] if year_tag else ""

    # Padronização do idioma
    lang_map = {"en": "english", "pt": "portuguese", "pt-br": "portuguese"}
    language = lang_map.get(language.lower(), language)

    # Tratamento de Autores (Tabela ou Meta Tags)
    if author_raw_string:
        raw_authors = [
            name.strip()
            for name in re.split(r"\s*\d+\s+", author_raw_string)
            if name.strip()
        ]
        autores_lista = [
            (
                f"{parts[1].strip()} {parts[0].strip()}"
                if len(parts := a.split(",", 1)) == 2
                else a
            )
            for a in raw_authors
        ]
    else:
        meta_authors = soup.find_all("meta", {"name": "citation_author"})
        autores_lista = [
            author["content"]
            for author in meta_authors
            if author.has_attr("content")
        ]


    if affiliation_raw_string:
        raw_affiliations = [
            aff.strip()
            for aff in re.split(r"\s*\d+\s+", affiliation_raw_string)
            if aff.strip()
        ]
        afiliacoes_lista = [
            aff.replace("\ufffd", "–") for aff in raw_affiliations
        ]
    else:
        afiliacoes_lista = []

    # Converte as listas de autores e afiliações em texto corrido separado por " | "
    autores_texto = " | ".join(autores_lista)
    afiliacoes_texto = " | ".join(afiliacoes_lista)

    # Criando o dicionário 
    metadata = {
        "repository_id": repositorio,
        "title": title,
        "conference_name": conference_name,
        "year": year,
        "language": language,
        "Area": area,
        "author": autores_texto,
        "affiliation": afiliacoes_texto,
    }

    todos_os_resultados.append(metadata)

# 3. SALVANDO EM FORMATO .CSV
nome_arquivo_csv = "metadados_inpe2012.csv"

# Definindo as colunas com base nas chaves do dicionário
colunas = [
    "repository_id",
    "title",
    "conference_name",
    "year",
    "language",
    "Area",
    "author",
    "affiliation",
]

try:
    
    with open(
        nome_arquivo_csv, mode="w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=";")
        # Escreve o cabeçalho (nomes das colunas)
        escritor.writeheader()
        # Escreve todas as linhas capturadas
        escritor.writerows(todos_os_resultados)

    print(
        f"\nSucesso! O arquivo '{nome_arquivo_csv}' foi gerado com {len(todos_os_resultados)} registros."
    )
except Exception as e:
    print(f"Erro ao salvar o arquivo CSV: {e}")