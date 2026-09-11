import json
from pathlib import Path

from flask import Flask, jsonify, request, render_template

from informed import a_star, greedy_best_first
from uninformed import bfs, dfs, ids, ucs

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "map_data.json"

app = Flask(__name__)


with DATA_FILE.open("r", encoding="utf-8") as handle:
    graph_data = json.load(handle)

GRAPH = graph_data["adjacency"]
GRAPH["_meta"] = {node["id"]: {"lat": node["lat"], "lon": node["lon"]} for node in graph_data["nodes"]}

ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "ids": ids,
    "greedy": greedy_best_first,
    "astar": a_star,
}

CONCEPT_NOTES = {
    "bfs": {
        "title": "Breadth-First Search",
        "main_idea": "Expand the frontier by depth level, visiting all neighbors of the current node before moving deeper.",
        "node_selection": "The next node is the earliest queued node in FIFO order. This ensures the shallowest path is explored first.",
        "information_used": "Uses the graph structure and depth, not path cost or heuristic estimates.",
    },
    "dfs": {
        "title": "Depth-First Search",
        "main_idea": "Follow one branch as far as possible before backtracking to explore alternate routes.",
        "node_selection": "The next node is the most recently added node on the stack, which favors deep exploration.",
        "information_used": "Uses graph structure and depth, without path cost or heuristic guidance.",
    },
    "ucs": {
        "title": "Uniform-Cost Search",
        "main_idea": "Expand the lowest accumulated path-cost node first, so the cheapest route is found systematically.",
        "node_selection": "The next node is chosen by the smallest known path cost from the start.",
        "information_used": "Uses path cost from the start, not heuristic information.",
    },
    "ids": {
        "title": "Iterative Deepening Search",
        "main_idea": "Repeat depth-limited DFS with increasing limit values to balance memory efficiency and completeness.",
        "node_selection": "At each iteration, it explores nodes up to a growing depth limit before increasing the limit.",
        "information_used": "Uses depth information and the graph structure, with no heuristic or edge-cost guidance.",
    },
    "greedy": {
        "title": "Greedy Best-First Search",
        "main_idea": "Always expand the neighbor that appears closest to the goal based on a heuristic estimate.",
        "node_selection": "The next node is chosen by the smallest heuristic estimate to the goal.",
        "information_used": "Uses heuristic guidance, but ignores accumulated path cost.",
    },
    "astar": {
        "title": "A* Search",
        "main_idea": "Combine the cost already spent with an estimate of the remaining cost to the goal.",
        "node_selection": "The next node minimizes f(n) = g(n) + h(n), balancing accuracy and efficiency.",
        "information_used": "Uses both path cost and heuristic information to prioritize promising routes.",
    },
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/algorithms")
def list_algorithms():
    return jsonify({"algorithms": list(ALGORITHMS.keys())})


@app.route("/api/cities")
def get_cities():
    cities = sorted([node["id"] for node in graph_data["nodes"]])
    return jsonify({"cities": cities})


@app.route("/api/graph")
def get_graph():
    return jsonify({
        "country": graph_data.get("country", ""),
        "nodes": [
            {
                "id": node["id"],
                "name": node.get("name", node["id"]),
                "lat": node["lat"],
                "lon": node["lon"],
            }
            for node in graph_data.get("nodes", [])
        ],
        "edges": [
            {
                "source": edge["source"],
                "target": edge["target"],
                "distance_km": edge.get("distance_km"),
            }
            for edge in graph_data.get("edges", [])
        ],
    })


@app.route("/api/search", methods=["POST"])
def search_route():
    payload = request.get_json(silent=True) or {}
    start = payload.get("source")
    goal = payload.get("destination")
    algorithm_name = payload.get("algorithm")

    if not start or not goal or not algorithm_name:
        return jsonify({"error": "source, destination, and algorithm are required."}), 400

    if start not in GRAPH or goal not in GRAPH:
        return jsonify({"error": "Source or destination is not in the graph."}), 400

    algorithm = ALGORITHMS.get(algorithm_name.lower())
    if algorithm is None:
        return jsonify({"error": "Unsupported algorithm."}), 400

    result = algorithm(GRAPH, start, goal)
    concept = CONCEPT_NOTES.get(algorithm_name.lower(), {})
    return jsonify({
        "algorithm": algorithm_name,
        "source": start,
        "destination": goal,
        "path": result.get("path", []),
        "cost": result.get("cost", float("inf")),
        "visited": result.get("visited", []),
        "concept": concept,
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "nodes": len(graph_data["nodes"]), "country": graph_data["country"]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
