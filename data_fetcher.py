import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import requests

COUNTRY = "Myanmar"
ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "map_data.json"

CITY_COORDINATES = {
    "Yangon": (16.8661, 96.1951),
    "Bago": (17.3357, 96.4814),
    "Naypyidaw": (19.7633, 96.0785),
    "Mandalay": (21.9588, 96.0891),
    "Pyin Oo Lwin": (22.0368, 96.4597),
    "Lashio": (22.9770, 97.7526),
    "Meiktila": (20.8838, 95.8582),
    "Taunggyi": (20.7897, 97.0365),
    "Mawlamyine": (16.4456, 97.6260),
    "Pathein": (16.7833, 94.7333),
    "Hpa-An": (16.8694, 97.6679),
    "Sagaing": (21.8787, 95.9786),
    "Monywa": (22.0717, 95.1295),
    "Kalay": (23.1944, 94.0365),
    "Magway": (20.1500, 94.9325),
    "Myitkyina": (25.3833, 97.4000),
    "Sittwe": (20.1467, 92.8998),
    "Dawei": (14.0835, 98.1998),
    "Myeik": (12.4398, 98.6002),
    "Muse": (23.2700, 97.9290),
    "Kyaikto": (17.3378, 97.0244),
    "Akyab": (20.1500, 92.9000),
}

CONNECTIONS = [
    ("Yangon", "Bago"),
    ("Bago", "Naypyidaw"),
    ("Naypyidaw", "Mandalay"),
    ("Mandalay", "Pyin Oo Lwin"),
    ("Mandalay", "Lashio"),
    ("Naypyidaw", "Meiktila"),
    ("Meiktila", "Taunggyi"),
    ("Yangon", "Pathein"),
    ("Yangon", "Mawlamyine"),
    ("Mawlamyine", "Hpa-An"),
    ("Yangon", "Dawei"),
    ("Dawei", "Myeik"),
    ("Mandalay", "Sagaing"),
    ("Sagaing", "Monywa"),
    ("Monywa", "Kalay"),
    ("Naypyidaw", "Magway"),
    ("Magway", "Sittwe"),
    ("Mandalay", "Myitkyina"),
    ("Myeik", "Dawei"),
    ("Muse", "Lashio"),
    ("Mandalay", "Muse"),
    ("Bago", "Kyaikto"),
    ("Kyaikto", "Hpa-An"),
    ("Magway", "Akyab"),
    ("Sittwe", "Akyab"),
    ("Pathein", "Hpa-An"),
    ("Naypyidaw", "Taunggyi"),
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def geocode_city(city: str) -> Tuple[float, float]:
    coords = CITY_COORDINATES.get(city)
    if coords:
        return coords

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{city}, Myanmar",
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    headers = {"User-Agent": "MyanmarSearchVisualizer/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    raise ValueError(f"Could not geocode city: {city}")


def osrm_distance(source: str, target: str) -> float:
    source_coords = geocode_city(source)
    target_coords = geocode_city(target)
    url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=false&geometries=geojson"
    req_url = url.format(source_coords[1], source_coords[0], target_coords[1], target_coords[0])
    try:
        response = requests.get(req_url, timeout=20)
        response.raise_for_status()
        payload = response.json()
        if payload.get("routes"):
            return float(payload["routes"][0]["distance"]) / 1000.0
    except Exception:
        pass
    return haversine_km(*source_coords, *target_coords) * 1.15


def normalize_name(name: str) -> str:
    return name.strip()


def build_graph() -> Dict[str, object]:
    city_names = []
    seen = set()
    for city_a, city_b in CONNECTIONS:
        for city in (city_a, city_b):
            if city not in seen:
                seen.add(city)
                city_names.append(city)

    nodes = []
    for city in city_names:
        lat, lon = geocode_city(city)
        nodes.append({"id": city, "name": city, "lat": lat, "lon": lon})

    adjacency: Dict[str, Dict[str, float]] = {city: {} for city in city_names}
    edges = []

    for source, target in CONNECTIONS:
        if source not in adjacency or target not in adjacency:
            continue
        distance = osrm_distance(source, target)
        adjacency[source][target] = round(distance, 2)
        adjacency[target][source] = round(distance, 2)
        edges.append({
            "source": source,
            "target": target,
            "distance_km": round(distance, 2),
        })

    # Ensure the graph is connected by adding a few key connector edges if absent.
    for city in city_names:
        if city not in adjacency:
            adjacency[city] = {}

    for city in city_names:
        if not adjacency[city]:
            fallback = city_names[0]
            if fallback != city:
                lat1, lon1 = geocode_city(city)
                lat2, lon2 = geocode_city(fallback)
                fallback_distance = haversine_km(lat1, lon1, lat2, lon2) * 1.15
                adjacency[city][fallback] = round(fallback_distance, 2)
                adjacency[fallback][city] = round(fallback_distance, 2)
                edges.append({
                    "source": city,
                    "target": fallback,
                    "distance_km": round(fallback_distance, 2),
                })

    data = {
        "country": COUNTRY,
        "nodes": nodes,
        "edges": edges,
        "adjacency": adjacency,
    }
    return data


def main() -> None:
    graph_data = build_graph()
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(graph_data, handle, ensure_ascii=False, indent=2)
    print(f"Saved graph to {OUTPUT_PATH}")
    print(f"Nodes: {len(graph_data['nodes'])}")
    print(f"Edges: {len(graph_data['edges'])}")


if __name__ == "__main__":
    main()
