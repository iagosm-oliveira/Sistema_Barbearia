from cliente import menu_cliente
from db import inicializar_banco
from dono import menu_dono
from funcionario import menu_funcionario
from login import cadastrar_cliente, login, recuperar_senha


def main():
    inicializar_banco()

    while True:
        print("\n=== SISTEMA BARBEARIA ===")
        print("1. Fazer Login")
        print("2. Cadastrar-se")
        print("3. Recuperar Senha")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            usuario = login()
            if usuario:
                if usuario["papel"] == "Cliente":
                    menu_cliente(usuario)
                elif usuario["papel"] == "Funcionario":
                    menu_funcionario(usuario)
                elif usuario["papel"] == "Dono":
                    menu_dono(usuario)
        elif opcao == "2":
            cadastrar_cliente()
        elif opcao == "3":
            recuperar_senha()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
