from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Tarea(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    titulo      = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), default='')
    completada  = db.Column(db.Boolean, default=False)
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'titulo':      self.titulo,
            'descripcion': self.descripcion,
            'completada':  self.completada,
            'creado_en':   self.creado_en.strftime('%Y-%m-%d %H:%M:%S')
        }


with app.app_context():
    db.create_all()


@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    """
    Obtener todas las tareas
    ---
    responses:
      200:
        description: Lista de tareas
    """
    tareas = Tarea.query.all()
    return jsonify([t.to_dict() for t in tareas])


@app.route('/api/tareas/<int:id>', methods=['GET'])
def get_tarea(id):
    """
    Obtener una tarea por ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tarea encontrada
      404:
        description: Tarea no encontrada
    """
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    return jsonify(tarea.to_dict())


@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    """
    Crear una nueva tarea
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            titulo:
              type: string
              example: Comprar leche
            descripcion:
              type: string
              example: En el supermercado
    responses:
      201:
        description: Tarea creada
      400:
        description: El titulo es obligatorio
    """
    data = request.get_json()

    if not data or not data.get('titulo'):
        return jsonify({'error': 'El titulo es obligatorio'}), 400

    nueva = Tarea(
        titulo=data['titulo'],
        descripcion=data.get('descripcion', '')
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.to_dict()), 201


@app.route('/api/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    """
    Actualizar una tarea existente
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          properties:
            titulo:
              type: string
              example: Tarea actualizada
            descripcion:
              type: string
              example: Nueva descripcion
            completada:
              type: boolean
              example: true
    responses:
      200:
        description: Tarea actualizada
      404:
        description: Tarea no encontrada
    """
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    data = request.get_json()
    tarea.titulo      = data.get('titulo', tarea.titulo)
    tarea.descripcion = data.get('descripcion', tarea.descripcion)
    tarea.completada  = data.get('completada', tarea.completada)
    db.session.commit()
    return jsonify(tarea.to_dict())


@app.route('/api/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    """
    Eliminar una tarea
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Tarea eliminada
      404:
        description: Tarea no encontrada
    """
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    db.session.delete(tarea)
    db.session.commit()
    return jsonify({'mensaje': 'Tarea eliminada'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)