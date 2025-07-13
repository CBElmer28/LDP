from flask import Flask
from config import Config
from routes import main_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'super_secret_key' # No se flaco la contrase;a es no hay contrase;a 

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)