import csv
import sys
from collections import deque
import os, time
from typing import Dict, List, Tuple, Optional

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                # ignore bad rows
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    # ===== usa Bidirectional BFS por padrão =====
    path = shortest_path_bidirectional(source, target)
    # (se quiser usar a BFS simples: path = shortest_path(source, target))

    if path is None:
        print("Not connected.")
    else:
        degrees_count = len(path)
        print(f"{degrees_count} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees_count):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


# ---------- BFS tradicional (mantido) ----------
def shortest_path(source: str, target: str) -> Optional[List[Tuple[str, str]]]:
    """
    Retorna a menor lista de (movie_id, person_id) que conecta source a target.
    [] se source == target; None se não houver caminho.
    """
    if source == target:
        return []

    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    explored = set()

    while True:
        if frontier.empty():
            return None

        node = frontier.remove()
        explored.add(node.state)

        for movie_id, person_id in neighbors_for_person(node.state):
            if person_id in explored or frontier.contains_state(person_id):
                continue

            child = Node(state=person_id, parent=node, action=movie_id)

            if child.state == target:
                path: List[Tuple[str, str]] = []
                current = child
                while current.parent is not None:
                    path.append((current.action, current.state))
                    current = current.parent
                path.reverse()
                return path

            frontier.add(child)


# ---------- Bidirectional BFS (novo) ----------
ParentMap = Dict[str, Tuple[Optional[str], Optional[str]]]

def shortest_path_bidirectional(source: str, target: str) -> Optional[List[Tuple[str, str]]]:
    """
    Bidirectional BFS com métricas: encontra a menor lista de (movie_id, person_id)
    conectando `source` a `target`. [] se source == target; None se não houver caminho.

    Define METRICS=1 no ambiente para imprimir métricas de performance.
    """
    if source == target:
        if os.getenv("METRICS") == "1":
            print("[metrics] source == target → 0 degrees")
        return []

    t0 = time.perf_counter()
    frontier_fwd = deque([source])
    frontier_bwd = deque([target])
    parents_fwd: ParentMap = {source: (None, None)}
    parents_bwd: ParentMap = {target: (None, None)}
    visited_fwd = {source}
    visited_bwd = {target}

    nodes_expanded_fwd = 0
    nodes_expanded_bwd = 0
    edges_considered = 0

    while frontier_fwd and frontier_bwd:
        # Expande sempre a frente menor
        if len(frontier_fwd) <= len(frontier_bwd):
            meet, ne, ec = _expand_one_layer_metrics(frontier_fwd, parents_fwd, visited_fwd, parents_bwd)
            nodes_expanded_fwd += ne
        else:
            meet, ne, ec = _expand_one_layer_metrics(frontier_bwd, parents_bwd, visited_bwd, parents_fwd)
            nodes_expanded_bwd += ne
        edges_considered += ec

        if meet is not None:
            path = _reconstruct_bidirectional_path(meet, parents_fwd, parents_bwd)
            t1 = time.perf_counter()
            if os.getenv("METRICS") == "1":
                print("\n[metrics]")
                print(f"nodes_expanded_fwd: {nodes_expanded_fwd}")
                print(f"nodes_expanded_bwd: {nodes_expanded_bwd}")
                print(f"edges_considered:   {edges_considered}")
                print(f"time_ms:            {round((t1 - t0)*1000, 3)}")
            return path

    # se não encontrar
    t1 = time.perf_counter()
    if os.getenv("METRICS") == "1":
        print("\n[metrics]")
        print(f"nodes_expanded_fwd: {nodes_expanded_fwd}")
        print(f"nodes_expanded_bwd: {nodes_expanded_bwd}")
        print(f"edges_considered:   {edges_considered}")
        print(f"time_ms:            {round((t1 - t0)*1000, 3)}")
    return None


def _expand_one_layer_metrics(frontier: "deque[str]",
                              parents_self: ParentMap,
                              visited_self: set,
                              parents_other: ParentMap) -> Tuple[Optional[str], int, int]:
    """Versão com métricas da expansão de camada."""
    nodes_expanded = 0
    edges_considered = 0
    layer_size = len(frontier)

    for _ in range(layer_size):
        current = frontier.popleft()
        nodes_expanded += 1
        for movie_id, neighbor in neighbors_for_person(current):
            edges_considered += 1
            if neighbor in visited_self:
                continue
            parents_self[neighbor] = (current, movie_id)
            visited_self.add(neighbor)
            if neighbor in parents_other:
                return neighbor, nodes_expanded, edges_considered
            frontier.append(neighbor)
    return None, nodes_expanded, edges_considered


def _reconstruct_bidirectional_path(meet: str,
                                    parents_fwd: ParentMap,
                                    parents_bwd: ParentMap) -> List[Tuple[str, str]]:
    """
    Reconstrói o caminho completo unindo:
      - parte forward: source -> ... -> meet
      - parte backward: meet -> ... -> target
    Retorna lista de (movie_id, person_id) do source ao target.
    """
    # sobe do 'meet' até a origem usando parents_fwd
    left: List[Tuple[str, str]] = []
    node = meet
    while True:
        parent, via_movie = parents_fwd[node]
        if parent is None:
            break
        left.append((via_movie, node))
        node = parent
    left.reverse()  # agora está source -> meet

    # desce do 'meet' até o target usando parents_bwd
    right: List[Tuple[str, str]] = []
    node = meet
    while True:
        parent, via_movie = parents_bwd[node]
        if parent is None:
            break
        # do lado backward, avançamos rumo ao target
        right.append((via_movie, parent))
        node = parent

    return left + right


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name_ = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name_}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for pid in movies[movie_id]["stars"]:
            neighbors.add((movie_id, pid))
    return neighbors


if __name__ == "__main__":
    main()
