import csv
import re
from pathlib import Path

import json
from matplotlib.pylab import rint
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_homepage_url_from_display(display_url, headers):
    def check_url(url):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
        
    domains = ['mtc-m16c', 'mtc-m16d', 'mtc-m21b']
    paths_to_try = []
    
    # Estratégia 1: Extrair o caminho ANTES do /goto/ (PRIORIDADE)
    match = re.search(r'displaydoccontent\.cgi/(.+?)/goto/([^?]+)', display_url)
    if match:
        # O caminho antes do /goto/ é o repositório correto
        antes = match.group(1).split('?')[0]
        paths_to_try.append(antes)  # Prioridade máxima
        
        # Também adiciona o caminho depois como fallback
        depois = match.group(2).split('?')[0]
        paths_to_try.append(depois)
    
    # Estratégia 2: Se não encontrou o padrão com /goto/, tenta outros métodos
    if not paths_to_try:
        # Tenta extrair apenas depois do /goto/
        match = re.search(r'/goto/([^?]+)', display_url)
        if match:
            paths_to_try.append(match.group(1))
        
        # Tenta extrair o caminho completo
        match = re.search(r'displaydoccontent\.cgi/(.+?)(?:\?|$)', display_url)
        if match:
            path = match.group(1)
            if '/goto/' in path:
                path = path.split('/goto/')[-1]
            paths_to_try.append(path)
    
    # Remove duplicatas mantendo a ordem
    paths_to_try = list(dict.fromkeys(paths_to_try))
    
    # Tenta cada combinação de domínio e caminho
    for path in paths_to_try:
        for domain in domains:
            url = f"http://{domain}.sid.inpe.br/col/{path}/doc/thisInformationItemHomePage.html"
            
            if check_url(url):
                return url
    
    # print("Original:")
    # print(f"{display_url}")
    # print("Tentativa:")
    # print(f"{url}")
    return None


def obtain_event_articles(edition, event_url, headers):
        articles = []
        response = requests.get(event_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        frame = soup.find('frame', {'name': 'body'})
        if frame and frame.get('src'):
            frame_url = urljoin(event_url, frame['src'])
            frame_response = requests.get(frame_url, headers=headers, timeout=30)
            frame_response.raise_for_status()
            frame_soup = BeautifulSoup(frame_response.content, "html.parser")

            # Encontrar todos os links
            links = frame_soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                texto = link.get_text(strip=True)

                # Pular links "How to cite?" e links curtos
                if texto and len(texto) > 20 and 'cite' not in texto.lower():
                    # Construir URL completa
                    if not href.startswith('http'):
                        url_completa = urljoin(frame_url, href)
                    else:
                        url_completa = href

                    if texto.startswith("http"):
                        continue  # Pular links que começam com "http"
                    articles.append((texto, url_completa))

        return articles

def get_metadata_link(soup_or_html):
    """
    Extrai o link de metadados do documento a partir do HTML.
    
    Args:
        soup_or_html: Pode ser um objeto BeautifulSoup ou uma string HTML
    
    Returns:
        str: URL completa para os metadados, ou None se não encontrado
    """
    # Se for string, cria o BeautifulSoup
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, "html.parser")
    else:
        soup = soup_or_html
    
    # Encontrar o frame header
    header_frame = soup.find('frame', attrs={'name': 'header'})
    
    if not header_frame:
        return None
    
    src_url = header_frame.get('src')
    if not src_url:
        return None
    
    # Extrair o parâmetro metadatarepository
    parsed = urllib.parse.urlparse(src_url)
    params = urllib.parse.parse_qs(parsed.query)
    
    metadatarepo = params.get('metadatarepository', [None])[0]
    
    if not metadatarepo:
        return None
    
    # Construir o link de metadados
    base_url = "http://mtc-m16c.sid.inpe.br/col/sid.inpe.br/mtc-m18@80/2008/03.17.15.17.24/doc/mirrorget.cgi"
    metadata_url = f"{base_url}?metadatarepository={metadatarepo}&choice=full&languagebutton=en"
    
    return metadata_url


