from pathlib import Path
import pandas as pd

BASE_DIR = Path(".")

artigos_globais = []
autoria_global = []
pessoas_global = []

# Mapeamentos
pessoa_map = {}          # (nome, instituicao) -> novo id_pessoa
novo_id_pessoa = 1
novo_id_artigo = 1
novo_id_autoria = 1

for edicao in range(1, 26):
    pasta = BASE_DIR / f"edition_{edicao:02d}"

    artigos = pd.read_csv(pasta / "artigos.csv")
    pessoas = pd.read_csv(pasta / "pessoas.csv")
    autoria = pd.read_csv(pasta / "autoria.csv")

    # id antigo -> id novo (artigos)
    mapa_artigos = {}

    for _, art in artigos.iterrows():
        antigo = art["id_artigo"]
        mapa_artigos[antigo] = novo_id_artigo

        art = art.copy()
        art["id_artigo"] = novo_id_artigo

        artigos_globais.append(art)

        novo_id_artigo += 1

    # id antigo -> id novo (pessoas)
    mapa_pessoas = {}

    for _, pessoa in pessoas.iterrows():

        chave = (
            str(pessoa["nome"]).strip(),
            str(pessoa["instituicao"]).strip()
        )

        if chave not in pessoa_map:
            pessoa_map[chave] = novo_id_pessoa

            nova = pessoa.copy()
            nova["id_pessoa"] = novo_id_pessoa

            pessoas_global.append(nova)

            novo_id_pessoa += 1

        mapa_pessoas[pessoa["id_pessoa"]] = pessoa_map[chave]

    # reconstruir autoria
    for _, aut in autoria.iterrows():

        nova = aut.copy()

        nova["id_autoria"] = novo_id_autoria
        nova["id_artigo"] = mapa_artigos[aut["id_artigo"]]
        nova["id_pessoa"] = mapa_pessoas[aut["id_pessoa"]]

        autoria_global.append(nova)

        novo_id_autoria += 1

# DataFrames finais
artigos_df = pd.DataFrame(artigos_globais)
pessoas_df = pd.DataFrame(pessoas_global)
autoria_df = pd.DataFrame(autoria_global)

# Ordenar
artigos_df = artigos_df.sort_values("id_artigo")
pessoas_df = pessoas_df.sort_values("id_pessoa")
autoria_df = autoria_df.sort_values("id_autoria")

# Salvar
Path("all_editions").mkdir(exist_ok=True)
artigos_df.to_csv("all_editions/artigos.csv", index=False)
pessoas_df.to_csv("all_editions/pessoas.csv", index=False)
autoria_df.to_csv("all_editions/autoria.csv", index=False)

print(f"Artigos : {len(artigos_df)}")
print(f"Pessoas : {len(pessoas_df)}")
print(f"Autorias: {len(autoria_df)}")