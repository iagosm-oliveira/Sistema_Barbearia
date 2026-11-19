import sqlite3
from hashlib import sha256

DB_NAME = "barbearia.db"


def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USUARIOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOME VARCHAR(100) NOT NULL,
            EMAIL VARCHAR(100) UNIQUE NOT NULL,
            SENHA VARCHAR(255) NOT NULL,
            PAPEL VARCHAR(20) NOT NULL CHECK (PAPEL IN ('Cliente', 'Funcionario', 'Dono'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SERVICOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TIPO VARCHAR(50) NOT NULL CHECK (TIPO IN ('Masculino', 'Feminino')),
            PRECO REAL NOT NULL
        )
    """)

    cursor.execute("""
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

    cursor.execute("SELECT COUNT(*) FROM SERVICOS")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO SERVICOS (ID, TIPO, PRECO) VALUES (1, 'Masculino', 40.00), (2, 'Feminino', 80.00)"
        )

    cursor.execute("SELECT COUNT(*) FROM USUARIOS")
    if cursor.fetchone()[0] == 0:
        senha_padrao = sha256("123".encode("utf-8")).hexdigest()
        usuarios_mock = [
            ("Carlos Dono", "dono@barbearia.com", senha_padrao, "Dono"),
            ("João Barbeiro", "joao@barbearia.com", senha_padrao, "Funcionario"),
            ("Pedro Barbeiro", "pedro@barbearia.com", senha_padrao, "Funcionario"),
            ("Maria Cabeleireira", "maria@barbearia.com", senha_padrao, "Funcionario"),
            ("Ana Cabeleireira", "ana@barbearia.com", senha_padrao, "Funcionario"),
        ]
        cursor.executemany(
            "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, ?)",
            usuarios_mock,
        )

    conn.commit()
    conn.close()
