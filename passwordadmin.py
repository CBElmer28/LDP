from werkzeug.security import generate_password_hash

contrasena_plana_admin = 'admin123' 

hashed_password_admin = generate_password_hash(contrasena_plana_admin)
print(hashed_password_admin)