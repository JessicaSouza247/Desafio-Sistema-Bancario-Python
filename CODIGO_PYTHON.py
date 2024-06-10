Menu = """
 
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [0] Sair

=> """

Saldo = 0
Limite = 500
Extrato = ""
Número_saque = 0
LIMITE_SAQUE = 3

while True:

    opção = input(Menu)
    
    if opção == "1":
        Valor = float(input("Informe o valor que deseja depositar: "))

        if Valor > 0:
            Saldo += Valor
            Extrato += f"Depósito: R$ {Valor:.2f}\n"

        else:
            print("Falha no depósito! O valor é inválido.")

    elif opção == "2":
        Valor = float(input("Informe o valor que deseja sacar: "))
    
        Excedeu_saldo = Valor > Saldo
        Excedeu_limite = Valor > Limite
        Excedeu_saque = Número_saque >= LIMITE_SAQUE
    
        if Excedeu_saldo:
            print("Falha no saque! Você não tem saldo suficiente.")
        
        elif Excedeu_limite:
            print("Falha no saque! O valor de saque excedeu o limite")
        
        elif Excedeu_saque:
            print("Falha no saque! Você excedeu o limite de saques diários.")

        elif Valor > 0: 
            Saldo -= Valor
            Extrato += f"Saque: R$ {Valor:.2f}\n"
            Número_saque += 1

        else:
            print("Falha no saque! O valor informado é inválido.")

    elif opção == "3":
        print("\n -------- EXTRATO --------")
        print("Não foram realizadas movimentações!" if not Extrato else Extrato)
        print(f"\n Saldo: R$ {Saldo:.2f}")
        print("--------------------------")


    elif opção == "0":
        break

    else:
        print ("Operação inválida, por favor selecione novamente a opção desejada.")
    
