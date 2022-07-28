import face_recognition
import secrets
import random
import faker
import simpy
import json

FOTOS = [
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Jim1.jpg",
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Jim2.jpg",

    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Kevin1.jpg",
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Kevin2.jpg",

    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Michael1.jpg",
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Michael2.jpg",

    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Pam1.jpg",
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Pam2.jpg",

    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Ryan2.jpg",
    "C:/Users/Marcos/Documents/labs/TrabIHM/faces/Ryan2.jpg"
]

CONFIGURACAO = "C:/Users/Marcos/Documents/labs/TrabIHM/configuracao.json"

def preparar():
    global configuracao
    
    global clientes_reconhecidos
    clientes_reconhecidos = {}

    configuracao = None
    with open(CONFIGURACAO, "r") as arquivo_configuracao:
        configuracao = json.load(arquivo_configuracao)
        if configuracao:
            print("Configuracao carregada. ")

    global gerador_dados_falsos
    gerador_dados_falsos = faker.Faker(locale="pt_BR")

def simular_entrada():
    visitante = {
        "foto": random.choice(FOTOS)
    }

    return visitante

def reconhecer_cliente(visitante):
    global configuracao
    global gerador_dados_falsos

    print("Iniciando reconhecimento de cliente...")
    foto_visitante = face_recognition.load_image_file(visitante["foto"])
    encoding_foto_visitante = face_recognition.face_encodings(foto_visitante)[0]

    reconhecido = False
    for cliente in configuracao["clientes"]:
        fotos_banco = cliente["fotos"]
        total_reconhecimentos = 0

        for foto in fotos_banco:
            foto_banco = face_recognition.load_image_file(foto)
            encoding_foto_banco = face_recognition.face_encodings(foto_banco)[0]

            foto_reconhecida = face_recognition.compare_faces([encoding_foto_visitante], encoding_foto_banco)[0]
            if foto_reconhecida:
                total_reconhecimentos += 1

        if total_reconhecimentos/len(fotos_banco) > 0.7:
            reconhecido = True

            visitante["clientes"] = {}
            visitante["clientes"]["nome"] = gerador_dados_falsos.name()
            visitante["clientes"]["pressao"] = random.randint(0, 1)
            visitante["clientes"]["colesterol"] = random.randint(0, 1)

    return reconhecido, visitante

def imprimir_cliente(cliente):
    print("nome:", cliente["clientes"]["nome"])

    if cliente["clientes"]["pressao"] == 1:    
        print("cliente com problema de pressao")
    else:
        print("cliente sem problema de pressao")

    if cliente["clientes"]["colesterol"] == 1:    
        print("cliente com problema de colesterol")
    else:
        print("cliente sem problema de colesterol")

def reconhecer_visitante(env):
    global clientes_reconhecidos

    while True:
        print("Reconhecendo clientes em ciclo/tempo", env.now)

        visitante = simular_entrada()
        reconhecido, cliente = reconhecer_cliente(visitante)
        if reconhecido:
            id_cliente = secrets.token_hex(nbytes=16).upper()
            clientes_reconhecidos[id_cliente] = cliente

            print("Cliente reconhecido: ")
            imprimir_cliente(cliente)

        else:
            print("Cliente não reconhecido.")

        yield env.timeout(100)

def recomendar_cardapio(env):
    global clientes_reconhecidos

    while True:
        if len(clientes_reconhecidos):
            for id_cliente, cliente in list(clientes_reconhecidos.items()):
                if cliente["clientes"]["pressao"] == 1:
                    if cliente["clientes"]["colesterol"] == 1:
                        print("Pratos nao recomendados: X-Burguer, Batata-Frita, Refrigerante.")
                        print("Pratos recomendados: Suco natural, X-Salada.")
                        clientes_reconhecidos.pop(id_cliente)
                    else: 
                        print("Prato nao recomendado: Batata-Frita.")
                        print("Prato recomendado: X-Salada.")
                        clientes_reconhecidos.pop(id_cliente)
                else:
                    if cliente["clientes"]["colesterol"] == 1:
                        print("Pratos nao recomendados: X-Burguer, Refrigerante.")
                        print("Pratos recomendados: Suco natural, X-Salada.")
                        clientes_reconhecidos.pop(id_cliente)
                    else: 
                        print("Nenhuma sugestao")
                        print("Nenhuma sugestao")
                        clientes_reconhecidos.pop(id_cliente)
            yield env.timeout(100)
        else:
            yield env.timeout(1)

if __name__ == "__main__":
    preparar()

    env = simpy.Environment()
    env.process(reconhecer_visitante(env))
    env.process(recomendar_cardapio(env))
    env.run(until=501)