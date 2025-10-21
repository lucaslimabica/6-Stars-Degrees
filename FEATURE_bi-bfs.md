# FEATURE: Bidirectional BFS

## 🧩 Objetivo
Implementar uma busca **Bidirecional** para otimizar a descoberta do menor caminho entre dois atores
no grafo de conexões de filmes (IMDB dataset).

Diferente do BFS simples, que expande a busca apenas a partir da origem, o Bidirectional BFS
mantém **duas buscas simultâneas** (uma a partir do `source` e outra do `target`), encontrando-se no meio.
Isso reduz drasticamente o número de nós explorados em grandes datasets.

---

## ⚙️ Implementação
- Duas filas (`frontier_fwd` e `frontier_bwd`) são usadas.
- Cada frente possui um **mapa de pais** (`parents_fwd`, `parents_bwd`) que registra o caminho percorrido.
- Em cada iteração, é expandida **a menor frente** para equilibrar desempenho.
- Quando um nó é encontrado nas duas frentes, o caminho é reconstruído combinando as duas metades.

---

## 📈 Métricas coletadas
A feature foi instrumentada com contadores e temporização para análise de performance:

| Métrica | Descrição |
|----------|------------|
| `nodes_expanded_fwd` | Nós expandidos pela busca a partir da origem |
| `nodes_expanded_bwd` | Nós expandidos pela busca a partir do destino |
| `edges_considered` | Total de pares (movie_id, person_id) avaliados |
| `time_ms` | Tempo total de execução em milissegundos |

Para ativar as métricas, defina a variável de ambiente:

```bash
METRICS=1 python3 degrees.py large
