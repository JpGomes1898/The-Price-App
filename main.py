import os
import json
import datetime
import jwt
from functools import wraps
from flask import Flask, request, jsonify, render_template, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from jinja2 import TemplateNotFound

# --- Inicialização da Aplicação ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
bcrypt = Bcrypt(app)

# --- Configuração ---
app.config['SECRET_KEY'] = 'esta-e-uma-chave-secreta-muito-segura' # Troque por uma chave mais segura em produção
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recipes_users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelos do Banco de Dados ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    recipes = db.relationship('Recipe', backref='owner', lazy=True, cascade="all, delete-orphan")
    ingredients = db.relationship('Ingredient', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    fixed_costs = db.Column(db.Text, nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    profit_margin = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        # (A lógica interna desta função não muda)
        try:
            ingredients_list = json.loads(self.ingredients)
            fixed_costs_list = json.loads(self.fixed_costs)
            ingredient_costs_total = sum(item.get('cost', 0) for item in ingredients_list)
            fixed_costs_total = sum(item.get('cost', 0) for item in fixed_costs_list)
            total_cost = ingredient_costs_total + fixed_costs_total
            if self.total_quantity > 0:
                unit_cost = total_cost / self.total_quantity
                unit_profit = unit_cost * (self.profit_margin / 100)
                unit_price = unit_cost + unit_profit
                total_revenue = unit_price * self.total_quantity
                total_profit = unit_profit * self.total_quantity
            else:
                unit_cost, unit_profit, unit_price, total_revenue, total_profit = 0, 0, 0, 0, 0
        except (json.JSONDecodeError, TypeError):
            ingredients_list, fixed_costs_list, total_cost, unit_cost, unit_profit, unit_price, total_revenue, total_profit = [], [], 0, 0, 0, 0, 0, 0
        return {
            'id': self.id, 'productName': self.product_name, 'ingredients': ingredients_list,
            'fixedCosts': fixed_costs_list, 'totalQuantity': self.total_quantity, 'profitMargin': self.profit_margin,
            'calculated': { 'totalCost': round(total_cost, 2), 'unitCost': round(unit_cost, 2), 'unitProfit': round(unit_profit, 2),
                'unitPrice': round(unit_price, 2), 'totalRevenue': round(total_revenue, 2), 'totalProfit': round(total_profit, 2) }
        }

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='_user_ingredient_uc'),)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'cost': self.cost, 'unit': self.unit}

# --- Decorator de Autenticação ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token está faltando!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token é inválido!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- Rotas de Páginas ---
@app.route('/')
def root():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    try:
        return render_template('login.html')
    except TemplateNotFound:
        abort(404)

@app.route('/app')
def index():
    # Esta rota agora servirá a aplicação principal
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)

# --- Rotas da API de Autenticação ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Utilizador já existe'}), 409
    
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Utilizador registado com sucesso'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'error': 'Credenciais inválidas'}), 401

# --- Rotas da API (Agora Protegidas) ---
@app.route('/api/recipes', methods=['POST'])
@token_required
def add_recipe(current_user):
    data = request.get_json()
    new_recipe = Recipe(
        product_name=data['productName'], ingredients=json.dumps(data['ingredients']),
        fixed_costs=json.dumps(data['fixedCosts']), total_quantity=data['totalQuantity'],
        profit_margin=data['profitMargin'], owner=current_user
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify(new_recipe.to_dict()), 201

@app.route('/api/recipes', methods=['GET'])
@token_required
def get_recipes(current_user):
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.id.desc()).all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@app.route('/api/recipes/<int:id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, id):
    recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Receita excluída com sucesso'})

@app.route('/api/ingredients', methods=['POST'])
@token_required
def add_ingredient(current_user):
    data = request.get_json()
    if Ingredient.query.filter_by(name=data['name'], user_id=current_user.id).first():
        return jsonify({'error': 'Ingrediente com este nome já existe'}), 409
    new_ingredient = Ingredient(name=data['name'], cost=data['cost'], unit=data['unit'], owner=current_user)
    db.session.add(new_ingredient)
    db.session.commit()
    return jsonify(new_ingredient.to_dict()), 201

@app.route('/api/ingredients', methods=['GET'])
@token_required
def get_ingredients(current_user):
    ingredients = Ingredient.query.filter_by(user_id=current_user.id).order_by(Ingredient.name).all()
    return jsonify([ing.to_dict() for ing in ingredients])

@app.route('/api/ingredients/<int:id>', methods=['DELETE'])
@token_required
def delete_ingredient(current_user, id):
    ingredient = Ingredient.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({'message': 'Ingrediente excluído com sucesso'})

@app.route('/api/dashboard-metrics')
@token_required
def get_dashboard_metrics(current_user):
    recipes_query = Recipe.query.filter_by(user_id=current_user.id).all()
    total_recipes = len(recipes_query)
    most_lucrative_product, highest_profit, total_profit_margin = None, -1, 0
    if total_recipes > 0:
        for recipe in recipes_query:
            unit_profit = recipe.to_dict()['calculated']['unitProfit']
            if unit_profit > highest_profit:
                highest_profit, most_lucrative_product = unit_profit, recipe.product_name
            total_profit_margin += recipe.profit_margin
        average_profit_margin = total_profit_margin / total_recipes
    else:
        average_profit_margin = 0
    return jsonify({
        'totalRecipes': total_recipes, 'mostLucrativeProduct': most_lucrative_product,
        'averageProfitMargin': round(average_profit_margin, 2)
    })
    
# (As rotas PUT foram omitidas para simplicidade, mas a lógica de proteção seria a mesma)

# --- Execução Principal ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

