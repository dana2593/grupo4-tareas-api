import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_get_tareas_vacio(client):
    res = client.get('/api/tareas')
    assert res.status_code == 200
    assert res.get_json() == []


def test_crear_tarea(client):
    res = client.post('/api/tareas', json={'titulo': 'Comprar leche'})
    assert res.status_code == 201
    data = res.get_json()
    assert data['titulo'] == 'Comprar leche'
    assert data['completada'] == False


def test_crear_tarea_sin_titulo(client):
    res = client.post('/api/tareas', json={'descripcion': 'sin titulo'})
    assert res.status_code == 400


def test_get_tarea_por_id(client):
    creada = client.post('/api/tareas', json={'titulo': 'Estudiar'}).get_json()
    res = client.get(f'/api/tareas/{creada["id"]}')
    assert res.status_code == 200
    assert res.get_json()['titulo'] == 'Estudiar'


def test_get_tarea_no_existe(client):
    res = client.get('/api/tareas/999')
    assert res.status_code == 404


def test_actualizar_tarea(client):
    creada = client.post('/api/tareas', json={'titulo': 'Original'}).get_json()
    res = client.put(f'/api/tareas/{creada["id"]}',
                     json={'titulo': 'Modificada', 'completada': True})
    assert res.status_code == 200
    assert res.get_json()['titulo'] == 'Modificada'
    assert res.get_json()['completada'] == True


def test_eliminar_tarea(client):
    creada = client.post('/api/tareas', json={'titulo': 'Borrar esto'}).get_json()
    res = client.delete(f'/api/tareas/{creada["id"]}')
    assert res.status_code == 200

    res2 = client.get(f'/api/tareas/{creada["id"]}')
    assert res2.status_code == 404
