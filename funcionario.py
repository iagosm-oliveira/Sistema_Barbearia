from db import conectar


def visualizar_agenda(funcionario_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT A.DATA, A.HORARIO, C.NOME, S.TIPO
        FROM AGENDAMENTOS A
        JOIN USUARIOS C ON A.CLIENTE_ID = C.ID
        JOIN SERVICOS S ON A.SERVICOS_ID = S.ID
        WHERE A.FUNCIONARIOS_ID = ?
        ORDER BY A.DATA, A.HORARIO
        """,
        (funcionario_id,),
    )
    agendamentos = cursor.fetchall()
    conn.close()

    print("\n--- MINHA AGENDA ---")
    if not agendamentos:
        print("Você não possui cortes agendados.")
        return

    for data_ag, horario, cliente_nome, servico_tipo in agendamentos:
        print(f"{data_ag} | {horario} | Cliente: {cliente_nome} | Serviço: {servico_tipo}")


def menu_funcionario(usuario):
    while True:
        print(f"\n=== ÁREA DO FUNCIONÁRIO ({usuario['nome']}) ===")
        print("1. Visualizar Agenda")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            visualizar_agenda(usuario["id"])
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
