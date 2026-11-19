#!/usr/bin/env python3
import random
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from cliente import HORARIOS_PADRAO, obter_dias_trabalho
from db import conectar, inicializar_banco
from login import enviar_email_codigo, hash_senha

janela = tk.Tk()
janela.title("Sistema Barbearia")
janela.geometry("420x480")


def limpar_tela():
    for widget in janela.winfo_children():
        widget.destroy()


# --- ACESSO GERAL (SEM LOGIN) ---

def tela_inicial():
    limpar_tela()
    tk.Label(janela, text="Sistema Barbearia", font=("Arial", 16, "bold")).pack(pady=20)

    tk.Button(janela, text="Fazer Login", width=25, command=tela_login).pack(pady=5)
    tk.Button(janela, text="Cadastrar-se (Cliente)", width=25, command=tela_cadastro_cliente).pack(pady=5)
    tk.Button(janela, text="Recuperar Senha", width=25, command=tela_recuperar_senha).pack(pady=5)
    tk.Button(janela, text="Sair", width=25, command=janela.quit).pack(pady=20)


def tela_login():
    limpar_tela()
    tk.Label(janela, text="Login", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(janela, text="Email:").pack()
    ent_email = tk.Entry(janela, width=30)
    ent_email.pack(pady=5)

    tk.Label(janela, text="Senha:").pack()
    ent_senha = tk.Entry(janela, width=30, show="*")
    ent_senha.pack(pady=5)

    def entrar():
        email = ent_email.get().strip()
        senha = ent_senha.get()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, NOME, PAPEL FROM USUARIOS WHERE EMAIL = ? AND SENHA = ?",
            (email, hash_senha(senha)),
        )
        res = cursor.fetchone()
        conn.close()

        if not res:
            messagebox.showerror("Erro", "Email ou senha inválidos.")
            return

        usuario = {"id": res[0], "nome": res[1], "papel": res[2]}
        if usuario["papel"] == "Cliente":
            tela_cliente(usuario)
        elif usuario["papel"] == "Funcionario":
            tela_funcionario(usuario)
        elif usuario["papel"] == "Dono":
            tela_dono(usuario)

    tk.Button(janela, text="Entrar", width=20, command=entrar).pack(pady=15)
    tk.Button(janela, text="Voltar", width=20, command=tela_inicial).pack()