def obtain_metadata(soup):
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
    #Deal with Nodata
    metadata["author"] = metadata["author"] or ""
    metadata["affiliation"] = metadata["affiliation"] or ""
    metadata["abstract"] = metadata["abstract"] or ""
    metadata["title"] = metadata["title"] or ""

    if metadata["article_type"] == "Full paper":
        metadata["article_type"] = "full"
    if metadata["article_type"] == "Short paper":
        metadata["article_type"] = "short"
    if metadata["language"] == "en":
        metadata["language"] = "english"
    if metadata["language"] == "pt":
        metadata["language"] = "portuguese"

    # Authors extraction and formatting
    raw_authors = re.findall(r'\d+\s+(.*?)(?=\s+\d+\s+|$)', metadata["author"])
    raw_authors = [name.strip() for name in raw_authors]
    # Convert "Last, First" to "First Last"
    formatted_authors = []

    for author in raw_authors:
        author = author.strip()

        if "," in author:
            last_name, first_name = author.split(",", 1)
            formatted_authors.append(f"{first_name.strip()} {last_name.strip()}")
        else:
            formatted_authors.append(author)
    metadata["author"] = formatted_authors

    affiliations = metadata.get("affiliation") or ""

    raw_affiliations = re.findall(
        r'\d+\s+(.*?)(?=\s+\d+\s+|$)',
        affiliations
    )
    raw_affiliations = [aff.strip() for aff in raw_affiliations]

    # Clean up encoding issues (replace \ufffd with –)
    formatted_affiliations = [
        aff.replace('\ufffd', '–').replace('�', '–')
        for aff in raw_affiliations
    ]

    metadata["affiliation"] = formatted_affiliations

    return metadata


