# 6-Stars-Degrees (CS50: Introduction to AI with Python)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]() [![CS50 AI](https://img.shields.io/badge/CS50AI-Project-orange)]() [![Check50 Tests](https://img.shields.io/badge/check50-pass-success)]() [![Style50](https://img.shields.io/badge/style50-100%25-success)]()

## Introdução
Este projeto é feito a partir do enunciado "degrees" do curso *CS50: Introduction to AI with Python*. O objetivo do programa é por em prática a teoria dos 6 Graus de Separação num hambiente cinematográfico. Com uma base de dados de filmes do IMDb, o programa irá traçar uma rota de estrela em estrela da cada filmes até unir os dois atores solicitados.

Por exemplo:
Carrie Fisher e Neil Patrick Harris estão a 3 graus de separação.
1: Carrie Fisher e Harrison Ford estrelaram *Star Wars: Episode VI - Return of the Jedi* (perfeito btw)
2: Harrison Ford e Patton Oswalt estrelaram *The Secret Life of Pets 2*
3: Patton Oswalt e Neil Patrick Harris estrelaram *A Very Harold & Kumar 3D* Christmas

## Requisitos
- ```Python 3.8+ ```

## Estrutura
```bash
| degrees.py
| util.py
| small/
 - movies.csv
 - people.csv
 - stars.csv
| large/
 - movies.csv
 - people.csv
 - stars.csv
```

## Lógica do Código
- Dados carregados de `people.csv`, `movies.csv`, `stars.csv`
- Algoritmo: **BFS**
- Busca pelo menor caminho através dos vizinhos (tuplas de id do filme e id do ator)

## Rodando
```bash
$ cd pasta_do_projeto
$ python3 degrees.py small        # dataset pequeno, pouqíssimos segundos
$ python3 degrees.py large        # dataset grande, quase um minuto mas bem mais completo
```
