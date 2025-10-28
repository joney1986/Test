from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes, can be configured more securely

    # Configuration
    # In a real app, these should be loaded from environment variables
    app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.sqlite' # Store db in root
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'another-super-secret-key-for-jwt'

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models # Import models to register them with SQLAlchemy

    # Import and register blueprints for routes will go here in the next step
    # from .routes.auth import auth_bp
    # from .routes.resume import resume_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(resume_bp, url_prefix='/api')

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.route('/api/auth/register', methods=['POST'])
    def register_user():
        from .models import User
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "Email already exists"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login_user():
        from .models import User
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token)

        return jsonify({"msg": "Bad email or password"}), 401

    @app.route('/api/resume', methods=['GET'])
    @jwt_required()
    def get_resume():
        from .models import Resume
        import json
        current_user_id = get_jwt_identity()
        resume = Resume.query.filter_by(user_id=current_user_id).first()
        if resume:
            # The data is stored as a JSON string, so we parse it back to an object
            return jsonify(json.loads(resume.data))
        return jsonify(None)

    @app.route('/api/resume', methods=['POST'])
    @jwt_required()
    def save_resume():
        from .models import Resume
        import json
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if data is None:
            return jsonify({"msg": "No data provided"}), 400

        resume = Resume.query.filter_by(user_id=current_user_id).first()

        resume_data_str = json.dumps(data)

        if resume:
            resume.data = resume_data_str
        else:
            resume = Resume(data=resume_data_str, user_id=current_user_id)
            db.session.add(resume)

        db.session.commit()
        return jsonify({"msg": "Resume saved successfully"})

    @app.route('/')
    def index():
        return "Backend server is running."

    return app