def criar_csvs(artigos_data, outputdir):
    
    # Limpar texto para CSV (remover quebras de linha)
    def limpar_texto(texto):
        if texto is None:
            return ''
        # Substituir quebras de linha por espaços
        texto = texto.replace('\n', ' ').replace('\r', '')
        # Remover aspas duplas
        texto = texto.replace('"', '""')
        return texto
    
    # Mapeamento de IDs
    pessoa_id = 1
    artigo_id = 1
    autoria_id = 1
    
    # Dicionários para mapear pessoas já cadastradas
    pessoas_map = {}  # chave: (nome, instituicao) -> id_pessoa
    pessoas_list = []
    artigos_list = []
    autoria_list = []
    
    for artigo in artigos_data:
        # Extrair dados do artigo
        titulo = limpar_texto(artigo.get('title', ''))
        abstract = limpar_texto(artigo.get('abstract', ''))
        tipo = artigo.get('article_type', '')
        lingua = artigo.get('language', '')
        edicao = artigo.get('event_edition', '')
        
        # Número de páginas - padrão NULL
        n_paginas = None
        
        # Adicionar artigo
        artigos_list.append({
            'id': artigo_id,
            'titulo': titulo,
            'abstract': abstract,
            'n_paginas': n_paginas,
            'tipo_artigo': tipo,
            'lingua': lingua,
            'n_edicao': edicao
        })
        
        # Processar autores e afiliações
        autores = artigo.get('author', [])
        afiliacoes = artigo.get('affiliation', [])
        
        # Se não houver afiliações, usar lista vazia
        if not afiliacoes:
            afiliacoes = [''] * len(autores)
        
        # Garantir que temos o mesmo número de autores e afiliações
        if len(afiliacoes) < len(autores):
            afiliacoes.extend([''] * (len(autores) - len(afiliacoes)))
        
        for idx, (autor, afiliacao) in enumerate(zip(autores, afiliacoes)):
            # Se autor for vazio, pular
            if not autor:
                continue
                
            # Limpar nome do autor
            nome_autor = limpar_texto(autor.strip())
            
            # Se afiliacao estiver vazia, usar valor padrão
            if not afiliacao:
                nome_instituicao = 'Instituição não informada'
            else:
                nome_instituicao = limpar_texto(afiliacao.strip())
            
            # Criar chave única para pessoa (nome + instituicao)
            chave_pessoa = (nome_autor, nome_instituicao)
            
            # Verificar se pessoa já existe
            if chave_pessoa not in pessoas_map:
                pessoas_map[chave_pessoa] = pessoa_id
                pessoas_list.append({
                    'id': pessoa_id,
                    'nome': nome_autor,
                    'instituicao': nome_instituicao
                })
                pessoa_id += 1
            
            id_pessoa = pessoas_map[chave_pessoa]
            
            # Autor correspondente: primeiro autor é TRUE, demais FALSE
            autor_correspondente = (idx == 0)
            
            # Adicionar autoria
            autoria_list.append({
                'id': autoria_id,
                'id_artigo': artigo_id,
                'id_pessoa': id_pessoa,
                'ordem_autoria': idx + 1,
                'autor_correspondente': autor_correspondente
            })
            autoria_id += 1
        
        artigo_id += 1
    
    # Escrever artigos.csv
    with open(outputdir/'artigos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['id_artigo', 'titulo', 'abstract', 'n_paginas', 'tipo_artigo', 'lingua', 'n_edicao'])
        for artigo in artigos_list:
            writer.writerow([
                artigo['id'],
                artigo['titulo'],
                artigo['abstract'],
                artigo['n_paginas'],
                artigo['tipo_artigo'],
                artigo['lingua'],
                artigo['n_edicao']
            ])
    
    # Escrever pessoas.csv
    with open(outputdir/'pessoas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['id_pessoa', 'nome', 'instituicao'])
        for pessoa in pessoas_list:
            writer.writerow([
                pessoa['id'],
                pessoa['nome'],
                pessoa['instituicao']
            ])
    
    # Escrever autoria.csv
    with open(outputdir/'autoria.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['id_autoria', 'id_artigo', 'id_pessoa', 'ordem_autoria', 'autor_correspondente'])
        for autoria in autoria_list:
            writer.writerow([
                autoria['id'],
                autoria['id_artigo'],
                autoria['id_pessoa'],
                autoria['ordem_autoria'],
                str(autoria['autor_correspondente']).upper()
            ])


def main():
    events=[
        (1, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42SUMHS'),
        (2, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3GNSDMB'),
        (3, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3GTDT9P'),
        (4, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3GUSQQ5'),
        (5, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3H5FH2B'),
        (6, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3H8DCF8'),
        (7, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3HD9RLP'),
        (8, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3HGQNHP'),
        (9, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGP8W/3HJQ4N8'),
        (10, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42SUU4E'),
        (11, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T257H'),
        (12, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T25E8'),
        (13, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T25JL'),
        (14, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T25RB'),
        (15, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T2678'),
        (16, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T288P'),
        (17, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T2PKB'),
        (18, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T2QPE'),
        (19, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T2QTS'),
        (20, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/42T2R5B'),
        (21, 'http://mtc-m16c.sid.inpe.br/rep/8JMKD3MGPDW34P/43PRNME'),
        (22, 'http://mtc-m16c.sid.inpe.br/ibi/8JMKD3MGPDW34P/462CM9S'),
        (23, 'http://mtc-m16c.sid.inpe.br/ibi/8JMKD3MGPDW34P/4888LHB'),
        (24, 'http://mtc-m16c.sid.inpe.br/ibi/8JMKD3MGPDW34P/4ADE2M8'),
        (25, 'http://mtc-m16c.sid.inpe.br/ibi/8JMKD2USPTW34P/4DKC4FB')
            ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        )
    }

    for edition, event_url in events:
        print(f"Scraping event edition {edition} from URL: {event_url} ...")
        outputdir = Path(f"edition_{edition:02d}")
        outputdir.mkdir(parents=True, exist_ok=True)
        edition_articles = []
        edition_articles = obtain_event_articles(edition, event_url, headers)

        #TODO Extract metadata of each article

        # print(f"Edition {edition}: {len(edition_articles)} articles found.")

        event_metadata = []
        for article in edition_articles:
            article_url = get_homepage_url_from_display(article[1], headers=headers)
            # print(f"Article URL: {article_url}")
            try:
                response = requests.get(article_url, headers=headers, timeout=30)
                status = response.status_code
                if status != 200:
                    print(f"❌ Edition: {edition} Title: {article[0]}")
            except Exception as e:
                print(f"⚠️ Erro ao obter artigos do evento {edition} Título: {article[0]} (Fazer manualmente)") # URL: {article[1]} {e}
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            article_metadata_url = get_metadata_link(soup)
            # print(f"Article Metadata URL: {article_metadata_url}")

            response = requests.get(article_metadata_url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            metadata = obtain_metadata(soup)
            # print(metadata)
            event_metadata.append(metadata)
        criar_csvs(event_metadata, outputdir)
    print("Acabou")


if __name__ == "__main__":
    main()
