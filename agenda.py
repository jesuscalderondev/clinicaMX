from flask import Blueprint
from flask import request, render_template, flash, redirect
from datetime import timedelta

import traceback
from database import *
from functions import *

agenda = Blueprint('agenda', __name__, url_prefix='/agenda')

@agenda.route("/cambiar")
def cambiarAgenda():
    if request.method == 'POST':

        try:
            data = request.form

            fecha = data['fecha']
            inicio = data['inicio']
            fin = data['fin']
            intervalo = data['intervalo']

            laborable = 'laborable' not in data

            nuevo = session.query(DiaTrabajo).filter(DiaTrabajo.fecha == fecha).first()

            if nuevo != None:
                if laborable and inicio != "" and fin != "" and intervalo != "":
                    nuevo.inicio = datetime.strptime(inicio, "%H:%M").time()
                    nuevo.fin = datetime.strptime(fin, "%H:%M").time()
                    nuevo.intervalo = intervalo
                nuevo.laborable = laborable
            else:
                if laborable:
                    nuevo = DiaTrabajo(fecha, intervalo, inicio, fin)
                else:
                    nuevo = DiaTrabajo(fecha, 15, datetime.now().time(), datetime.now().time())
                nuevo.laborable = laborable
            
            session.add(nuevo)
            session.commit()

            flash('Se ha actualizado de manera correcta la fecha para trabajo')
        except Exception as e:
            flash(e)
            print(e)
            session.rollback()
            flash('Ha ocurrido un error a la hora de modificar la fecha')
    return render_template('agenda.html', fechaMin = date.today() + timedelta(days=3))


def reprogramar(turno:Turno):
    
    
    dia = 1
    while True:
        fecha = turno.fecha + timedelta(days=dia)
        fechaStr = fecha.strftime('%Y-%m-%d')
        print(fechaStr)

        diaTrabajo = session.query(DiaTrabajo).filter(DiaTrabajo.fecha == fechaStr, DiaTrabajo.laborable == True).first()
        if diaTrabajo != None:
            print(diaTrabajo.fecha)
            
            horasNoValdasObj = session.query(Turno).filter(Turno.fecha == fecha, Turno.paciente != "Sin definir").all()

            horasNoValidas = ["11:00", "11:15", "11:20"]
            for i in horasNoValdasObj:
                hora = f"{i.hora.hour:02}:{i.hora.minute:02}"
                horasNoValidas.append(hora)
                if i.motivo == 'Embarazo':
                    if i.veces == 'Primera vez':
                        tiempoExtra = 30
                    else:
                        tiempoExtra = 15

                    for hora2 in range(0, int(tiempoExtra/diaTrabajo.intervalo)):
                        horaSrt = datetime.combine(date.today(), i.hora)
                        horaSrt = horaSrt + timedelta(minutes=diaTrabajo.intervalo + (diaTrabajo.intervalo * hora2))
                        horasNoValidas.append(horaSrt.strftime('%H:%M'))
            
            lista = crearListaHoras(diaTrabajo.inicio.hour, diaTrabajo.fin.hour, diaTrabajo.intervalo, horasNoValidas)
            
            print(lista)
            if turno.hora.strftime('%H:%M') in lista:
                turno.fecha = fecha
                turno.condicion = "Reagendado"
                session.add(turno)
                session.commit()
                break

        dia+=1

    return fechaStr

@agenda.route("/reprogramar")
def vistaReprogramar():
    citas = session.query(Turno).filter(Turno.paciente != "Sin definir").order_by(Turno.fecha.desc(), Turno.id.desc()).all()
    return render_template("/turnos/turnosPendientes.html", citas=citas)

@agenda.route("/reprogramar/<int:id>", methods=["GET"])
def reprogramarCita(id):
    try:
        cita = session.get(Turno, id)
        fecha = reprogramar(cita)
        flash(f"La nueva fecha de su cita es {fecha} a las {str(cita.hora)[:5]}")
        return redirect('/agenda/reprogramar')
    except Exception as e:
        print(traceback.extract_tb(e.__traceback__))
        return "Error a la hora de reagendar, esta cita fue eliminada anteriormente"