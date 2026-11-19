import random
import smtplib
import sqlite3
from email.message import EmailMessage
from hashlib import sha256

from db import conectar

# Gmail da barbearia que envia os códigos de recuperação
EMAIL_REMETENTE = "tuggofmirrah@gmail.com"
SENHA_APP = "qmfs emkb glkf uuec"  # Senha de App do Google (16 letras)


def hash_senha(senha):
    return sha256(senha.encode("utf-8")).hexdigest()


def enviar_email_codigo(destinatario, codigo):
    msg = EmailMessage()
    msg["Subject"] = "Código de Recuperação de Senha - Barbearia"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg.set_content(f"Seu código de verificação para redefinir a senha é: {codigo}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_REMETENTE, SENHA_APP)
            smtp.send_message(msg)
        print("Código enviado para o seu e-mail!")
        return True
    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")
        return False


def login():
    print("\n--- LOGIN ---")
    email = input("Email: ").strip()
    senha = input("Senha: ")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, NOME, PAPEL FROM USUARIOS WHERE EMAIL = ? AND SENHA = ?",
        (email, hash_senha(senha)),
    )
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        print(f"\nBem-vindo(a), {resultado[1]}!")
        return {"id": resultado[0], "nome": resultado[1], "papel": resultado[2]}

    print("Email ou senha inválidos.")
    return None


def cadastrar_cliente():
    print("\n--- CADASTRO DE CLIENTE ---")
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ")

    if not nome or not email or not senha:
        print("Todos os campos são obrigatórios.")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, 'Cliente')",
            (nome, email, hash_senha(senha)),
        )
        conn.commit()
        print("Cadastro realizado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: este e-mail já está cadastrado.")
    finally:
        conn.close()


def recuperar_senha():
    print("\n--- RECUPERAR SENHA ---")
    email = input("Digite seu e-mail cadastrado: ").strip()

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM USUARIOS WHERE EMAIL = ?", (email,))
    usuario = cursor.fetchone()

    if not usuario:
        print("E-mail não encontrado.")
        conn.close()
        return

    codigo = str(random.randint(100000, 999999))
    if not enviar_email_codigo(email, codigo):
        conn.close()
        return

    codigo_digitado = input("Digite o código recebido: ").strip()
    if codigo_digitado != codigo:
        print("Código inválido.")
        conn.close()
        return

    nova_senha = input("Digite a nova senha: ")
    if not nova_senha:
        print("A senha não pode ficar vazia.")
        conn.close()
        return

    cursor.execute(
        "UPDATE USUARIOS SET SENHA = ? WHERE EMAIL = ?",
        (hash_senha(nova_senha), email),
    )
    conn.commit()
    conn.close()
    print("Senha redefinida com sucesso!")