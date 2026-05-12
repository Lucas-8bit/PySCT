import time
import sys
import sqlite3
import os
from datetime import datetime

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def mensagem_temporaria():
    mensagem = "PySCT"
    sys.stdout.write(mensagem)
    sys.stdout.flush()
    time.sleep(1) 
    sys.stdout.write("\r" + " " * len(mensagem) + "\r")
    sys.stdout.flush()


def inicia_banco_de_dados():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                          (usuario TEXT PRIMARY KEY, senha TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           usuario_vinculado TEXT, 
                           operacao TEXT, 
                           data TEXT,
                           FOREIGN KEY (usuario_vinculado) REFERENCES usuarios (usuario))''')
        conn.commit()


def cadastrar_usuario(usuario, senha):
    try:
        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
            print(f"\nUsuário {usuario} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\nErro: Este usuário já existe.")


def salvar_calculo(usuario, operacao):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historico (usuario_vinculado, operacao, data) VALUES (?, ?, ?)", 
                       (usuario, operacao, data_atual))
        conn.commit()


def exibir_historico(usuario_logado):
    limpar_tela()
    print(f"=== HISTÓRICO DE {usuario_logado.upper()} ===")
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT operacao, data FROM historico WHERE usuario_vinculado = ?", (usuario_logado,))
        registros = cursor.fetchall()

    if not registros:
        print("Nenhum cálculo encontrado.")
    else:
        for i, reg in enumerate(registros, 1):
            print(f"{i}. [{reg[1]}] {reg[0]}")
    
    print("\n[1] Voltar para Calculadora | [2] Apagar Histórico")
    opt = input("Escolha: ")
    if opt == '2':
        limpar_historico(usuario_logado)


def limpar_historico(usuario_logado):
    confirmar = input(f"Tem certeza que deseja apagar o histórico de {usuario_logado}? (s/n): ").lower()
    if confirmar == 's':
        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM historico WHERE usuario_vinculado = ?", (usuario_logado,))
            conn.commit()
        print("Histórico deletado com sucesso!")
        time.sleep(1)


def calculadora(usuario_logado):
    while True:
        limpar_tela()
        print("=====================================")
        print(f"      PySCT     - Usuário: {usuario_logado}")
        print("=====================================")
        print(" 1. Realizar Cálculo")
        print(" 2. Ver Histórico / Excluir")
        print(" 3. Sair")
        print("=====================================")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            limpar_tela()
            print("--- NOVA OPERAÇÃO ---")
            try:
                num1 = float(input("Digite o primeiro número: "))
                num2 = float(input("Digite o segundo número: "))
                operador = input("Digite o operador (+, -, *, /, **): ")

                if operador == '+': 
                    resultado = num1 + num2
                elif operador == '-': 
                    resultado = num1 - num2
                elif operador == '*': 
                    resultado = num1 * num2
                elif operador == '**':
                    try:
                        # Limitar o tamanho do expoente para evitar overflow
                        if abs(num2) > 1000:
                            print(f"\nErro: Expoente {num2} é muito grande.")
                            print("Use expoentes entre -1000 e 1000.")
                            time.sleep(6)
                            continue
                        
                        # Verificar se o resultado seria extremamente grande
                        if abs(num1) > 1 and abs(num2) > 100:
                            # Estimar o tamanho do resultado
                            import math
                            tamanho_estimado = abs(num2) * math.log10(abs(num1))
                            if tamanho_estimado > 10000:
                                print(f"\nErro: O resultado teria aproximadamente {int(tamanho_estimado)} dígitos.")
                                print("Isso é muito grande para ser calculado.")
                                print("Use números menores para operações de exponenciação.")
                                time.sleep(3)
                                continue
                        
                        resultado = num1 ** num2
                    except OverflowError:
                        print("\nErro: O resultado da exponenciação é muito grande para ser calculado.")
                        print("Tente usar números menores.")
                        time.sleep(2)
                        continue
                elif operador == '/':
                    if num2 != 0: 
                        resultado = num1 / num2
                    else: 
                        print("\nErro: Divisão por zero!")
                        time.sleep(1)
                        continue
                else:
                    print("\nOperador inválido.")
                    print("Operadores permitidos: +, -, *, /, **")
                    time.sleep(1)
                    continue

                texto_operacao = f"{num1} {operador} {num2} = {resultado}"
                print(f"\n>>> Resultado: {resultado}")
                salvar_calculo(usuario_logado, texto_operacao)
                input("\nPressione Enter para continuar...")
                
            except ValueError:
                print("\nErro: Digite apenas números válidos.")
                time.sleep(1)
            except Exception as e:
                print(f"\nErro inesperado: {e}")
                time.sleep(1)

        elif escolha == '2':
            exibir_historico(usuario_logado)
        
        elif escolha == '3':
            print("\nSaindo do PySCT...")
            print("Obrigado por usar a calculadora!")
            time.sleep(1)
            break
        
        else:
            print("\nOpção inválida! Escolha 1, 2 ou 3.")
            time.sleep(1)


def login():
    inicia_banco_de_dados()
    mensagem_temporaria()
    
    while True:
        limpar_tela()
        print("\n=====================================")
        print("         PySCT - CALCULADORA")
        print("=====================================")
        print("\n--- TELA DE LOGIN ---")
        user_input = input("Usuário: ")
        pass_input = input("Senha: ")

        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (user_input, pass_input))
            resultado = cursor.fetchone()

        if resultado:
            print(f"\n✓ Acesso concedido! Bem-vindo, {user_input}.")
            time.sleep(1)
            calculadora(user_input) 
            break
        else:
            print("\n✗ Usuário ou senha incorretos.")
            opcao = input("\nDeseja tentar novamente (T) ou cadastrar (C)? ").upper()
            if opcao == 'C':
                print("\n--- CADASTRO DE NOVO USUÁRIO ---")
                novo_user = input("Escolha um nome de usuário: ")
                nova_senha = input("Escolha uma senha: ")
                cadastrar_usuario(novo_user, nova_senha)
                print("\nAguarde...")
                time.sleep(2)
            elif opcao != 'T':
                print("\nEncerrando programa...")
                time.sleep(1)
                break


if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
        time.sleep(1)
    except Exception as e:
        print(f"\nErro fatal: {e}")
        time.sleep(2)