from flask import render_template, Blueprint, redirect, request, flash
from datetime import date, timedelta, time, timezone
from flask_bootstrap import Bootstrap


from database import *
from functions import *

turnos = Blueprint('turnos', __name__, url_prefix='/turnos')

#@requiredSession
@turnos.route('/registrar', methods=['POST', 'GET'])
def registrarTurno():
    if request.method == 'POST':
        try:
            data = request.form
            
            hora = data['hora']
            fecha = data['fecha']
            motivo = data['motivo']
            paciente = data['paciente']
            veces = data['veces']
            deriva = data['deriva']
            edad = data['edad']
            localidad = data['localidad']

            nuevoTurno = Turno(fecha, hora, motivo, paciente, edad, localidad, veces, deriva)
            session.add(nuevoTurno)
            session.commit()
            flash(f'Turno registrado de manera exitosa, codigo de turno {nuevoTurno.id}')
        except Exception as e:
            flash(e)
            session.rollback()
            flash('El turno no pudo ser creado, selecciona una fecha válida')
    hoy = date.today()
    return render_template('/turnos/registrar.html', fechaMin = hoy , fechaMax = hoy + timedelta(days=2))

#@requiredSession
@turnos.route('/hoy')
def verTurnosHoy():
    return render_template('/turnos/turnos.html', turnos = session.query(Turno).filter(Turno.fecha == date.today(), Turno.asiste == 'Pendiente').order_by(Turno.hora.asc()).all())

#@requiredSession
@turnos.route('/cancelar')
def cancelarTurno():
    return render_template('/turnos/cancelar.html', turnos = session.query(Turno).filter(Turno.fecha == date.today(), Turno.asiste == 'Pendiente').order_by(Turno.hora.asc()).all())

#@requiredSession
@turnos.route('/cancelar/<int:id>')
def cancelarTurnoId(id):
    try:
        turno = session.get(Turno, id)
        session.delete(turno)
        session.commit()
        flash('Turno cancelado de manera exitosa')
    except Exception as e:
        flash(e)
        session.rollback()
    
    finally:
        return redirect('/turnos/cancelar')

#@requiredSession
@turnos.route('/sala')
def salaDeEspera():
    return render_template('/turnos/pantallaEspera.html')

#@requiredSession
@turnos.route('/listar/atendidos')
def listarAtendidos():
    return render_template('/turnos/atendidos.html', turnos = session.query(Turno).filter(Turno.fecha == date.today(), Turno.asiste != 'Pendiente').order_by(Turno.hora.asc()).all())

#@requiredSession
@turnos.route('/cambiar/asistencia/<int:cita>')
def cambiarAsistencia(cita):
    try:
        turno = session.get(Turno, cita)
        estados = ['No asistió', 'Asistió']
        estado = estados.index(turno.asiste)
        turno.asiste = estados[estado-1]
        session.add(turno)
        session.commit()
        flash('Asistencia actualizada')
    except:
        flash('La cita seleccionada no existe')

    return redirect('/turnos/listar/atendidos')

#@requiredSession
@turnos.route('/asiste/<int:cita>')
def asiste(cita):
    try:
        turno = session.get(Turno, cita)

        if turno.asiste not in ['No asistió', 'Asistió']:
            turno.asiste = 'Asistió'
            session.add(turno)
            session.commit()
            flash('Turno despachado')
    except:
        flash('La cita seleccionada no existe')

    return redirect('/turnos/hoy')

#@requiredSession
@turnos.route('/noAsiste/<int:cita>')
def noAsiste(cita):
    try:
        turno = session.get(Turno, cita)

        if turno.asiste not in ['No asistió', 'Asistió']:
            turno.asiste = 'No asistió'
            session.add(turno)
            session.commit()
            flash('Turno despachado')
    except:
        flash('La cita seleccionada no existe')

    return redirect('/turnos/hoy')