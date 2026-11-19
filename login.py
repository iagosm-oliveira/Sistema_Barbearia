import sqlite3
from hashlib import sha256

conn = sqlite3.connect("barbearia.db")
cursor = conn.cursor()

def login(senha,email):
    while True:
        nome = input("Nome completo: ")
        email = input("Email: ")
        senha = input("Senha: ")
        senha_hash = sha256(senha.encode('utf-8')).hexdigest()

        cursor.execute('''SELECT (NOME,EMAIL,SENHA) FROM USUARIOS
                        WHERE EMAIL, SENHA = ? ''',(email,senha_hash))

        resultado = cursor.fetchone()
        if resultado[0] > 0:
            print("Login bem sucedido!")


conn.close()
quit()