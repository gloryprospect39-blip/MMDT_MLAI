import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_graph_api_exposes_nodes_and_edges(client):
    response = client.get('/api/graph')

    assert response.status_code == 200
    payload = response.get_json()
    assert 'nodes' in payload
    assert 'edges' in payload
    assert len(payload['nodes']) >= 20
    assert len(payload['edges']) >= 20
    first_node = payload['nodes'][0]
    assert {'id', 'lat', 'lon'}.issubset(first_node)
