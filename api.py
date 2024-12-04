from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import json

# Создаем Flask-приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/tax_calculator_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Включаем логирование SQL-запросов для отладки

# Инициализируем API и Swagger
api = Api(app, version='1.0', title='Tax Calculator API', description='API для управления налоговыми вычетами')

# Создаем базу данных
db = SQLAlchemy(app)

# Создаем модель для вычетов
class Deduction(db.Model):
    __tablename__ = 'deductions'  # Указываем имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_rate_id = db.Column(db.Integer, nullable=True)  # ID ставки налога (может быть NULL)
    user_id = db.Column(db.Integer, nullable=True)  # ID пользователя (может быть NULL)

# Определяем пространство имен
deductions_ns = api.namespace('deductions', description='Operations related to deductions')

# Модель данных для API
deduction_model = api.model('Deduction', {
    'id': fields.Integer(readonly=True, description='Уникальный идентификатор вычета'),
    'name': fields.String(required=True, description='Название вычета'),
    'amount': fields.Float(required=True, description='Сумма вычета'),
    'tax_rate_id': fields.Integer(description='ID ставки налога (опционально)'),
    'user_id': fields.Integer(description='ID пользователя (опционально)')
})

# Ресурс для работы с вычетами
@deductions_ns.route('/')
class DeductionList(Resource):
    @deductions_ns.doc('list_deductions')
    @deductions_ns.marshal_list_with(deduction_model)
    def get(self):
        """Получить все вычеты"""
        try:
            deductions = Deduction.query.all()
            return deductions, 200
        except SQLAlchemyError as e:
            return {'message': 'Ошибка при получении данных из базы.', 'error': str(e)}, 500

    @deductions_ns.doc('create_deduction')
    @deductions_ns.expect(deduction_model)
    @deductions_ns.marshal_with(deduction_model, code=201)
    def post(self):
        """Создать новый вычет"""
        try:
            data = request.json
            new_deduction = Deduction(
                name=data['name'],
                amount=data['amount'],
                tax_rate_id=data.get('tax_rate_id'),
                user_id=data.get('user_id')
            )
            db.session.add(new_deduction)
            db.session.commit()
            return new_deduction, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Ошибка при добавлении данных в базу.', 'error': str(e)}, 500

@deductions_ns.route('/<int:id>')
@deductions_ns.response(404, 'Deduction not found')
@deductions_ns.param('id', 'Идентификатор вычета')
class DeductionResource(Resource):
    @deductions_ns.doc('get_deduction')
    @deductions_ns.marshal_with(deduction_model)
    def get(self, id):
        """Получить вычет по ID"""
        try:
            deduction = Deduction.query.get_or_404(id)
            return deduction
        except SQLAlchemyError as e:
            return {'message': 'Ошибка при получении данных из базы.', 'error': str(e)}, 500

    @deductions_ns.doc('update_deduction')
    @deductions_ns.expect(deduction_model)
    @deductions_ns.marshal_with(deduction_model)
    def put(self, id):
        """Обновить вычет по ID"""
        try:
            deduction = Deduction.query.get_or_404(id)
            data = request.json
            deduction.name = data['name']
            deduction.amount = data['amount']
            deduction.tax_rate_id = data.get('tax_rate_id')
            deduction.user_id = data.get('user_id')
            db.session.commit()
            return deduction
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Ошибка при обновлении данных в базе.', 'error': str(e)}, 500

    @deductions_ns.doc('delete_deduction')
    def delete(self, id):
        """Удалить вычет по ID"""
        try:
            deduction = Deduction.query.get_or_404(id)
            db.session.delete(deduction)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Ошибка при удалении данных из базы.', 'error': str(e)}, 500


# Функция для инициализации базы данных
def create_tables():
    with app.app_context():  # Создаем контекст приложения
        db.create_all()  # Создаем таблицы, если их нет

# Читаем настройки из файла application.json
with open('application.json') as config_file:
    config = json.load(config_file)

# Применяем настройки из файла
app.config.update(config)


# Главный блок
if __name__ == '__main__':
    create_tables()  # Создаем таблицы
    app.run(debug=True)