def tela_cadastro_cliente():
    limpar_tela()
    tk.Label(janela, text="Cadastro de Cliente", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(janela, text="Nome completo:").pack()
    ent_nome = tk.Entry(janela, width=30)
    ent_nome.pack(pady=5)

    tk.Label(janela, text="Email:").pack()
    ent_email = tk.Entry(janela, width=30)
    ent_email.pack(pady=5)

    tk.Label(janela, text="Senha:").pack()
    ent_senha = tk.Entry(janela, width=30, show="*")
    ent_senha.pack(pady=5)

    def salvar():
        nome = ent_nome.get().strip()
        email = ent_email.get().strip()
        senha = ent_senha.get()

        if not nome or not email or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        conn = conectar()
        try:
            conn.execute(
                "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, 'Cliente')",
                (nome, email, hash_senha(senha)),
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            tela_inicial()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Este e-mail já está cadastrado.")
        finally:
            conn.close()

    tk.Button(janela, text="Cadastrar", width=20, command=salvar).pack(pady=15)
    tk.Button(janela, text="Voltar", width=20, command=tela_inicial).pack()


def tela_recuperar_senha():
    limpar_tela()
    tk.Label(janela, text="Recuperar Senha", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(janela, text="Digite seu e-mail cadastrado:").pack()
    ent_email = tk.Entry(janela, width=30)
    ent_email.pack(pady=5)

    def enviar():
        email = ent_email.get().strip()
        conn = conectar()
        usuario = conn.execute("SELECT ID FROM USUARIOS WHERE EMAIL = ?", (email,)).fetchone()
        conn.close()

        if not usuario:
            messagebox.showerror("Erro", "E-mail não encontrado.")
            return

        codigo = str(random.randint(100000, 999999))
        if not enviar_email_codigo(email, codigo):
            messagebox.showerror("Erro", "Falha ao enviar o e-mail.")
            return

        messagebox.showinfo("Enviado", "Código enviado para o seu e-mail!")

        tela_confirmar_codigo(email, codigo)

    tk.Button(janela, text="Enviar Código", width=20, command=enviar).pack(pady=15)
    tk.Button(janela, text="Voltar", width=20, command=tela_inicial).pack()


def tela_confirmar_codigo(email, codigo_correto):
    limpar_tela()
    tk.Label(janela, text="Redefinir Senha", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(janela, text="Código recebido:").pack()
    ent_codigo = tk.Entry(janela, width=30)
    ent_codigo.pack(pady=5)

    tk.Label(janela, text="Nova senha:").pack()
    ent_senha = tk.Entry(janela, width=30, show="*")
    ent_senha.pack(pady=5)

    def redefinir():
        if ent_codigo.get().strip() != codigo_correto:
            messagebox.showerror("Erro", "Código inválido.")
            return

        nova_senha = ent_senha.get()
        if not nova_senha:
            messagebox.showwarning("Aviso", "Digite a nova senha.")
            return

        conn = conectar()
        conn.execute(
            "UPDATE USUARIOS SET SENHA = ? WHERE EMAIL = ?",
            (hash_senha(nova_senha), email),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!")
        tela_inicial()

    tk.Button(janela, text="Salvar Nova Senha", width=20, command=redefinir).pack(pady=15)
    tk.Button(janela, text="Cancelar", width=20, command=tela_inicial).pack()


# --- ÁREA DO CLIENTE ---

def tela_cliente(usuario):
    limpar_tela()
    tk.Label(janela, text=f"Cliente: {usuario['nome']}", font=("Arial", 14, "bold")).pack(pady=10)

    conn = conectar()
    profissionais = conn.execute("SELECT ID, NOME FROM USUARIOS WHERE PAPEL = 'Funcionario'").fetchall()
    servicos = conn.execute("SELECT ID, TIPO, PRECO FROM SERVICOS").fetchall()
    conn.close()

    if not profissionais:
        tk.Label(janela, text="Nenhum profissional cadastrado no momento.").pack(pady=20)
        tk.Button(janela, text="Sair", width=20, command=tela_inicial).pack()
        return

    dias = obter_dias_trabalho()

    tk.Label(janela, text="Profissional:").pack()
    cb_prof = ttk.Combobox(janela, state="readonly", width=28, values=[p[1] for p in profissionais])
    cb_prof.current(0)
    cb_prof.pack(pady=5)

    tk.Label(janela, text="Dia de trabalho:").pack()
    cb_dia = ttk.Combobox(janela, state="readonly", width=28, values=[f"{d[0]} ({d[1]})" for d in dias])
    cb_dia.current(0)
    cb_dia.pack(pady=5)

    tk.Label(janela, text="Horário livre:").pack()
    cb_hora = ttk.Combobox(janela, state="readonly", width=28)
    cb_hora.pack(pady=5)

    tk.Label(janela, text="Serviço:").pack()
    cb_serv = ttk.Combobox(
        janela, state="readonly", width=28, values=[f"{s[1]} - R$ {s[2]:.2f}" for s in servicos]
    )
    cb_serv.current(0)
    cb_serv.pack(pady=5)

    def atualizar_horarios(*args):
        prof_id = profissionais[cb_prof.current()][0]
        data_escolhida = dias[cb_dia.current()][0]

        conn = conectar()
        ocupados = {
            r[0]
            for r in conn.execute(
                "SELECT HORARIO FROM AGENDAMENTOS WHERE FUNCIONARIOS_ID = ? AND DATA = ?",
                (prof_id, data_escolhida),
            ).fetchall()
        }
        conn.close()

        livres = [h for h in HORARIOS_PADRAO if h not in ocupados]
        cb_hora["values"] = livres
        cb_hora.set(livres[0] if livres else "Sem horários livres")

    cb_prof.bind("<<ComboboxSelected>>", atualizar_horarios)
    cb_dia.bind("<<ComboboxSelected>>", atualizar_horarios)
    atualizar_horarios()

    def confirmar():
        horario = cb_hora.get()
        if not horario or horario == "Sem horários livres":
            messagebox.showwarning("Aviso", "Escolha um dia com horário livre.")
            return

        prof = profissionais[cb_prof.current()]
        data_escolhida = dias[cb_dia.current()][0]
        serv = servicos[cb_serv.current()]

        conn = conectar()
        conn.execute(
            "INSERT INTO AGENDAMENTOS (CLIENTE_ID, SERVICOS_ID, FUNCIONARIOS_ID, DATA, HORARIO) VALUES (?, ?, ?, ?, ?)",
            (usuario["id"], serv[0], prof[0], data_escolhida, horario),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Confirmado",
            f"Corte agendado!\n{serv[1]} com {prof[1]}\nData: {data_escolhida} às {horario}",
        )
        atualizar_horarios()

    tk.Button(janela, text="Confirmar Agendamento", width=22, command=confirmar).pack(pady=15)
    tk.Button(janela, text="Sair", width=22, command=tela_inicial).pack()


# --- ÁREA DO FUNCIONÁRIO ---

def tela_funcionario(usuario):
    limpar_tela()
    tk.Label(janela, text=f"Agenda: {usuario['nome']}", font=("Arial", 14, "bold")).pack(pady=10)

    conn = conectar()
    agendamentos = conn.execute(
        """
        SELECT A.DATA, A.HORARIO, C.NOME, S.TIPO
        FROM AGENDAMENTOS A
        JOIN USUARIOS C ON A.CLIENTE_ID = C.ID
        JOIN SERVICOS S ON A.SERVICOS_ID = S.ID
        WHERE A.FUNCIONARIOS_ID = ?
        ORDER BY A.DATA, A.HORARIO
        """,
        (usuario["id"],),
    ).fetchall()
    conn.close()

    lista = tk.Listbox(janela, width=55, height=14)
    lista.pack(pady=10, padx=10)

    if not agendamentos:
        lista.insert(tk.END, "Nenhum corte agendado.")
    else:
        for data_ag, horario, cliente_nome, servico_tipo in agendamentos:
            lista.insert(tk.END, f"{data_ag} | {horario} | {cliente_nome} ({servico_tipo})")

    tk.Button(janela, text="Sair", width=20, command=tela_inicial).pack(pady=10)


# --- ÁREA DO DONO ---

def tela_dono(usuario):
    limpar_tela()
    tk.Label(janela, text=f"Dono: {usuario['nome']}", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Button(janela, text="Relatório Financeiro", width=25, command=lambda: tela_relatorio(usuario)).pack(pady=5)
    tk.Button(janela, text="Cadastrar Equipe", width=25, command=lambda: tela_cadastrar_equipe(usuario)).pack(pady=5)
    tk.Button(janela, text="Sair", width=25, command=tela_inicial).pack(pady=20)


def tela_relatorio(usuario):
    limpar_tela()
    tk.Label(janela, text="Relatório Financeiro", font=("Arial", 14, "bold")).pack(pady=10)

    conn = conectar()
    linhas = conn.execute(
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
    conn.close()

    lista = tk.Listbox(janela, width=50, height=12)
    lista.pack(pady=10, padx=10)

    lucro_total = 0.0
    if not linhas:
        lista.insert(tk.END, "Nenhum funcionário cadastrado.")
    else:
        for nome, total_cortes, faturamento in linhas:
            lucro_total += faturamento
            lista.insert(tk.END, f"{nome}: {total_cortes} corte(s) | R$ {faturamento:.2f}")

    tk.Label(janela, text=f"Lucro Total: R$ {lucro_total:.2f}", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Button(janela, text="Voltar", width=20, command=lambda: tela_dono(usuario)).pack(pady=10)


def tela_cadastrar_equipe(usuario):
    limpar_tela()
    tk.Label(janela, text="Cadastrar Equipe", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(janela, text="Nome completo:").pack()
    ent_nome = tk.Entry(janela, width=30)
    ent_nome.pack(pady=5)

    tk.Label(janela, text="Email:").pack()
    ent_email = tk.Entry(janela, width=30)
    ent_email.pack(pady=5)

    tk.Label(janela, text="Senha:").pack()
    ent_senha = tk.Entry(janela, width=30, show="*")
    ent_senha.pack(pady=5)

    tk.Label(janela, text="Cargo:").pack()
    cb_cargo = ttk.Combobox(janela, state="readonly", width=28, values=["Funcionario", "Dono"])
    cb_cargo.current(0)
    cb_cargo.pack(pady=5)

    def salvar():
        nome = ent_nome.get().strip()
        email = ent_email.get().strip()
        senha = ent_senha.get()
        papel = cb_cargo.get()

        if not nome or not email or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        conn = conectar()
        try:
            conn.execute(
                "INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES (?, ?, ?, ?)",
                (nome, email, hash_senha(senha), papel),
            )
            conn.commit()
            messagebox.showinfo("Sucesso", f"{papel} cadastrado com sucesso!")
            tela_dono(usuario)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Este e-mail já está cadastrado.")
        finally:
            conn.close()

    tk.Button(janela, text="Cadastrar", width=20, command=salvar).pack(pady=15)
    tk.Button(janela, text="Voltar", width=20, command=lambda: tela_dono(usuario)).pack()


if __name__ == "__main__":
    inicializar_banco()
    tela_inicial()
    janela.mainloop()
