import sqlite3

from db import conectar
from login import hash_senha


def relatorio_financeiro():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT U.NOME, COUNT(A.ID) AS TOTAL_CORTES, COALESCE(SUM(S.PRECO), 0) AS FATURAMENTO
        FROM USUARIOS U
        LEFT JOIN AGENDAMENTOS A ON U.ID = A.FUNCIONARIOS_ID
        LEFT JOIN SERVICOS S ON A.SERVICOS_ID = S.ID
        WHERE U.PAPEL = 'Funcionario'
        GROUP BY U.ID, U.NOME
        ORDER BY FATURAMENTO DESC
        """
    )
    linhas = cursor.fetchall()
    conn.close()

    print("\n--- RELATÓRIO FINANCEIRO ---")
    if not linhas:
        print("Nenhum funcionário cadastrado.")
        return

    lucro_total = 0.0
    for nome, total_cortes, faturamento in linhas:
        lucro_total += faturamento
        print(f"{nome}: {total_cortes} corte(s) | Faturamento: R$ {faturamento:.2f}")

    print(f"\nLucro total da barbearia: R$ {lucro_total:.2f}")


def cadastrar_equipe():
    print("\n--- CADASTRAR EQUIPE ---")
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ")
    print("Cargo: 1. Funcionario | 2. Dono")
    escolha = input("Escolha (1 ou 2): ").strip()

    if escolha == "1":
        papel = "Funcionario"
    elif escolha == "2":
        papel = "Dono"
    else:
        print("Cargo inválido.")
        return

    if not nome or not email or not senha:
        print("Todos os campos são obrigatórios.")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha(senha), papel),
        )
        conn.commit()
        print(f"{papel} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: este e-mail já está cadastrado.")
    finally:
        conn.close()


def menu_dono(usuario):
    while True:
        print(f"\n=== ÁREA DO DONO ({usuario['nome']}) ===")
        print("1. Relatório Financeiro")
        print("2. Cadastrar Equipe")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            relatorio_financeiro()
        elif opcao == "2":
            cadastrar_equipe()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
