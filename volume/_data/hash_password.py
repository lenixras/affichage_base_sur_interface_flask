from werkzeug.security import generate_password_hash; print(generate_password_hash("your_pwd", method="pbkdf2:sha256"))
