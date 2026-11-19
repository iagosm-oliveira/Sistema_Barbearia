import os
import random
import smtplib
import sqlite3
from datetime import date, timedelta
from email.message import EmailMessage
from hashlib import sha256

DB_NAME = "barbearia.db"
HORARIOS = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_senha(senha):
    return sha256(senha.encode("utf-8")).hexdigest()


def inicializar_banco():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS USUARIOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NOME VARCHAR(100) NOT NULL,
                EMAIL VARCHAR(100) UNIQUE NOT NULL,
                SENHA VARCHAR(255) NOT NULL,
                PAPEL VARCHAR(20) NOT NULL CHECK (PAPEL IN ('Cliente', 'Funcionario', 'Dono'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS SERVICOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO VARCHAR(50) NOT NULL CHECK (TIPO IN ('Masculino', 'Feminino')),
                PRECO REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS AGENDAMENTOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CLIENTE_ID INTEGER NOT NULL,
                SERVICOS_ID INTEGER NOT NULL,
                FUNCIONARIOS_ID INTEGER NOT NULL,
                DATA DATE NOT NULL,
                HORARIO VARCHAR(5) NOT NULL,
                FOREIGN KEY (CLIENTE_ID) REFERENCES USUARIOS(ID),
                FOREIGN KEY (FUNCIONARIOS_ID) REFERENCES USUARIOS(ID),
                FOREIGN KEY (SERVICOS_ID) REFERENCES SERVICOS(ID)
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM SERVICOS").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO SERVICOS (ID, TIPO, PRECO) VALUES (1, 'Masculino', 40.00), (2, 'Feminino', 80.00)"
            )


def escolher(itens, texto="Escolha o número: "):
    try:
        return itens[int(input(texto)) - 1]
    except (ValueError, IndexError):
        print("Opção inválida.")
        return None


# --- ACESSO GERAL ---

def cadastrar_usuario(papel="Cliente"):
    print(f"\n--- CADASTRO ({papel.upper()}) ---")
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ")

    if not nome or not email or not senha:
        print("Preencha todos os campos.")
        return

    try:
        with conectar() as conn:
            conn.execute(
                "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, ?)",
                (nome, email, hash_senha(senha), papel),
            )
        print(f"{papel} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Este e-mail já está cadastrado.")


def login():
    print("\n--- LOGIN ---")
    email = input("Email: ").strip()
    senha = input("Senha: ")

    with conectar() as conn:
        user = conn.execute(
            "SELECT ID, NOME, PAPEL FROM USUARIOS WHERE EMAIL = ? AND SENHA = ?",
            (email, hash_senha(senha)),
        ).fetchone()

    if not user:
        print("Email ou senha inválidos.")
        return None

    print(f"\nBem-vindo(a), {user[1]}!")
    return {"id": user[0], "nome": user[1], "papel": user[2]}


def enviar_codigo(email, codigo):
    remetente = os.getenv("SMTP_EMAIL")
    senha_app = os.getenv("SMTP_SENHA")

    if not remetente or not senha_app:
        print(f"\n[Modo Teste] Código de verificação: {codigo}")
        return True

    msg = EmailMessage()
    msg["Subject"] = "Recuperação de Senha - Barbearia"
    msg["From"] = remetente
    msg["To"] = email
    msg.set_content(f"Seu código de verificação é: {codigo}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(remetente, senha_app)
            smtp.send_message(msg)
        print("Código enviado para o seu e-mail!")
        return True
    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")
        return False


def recuperar_senha():
    print("\n--- RECUPERAR SENHA ---")
    email = input("Email cadastrado: ").strip()

    with conectar() as conn:
        if not conn.execute("SELECT 1 FROM USUARIOS WHERE EMAIL = ?", (email,)).fetchone():
            print("E-mail não encontrado.")
            return

        codigo = str(random.randint(100000, 999999))
        if not enviar_codigo(email, codigo):
            return

        if input("Código recebido: ").strip() != codigo:
            print("Código inválido.")
            return

        nova_senha = input("Nova senha: ")
        if not nova_senha:
            print("A senha não pode ficar vazia.")
            return

        conn.execute("UPDATE USUARIOS SET SENHA = ? WHERE EMAIL = ?", (hash_senha(nova_senha), email))
        print("Senha redefinida com sucesso!")


# --- ÁREA DO CLIENTE ---

def agendar_corte(cliente_id):
    with conectar() as conn:
        barbeiros = conn.execute("SELECT ID, NOME FROM USUARIOS WHERE PAPEL = 'Funcionario'").fetchall()
        if not barbeiros:
            print("\nNenhum profissional cadastrado.")
            return

        print("\n--- PROFISSIONAIS ---")
        for i, b in enumerate(barbeiros, 1):
            print(f"{i}. {b[1]}")
        barbeiro = escolher(barbeiros)
        if not barbeiro:
            return

        dias = []
        d = date.today()
        while len(dias) < 6:
            if d.weekday() != 6:  # Pula domingo
                dias.append((d.strftime("%Y-%m-%d"), DIAS_SEMANA[d.weekday()]))
            d += timedelta(days=1)

        print("\n--- DIAS DISPONÍVEIS ---")
        for i, (data_str, dia_nome) in enumerate(dias, 1):
            print(f"{i}. {data_str} ({dia_nome})")
        dia = escolher(dias)
        if not dia:
            return

        ocupados = {
            r[0]
            for r in conn.execute(
                "SELECT HORARIO FROM AGENDAMENTOS WHERE FUNCIONARIOS_ID = ? AND DATA = ?",
                (barbeiro[0], dia[0]),
            ).fetchall()
        }
        livres = [h for h in HORARIOS if h not in ocupados]
        if not livres:
            print("\nSem horários livres neste dia.")
            return

        print("\n--- HORÁRIOS LIVRES ---")
        for i, h in enumerate(livres, 1):
            print(f"{i}. {h}")
        horario = escolher(livres)
        if not horario:
            return

        servicos = conn.execute("SELECT ID, TIPO, PRECO FROM SERVICOS").fetchall()
        print("\n--- SERVIÇOS ---")
        for i, s in enumerate(servicos, 1):
            print(f"{i}. {s[1]} - R$ {s[2]:.2f}")
        servico = escolher(servicos)
        if not servico:
            return

        conn.execute(
            "INSERT INTO AGENDAMENTOS (CLIENTE_ID, SERVICOS_ID, FUNCIONARIOS_ID, DATA, HORARIO) VALUES (?, ?, ?, ?, ?)",
            (cliente_id, servico[0], barbeiro[0], dia[0], horario),
        )
        print(f"\nConfirmado! {servico[1]} com {barbeiro[1]} em {dia[0]} às {horario}.")


def menu_cliente(usuario):
    while True:
        print(f"\n=== CLIENTE: {usuario['nome']} ===")
        print("1. Agendar Corte | 0. Sair")
        op = input("Escolha: ").strip()
        if op == "1":
            agendar_corte(usuario["id"])
        elif op == "0":
            break


# --- ÁREA DO FUNCIONÁRIO ---

def visualizar_agenda(funcionario_id):
    with conectar() as conn:
        agenda = conn.execute(
            """
            SELECT A.DATA, A.HORARIO, C.NOME, S.TIPO
            FROM AGENDAMENTOS A
            JOIN USUARIOS C ON A.CLIENTE_ID = C.ID
            JOIN SERVICOS S ON A.SERVICOS_ID = S.ID
            WHERE A.FUNCIONARIOS_ID = ?
            ORDER BY A.DATA, A.HORARIO
            """,
            (funcionario_id,),
        ).fetchall()

    print("\n--- MINHA AGENDA ---")
    if not agenda:
        print("Nenhum corte agendado.")
    for data_ag, horario, cliente_nome, servico in agenda:
        print(f"{data_ag} | {horario} | Cliente: {cliente_nome} | {servico}")


def menu_funcionario(usuario):
    while True:
        print(f"\n=== FUNCIONÁRIO: {usuario['nome']} ===")
        print("1. Visualizar Agenda | 0. Sair")
        op = input("Escolha: ").strip()
        if op == "1":
            visualizar_agenda(usuario["id"])
        elif op == "0":
            break


# --- ÁREA DO DONO ---

def relatorio_financeiro():
    with conectar() as conn:
        dados = conn.execute(
            """
            SELECT U.NOME, COUNT(A.ID), COALESCE(SUM(S.PRECO), 0)
            FROM USUARIOS U
            LEFT JOIN AGENDAMENTOS A ON U.ID = A.FUNCIONARIOS_ID
            LEFT JOIN SERVICOS S ON A.SERVICOS_ID = S.ID
            WHERE U.PAPEL = 'Funcionario'
            GROUP BY U.ID, U.NOME
            ORDER BY 3 DESC
            """
        ).fetchall()

    print("\n--- RELATÓRIO FINANCEIRO ---")
    total = 0.0
    for nome, cortes, valor in dados:
        total += valor
        print(f"{nome}: {cortes} corte(s) | R$ {valor:.2f}")
    print(f"Lucro total da barbearia: R$ {total:.2f}")


def menu_dono(usuario):
    while True:
        print(f"\n=== DONO: {usuario['nome']} ===")
        print("1. Relatório Financeiro | 2. Cadastrar Equipe | 0. Sair")
        op = input("Escolha: ").strip()
        if op == "1":
            relatorio_financeiro()
        elif op == "2":
            cargo = input("Cargo (1. Funcionario | 2. Dono): ").strip()
            if cargo in ("1", "2"):
                cadastrar_usuario("Funcionario" if cargo == "1" else "Dono")
            else:
                print("Cargo inválido.")
        elif op == "0":
            break


# --- MENU PRINCIPAL ---

def main():
    inicializar_banco()
    while True:
        print("\n=== SISTEMA BARBEARIA ===")
        print("1. Login | 2. Cadastrar-se | 3. Recuperar Senha | 0. Sair")
        op = input("Escolha: ").strip()

        if op == "1":
            usuario = login()
            if usuario:
                if usuario["papel"] == "Cliente":
                    menu_cliente(usuario)
                elif usuario["papel"] == "Funcionario":
                    menu_funcionario(usuario)
                else:
                    menu_dono(usuario)
        elif op == "2":
            cadastrar_usuario("Cliente")
        elif op == "3":
            recuperar_senha()
        elif op == "0":
            break


if __name__ == "__main__":
    main()
