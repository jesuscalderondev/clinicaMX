from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime

def passwordHash(password:str):
    return generate_password_hash(password)

def passwordVerify(passHash:str, passUnHashed):
    return check_password_hash(passHash, passUnHashed)

def toJson(objetc):
    if hasattr(objetc, "__dict__"):
        json = {}
        for atributo in objetc.__dict__.keys():           
            json[atributo] = getattr(objetc, atributo)
        return json
    else:
        return {}


def obtenerHoraCita(fecha:str):
    try:
        #Reemplazar
        local = 'http://127.0.0.1:5000'
        response = requests.get(f'{local}/api/consultar/horario/{fecha.replace("/", "-")}')
        try:
            hora = response.json()['horas']
            print(hora, "Hoaaa")
            return hora
        except Exception as e:
            print("Error en el primero")
            print(e)
            return None
    except Exception as e:
        print("Error en el segundo")
        print(e)
        return None

def formatearFecha(fechaStr):
    formatos = ["%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    contador = 0
    while contador < 4:
        try:
            fecha = datetime.strptime(fechaStr, formatos[contador])
            return fecha
        except:
            contador+=1
    
    return ExceptionGroup