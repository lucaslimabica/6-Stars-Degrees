import csv
import sys
from typing import List, Tuple
import time

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

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")
        shortest_path_dps(source, target)


def shortest_path(source: str, target: str) -> List[Tuple[int, int]]:
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.
    
    And print the metrics about how many nodes, paths checkeds and how much time it had spent
    
    Args:
        source (str): The unique ID of the starting person
        target (str): The unique ID of the target person

    Returns:
        List[Tuple[str, str]]: 
            A list of (movie_id, person_id) pairs representing the shortest
            path from `source` to `target`. If no connection exists, returns None
            If `source` equals `target`, returns an empty array

    Example:
        >>> shortest_path("158", "102")
        [("112384", "102")]  # Tom Hanks → Kevin Bacon (Apollo 13)

    If no possible path, returns None.
    """
    print("- | Dados da Busca BPS | -")
    t0 = time.perf_counter()
    
    # Caso sejam o mesmo, rertorna array vazio pro check50
    if source == target:
        t1 = time.perf_counter()
        print(f"Atores Expandidos: 0 \nParcerias Verificadas: 0 \nTempo em segundos {t1 - t0:.6f}")
        return []

    # Set de início, com o primeiro node e set de nodes explorados
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    explored = set()
    nodes_explorados = 0
    vizinhancas_exploradas = 0
    
    while True:
        # Check da fronteira vazia (na main() dará retorno de "no solution")
        if frontier.empty():
            t1 = time.perf_counter()
            print(f"Atores Expandidos: {nodes_explorados} \nParcerias Verificadas: {vizinhancas_exploradas} \nTempo em segundos {t1 - t0:.6f}")
            return None
        
        # Começando a buscar nos vizinhos do node na beira da fronteira
        node = frontier.remove()
        explored.add(node.state)
        nodes_explorados += 1
        for movie_id, person_id in neighbors_for_person(node.state):
            # Verificando se já não vi a pessoa num node já deletado ou a pessoa num outro node atual na fronteira (if igual, mas ao contrário, do Maze.py)
            if person_id in explored or frontier.contains_state(person_id):
                continue  # ignoro esse, sem criar um child pra ele nem nada
            vizinhancas_exploradas += 1
            
            child = Node(state=person_id, parent=node, action=movie_id)
            
            # Verificando se o node vizinho então vai ser o target 
            if child.state == target:
                path = []
                current = child
                while current.parent is not None:  # basicamente o mesmo do maze
                    # lista de tuplas que será o retorno final
                    path.append((current.action, current.state))
                    current = current.parent  # filho vira o pai, rewind no tempo
                path.reverse()
                t1 = time.perf_counter()
                print(f"Atores Expandidos: {nodes_explorados} \nParcerias Verificadas: {vizinhancas_exploradas} \nTempo em segundos {t1 - t0:.6f}")
                return path  # Vai sair da function no instante q achar o state target num vizinho
            
            # Basicamente inverti a ordem do check de solution pois comecei o código do pressuposto que o state inicial nunca é o resultado
            else:
                frontier.add(child)
                
def shortest_path_dps(source: str, target: str) -> None:
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.
    
    And print the metrics about how many nodes, paths checkeds and how much time it had spent
    
    Args:
        source (str): The unique ID of the starting person
        target (str): The unique ID of the target person

    Returns:
        None

    """
    print("- | Dados da Busca DPS | -")
    t0 = time.perf_counter()

    if source == target:
        t1 = time.perf_counter()
        print(f"Atores Expandidos: 0 \nParcerias Verificadas: 0 \nTempo em segundos {t1 - t0:.6f}")

    start = Node(state=source, parent=None, action=None)
    frontier = StackFrontier()
    frontier.add(start)
    explored = set()
    nodes_explorados = 0
    vizinhancas_exploradas = 0
    
    while True:
        if frontier.empty():
            t1 = time.perf_counter()
            print(f"Atores Expandidos: {nodes_explorados} \nParcerias Verificadas: {vizinhancas_exploradas} \nTempo em segundos {t1 - t0:.6f}")
            return None
        
        node = frontier.remove()
        explored.add(node.state)
        nodes_explorados += 1
        for movie_id, person_id in neighbors_for_person(node.state):
            if person_id in explored or frontier.contains_state(person_id):
                continue  
            vizinhancas_exploradas += 1
            
            child = Node(state=person_id, parent=node, action=movie_id)
            
            if child.state == target:
                path = []
                current = child
                while current.parent is not None: 
                    path.append((current.action, current.state))
                    current = current.parent  
                path.reverse()
                t1 = time.perf_counter()
                print(f"Atores Expandidos: {nodes_explorados} \nParcerias Verificadas: {vizinhancas_exploradas} \nTempo em segundos {t1 - t0:.6f}")
                return None
            
            else:
                frontier.add(child)


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
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
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
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
