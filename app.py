from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Modelo de tarea
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


# Obtener todas las tareas
@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    tareas = Tarea.query.all()
    return jsonify([t.to_dict() for t in tareas])


# Obtener una tarea por id
@app.route('/api/tareas/<int:id>', methods=['GET'])
def get_tarea(id):
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404
    return jsonify(tarea.to_dict())


# Crear una tarea
@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
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


# Actualizar una tarea
@app.route('/api/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    data = request.get_json()
    tarea.titulo      = data.get('titulo', tarea.titulo)
    tarea.descripcion = data.get('descripcion', tarea.descripcion)
    tarea.completada  = data.get('completada', tarea.completada)
    db.session.commit()
    return jsonify(tarea.to_dict())


# Eliminar una tarea
@app.route('/api/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    tarea = Tarea.query.get(id)
    if tarea is None:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    db.session.delete(tarea)
    db.session.commit()
    return jsonify({'mensaje': 'Tarea eliminada'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
