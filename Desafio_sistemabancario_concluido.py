import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
from pathlib import Path

ROOT_PATH = Path(__file__).parent

class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 3:
            print("\n!!! Você excedeu o número de transações permitida para hoje! !!!")
            return
        
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.nome}', '{self.cpf}')>"


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n!!! Falha no sistema! Você não tem saldo suficiente. !!!")

        elif valor > 0:
            self._saldo -= valor
            print("\n--- Saque realizado com sucesso! ---")
            return True

        else:
            print("\n!!! Falha no sistema! O valor informado é inválido. !!!")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n--- Depósito realizado com sucesso! ---")
        else:
            print("\n!!! Falha no sistema! O valor informado é inválido. !!!")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n!!! Falha no sistema! Você excedeu o valor limite de saque. !!!")

        elif excedeu_saques:
            print("\n!!! Falha no sistema! Você excedeu o número máximo de saques diário. !!!")

        else:
            return super().sacar(valor)

        return False
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self):
        data_atual = datetime.utcnow().date()
        transacoes = []
        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ROOT_PATH / "log.txt", "a") as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__}' executada com argumentos {args} e {kwargs}. "
                f"Retornou {resultado}\n"
            )
        return resultado

    return envelope


def menu():
    menu = """\n
    ---------- MENU ----------
    [u]\tNovo usuário
    [c]\tNova conta
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [l]\tListar contas
    [t]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n!!! Cliente não possui conta! !!!")
        return

    return cliente.contas[0]


@log_transacao
def depositar(clientes):
    cpf = input("Informe seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Cliente não encontrado! !!!")
        return

    valor = float(input("Informe o valor que deseja depósitar: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Cliente não encontrado! !!!")
        return

    valor = float(input("Informe o valor que deseja sacar: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Cliente não encontrado! !!!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n--------------EXTRATO --------------")
    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("--------------------------------------")


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe seu CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n!!! Já existe cliente com esse CPF! !!!")
        return

    nome = input("Informe seu nome completo: ")
    data_nascimento = input("Informe sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe seu endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n--- Cliente criado com sucesso! ---")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!! Cliente não foi encontrado, fluxo de criação de conta encerrado! !!!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, limite_saques=50)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n--- Conta criada com sucesso! ---")


def listar_contas(contas):
    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "u":
            criar_cliente(clientes)

        elif opcao == "c":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "t":
            break

        else:
            print("\n!!! Falha no sistema, por favor selecione novamente a operação desejada. !!!")

main()

