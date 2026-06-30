from pathlib import Path

import pandas as pd
import numpy as np

geoinfo_dir = Path('/home/marujo/Github/Marujore/geoinfo-papers/all_editions')

artigos = pd.read_csv(
    geoinfo_dir / 'artigos.csv',
    quotechar='"',
    quoting=1,
    encoding='utf-8-sig'
)
print(f"Artigos: {len(artigos)} registros")

pessoas = pd.read_csv(
    geoinfo_dir / 'pessoas.csv',
    quotechar='"',
    quoting=1,
    encoding='utf-8-sig'
)
print(f"Pessoas: {len(pessoas)} registros")

autoria = pd.read_csv(
    geoinfo_dir / 'autoria.csv',
    quotechar='"',
    quoting=1,
    encoding='utf-8-sig'
)
print(f"Autoria: {len(autoria)} registros")

#DF Papers
df = artigos.merge(autoria, on='id_artigo')
df = df.merge(pessoas[['id_pessoa', 'nome', 'instituicao']], on='id_pessoa')

df_papers = df.groupby('id_artigo').agg({
    'titulo': 'first',
    'abstract': 'first',
    'tipo_artigo': 'first',
    'lingua': 'first',
    'n_edicao': 'first',
    'nome': list,
    'instituicao': list
}).reset_index()
print(df_papers)