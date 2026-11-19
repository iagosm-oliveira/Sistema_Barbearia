from datetime import date, timedelta

from db import conectar

HORARIOS_PADRAO = [
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
]

DIAS_SEMANA = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]


def obter_dias_trabalho(quantidade=6):
    dias = []
    atual = date.today()
    while len(dias) < quantidade:
        if atual.weekday() != 6:  # Barbearia não abre aos domingos
            dias.append((atual.strftime("%Y-%m-%d"), DIAS_SEMANA[atual.weekday()]))
        atual += timedelta(days=1)
    return dias


def agendar_corte(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT ID, NOME FROM USUARIOS WHERE PAPEL = 'Funcionario'")
    profissionais = cursor.fetchall()
    if not profissionais:
        print("\nNenhum profissional cadastrado no momento.")
        conn.close()
        return

    print("\n--- ESCOLHA O PROFISSIONAL ---")
    for i, prof in enumerate(profissionais, start=1):
        print(f"{i}. {prof[1]}")

    try:
        idx_prof = int(input("Número do profissional: ")) - 1
        profissional = profissionais[idx_prof]
    except (ValueError, IndexError):
        print("Opção inválida.")
        conn.close()
        return

    dias = obter_dias_trabalho()
    print("\n--- DIAS DE TRABALHO DISPONÍVEIS ---")
    for i, (data_str, dia_nome) in enumerate(dias, start=1):
        print(f"{i}. {data_str} ({dia_nome})")

    try:
        idx_dia = int(input("Número do dia: ")) - 1
        data_escolhida = dias[idx_dia][0]
    except (ValueError, IndexError):
        print("Opção inválida.")
        conn.close()
        return

    cursor.execute(
        "SELECT HORARIO FROM AGENDAMENTOS WHERE FUNCIONARIOS_ID = ? AND DATA = ?",
        (profissional[0], data_escolhida),
    )
    ocupados = {linha[0] for linha in cursor.fetchall()}
    livres = [h for h in HORARIOS_PADRAO if h not in ocupados]

    if not livres:
        print("\nNão há horários livres neste dia para esse profissional.")
        conn.close()
        return

    print("\n--- HORÁRIOS LIVRES ---")
    for i, horario in enumerate(livres, start=1):
        print(f"{i}. {horario}")

    try:
        idx_hora = int(input("Número do horário: ")) - 1
        horario_escolhido = livres[idx_hora]
    except (ValueError, IndexError):
        print("Opção inválida.")
        conn.close()
        return

    cursor.execute("SELECT ID, TIPO, PRECO FROM SERVICOS")
    servicos = cursor.fetchall()
    print("\n--- ESCOLHA O SERVIÇO ---")
    for i, serv in enumerate(servicos, start=1):
        print(f"{i}. {serv[1]} - R$ {serv[2]:.2f}")

    try:
        idx_serv = int(input("Número do serviço: ")) - 1
        servico = servicos[idx_serv]
    except (ValueError, IndexError):
        print("Opção inválida.")
        conn.close()
        return

    cursor.execute(
        """
        INSERT INTO AGENDAMENTOS (CLIENTE_ID, SERVICOS_ID, FUNCIONARIOS_ID, DATA, HORARIO)
        VALUES (?, ?, ?, ?, ?)
        """,
        (cliente_id, servico[0], profissional[0], data_escolhida, horario_escolhido),
    )
    conn.commit()
    conn.close()

    print(
        f"\nAgendamento confirmado! {servico[1]} com {profissional[1]} em {data_escolhida} às {horario_escolhido}."
    )


def menu_cliente(usuario):
    while True:
        print(f"\n=== ÁREA DO CLIENTE ({usuario['nome']}) ===")
        print("1. Agendar Corte")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            agendar_corte(usuario["id"])
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
