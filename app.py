from flask import Flask, session
from config import Config
from routes import main_bp, admin_bp, auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'aqui_deberia_ir_una_contrase;a_talvez_pero_mejorar_ignorar'

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_user_status():
        user_logged_in = session.get('user_id') is not None
        username = session.get('username') if user_logged_in else None
        is_admin = session.get('is_admin', False)

        return {
            'user_logged_in': user_logged_in,
            'username': username,
            'is_admin': is_admin,
        }

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)