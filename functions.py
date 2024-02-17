from werkzeug.security import generate_password_hash, check_password_hash
from flask import session as cookies
from apscheduler.schedulers.background import BackgroundScheduler
import requests

programador = BackgroundScheduler()

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



def requiredSession(f):
    def decorated(*args, **kwargs):
        if 'token' not in cookies:
            raise ValueError('Se requiere una sesión activa para ver la información')
        return f(*args, **kwargs)
    return decorated


def crearListaHoras(inicio, fin, intervalo, horasNoValdas):
    horas = []
    for hora in range(inicio, fin+1):
        for a in range(0, 60, intervalo):
            horaf = f"{hora:02}:{a:02}"
            if horaf not in horasNoValdas:
                horas.append(horaf)
    #Modificar
    """ if(horas[-1] == '15:45' or horas[-1][:2] == '16'):
        horas.pop() """
    return horas

def obtenerHoraCita(fecha:str):
    try:
        rutaHost = 'https://clinicamx-dev-efpc.2.us-1.fl0.io'
        rutaLocal = 'http://127.0.0.1:8080'
        response = requests.get(f'{rutaLocal}/api/consultar/horario/{fecha.replace("/", "-")}')
        try:
            hora = response.json()['horas']
            return hora
        except Exception as e:
            print("Error en el primero")
            print(e)
            return None
    except Exception as e:
        print("Error en el segundo")
        print(e)
        return None
