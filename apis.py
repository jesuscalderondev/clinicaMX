from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from database import *
from functions import *

apis = Blueprint('apis', __name__, url_prefix='/api')

#@requiredSession
@apis.route('/consultar/horario/<string:fecha>')
def consularHorario(fecha):
    intervalo = session.query(DiaTrabajo).filter(DiaTrabajo.fecha == fecha).first()
    if intervalo != None:
        #haciendo pruebas aquí
        horasNoValdasObj = session.query(Turno).filter(Turno.fecha == formatearFecha(fecha), Turno.paciente != "Sin definir").all()
        horasNoValidas = []
        for i in horasNoValdasObj:
            hora = f"{i.hora.hour:02}:{i.hora.minute:02}"
            horasNoValidas.append(hora)
            if i.motivo == 'Embarazo':
                if i.veces == 'Primera vez':
                    tiempoExtra = 30
                else:
                    tiempoExtra = 15

                print(int(tiempoExtra/intervalo.intervalo))
                for hora2 in range(0, int(tiempoExtra/intervalo.intervalo)):
                    horaSrt = datetime.combine(date.today(), i.hora)
                    horaSrt = horaSrt + timedelta(minutes=intervalo.intervalo + (intervalo.intervalo * hora2))
                    horasNoValidas.append(horaSrt.strftime('%H:%M'))
        
        if datetime.strptime(fecha, "%Y-%m-%d").date() != date.today():
            inicio = intervalo.inicio.hour
        else:
            inicio = (datetime.now() + timedelta(hours=1)).time().hour
        #Modificar
        if inicio <= 20:
            horas = crearListaHoras(inicio, 23, intervalo.intervalo, horasNoValidas)
        else:
            horas = []
    else:
        horas = []
    return jsonify(horas = horas)


#@requiredSession
@apis.route('/sala')
def consultarTurnoSala():
    try:
        turnosObj = session.query(Turno).filter(Turno.fecha == date.today(), Turno.asiste == 'Pendiente').order_by(Turno.hora).limit(5).all()
        print(turnosObj)
        turnos = []

        for turno in turnosObj:
            if turno != None:
                turnos.append({
                    'codigo' : f'C1-{turno.id}',
                    'texto' : f'{turno.paciente}'
                })
        
        return jsonify(turnos = turnos, mensaje = 'joaaa')
    except Exception as e:
        return jsonify(turnos = [], error = f'{e}')


#@requiredSession
@apis.route('/videos')
def videos():
    videosObj = session.query(Video).all()
    videos = []

    for i in videosObj:
        videos.append({'src' : i.ruta})
    
    return jsonify(videos = videos)

def convertirTurnoJson(Cita:Turno):
    return {'paciente' : Cita.paciente, 'deriva' : Cita.deriva, 'fecha' : f'{Cita.fecha}', 'hora' : f'{Cita.hora}', 'localidad' : Cita.localidad, 'id' : Cita.id}

