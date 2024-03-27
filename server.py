from flask import Flask, render_template, request, redirect, flash
from flask import session as cookies
from flask_cors import CORS
from os import getenv
from dotenv import load_dotenv
from datetime import timedelta, timezone
from werkzeug.utils import secure_filename
import os
import pytz

from database import *
from functions import *

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

CORS(app, origins=['*'], supports_credentials=True)

#programador.add_job(saludar, 'cron', hour=20, minute=50, second=45, args=['holaaa'])

def agendar():
    for i in range(7):
        try:
            nuevaAgenda = DiaTrabajo(datetime.strftime(datetime.now() + timedelta(days=i), '%Y-%m-%d'), 15, '8:30', '13:30')
            session.add(nuevaAgenda)
            session.commit()
        except Exception as e:
            print("Error: ", e)
            session.rollback()

@app.route('/')
def index():
    agendar()
    if 'token' in cookies:
        return redirect('/home')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.form

    nombreUsuario = data['username']
    clave = data['password']

    try:
        usuario = session.query(Usuario).filter(Usuario.nombreUsuario == nombreUsuario).first()
        if passwordVerify(usuario.clave, clave):
            cookies['token'] = usuario.id
            return redirect('/home')
        else:
            flash("El usuario no existe")
            return redirect('/')
    except Exception as e:
        flash(e)
        return redirect('/')
    

#@requiredSession
@app.route('/home')
def home():
        agendar()
        return render_template('inicio.html', fecha = datetime.now())

#@requiredSession
@app.route("/subir_video", methods=["POST", "GET"])
def subir_video():

    if request.method == "POST":
        try:
            # Obtener el archivo del formulario
            if request.files['video']:
                archivo = request.files["video"]

                # Guardar el archivo en el servidor
                nombre_archivo = secure_filename(archivo.filename).split('.mp4')[0]
                ruta = "static/videos/" + nombre_archivo + '.mp4'
                archivo.save(ruta)
                nuevoVideo = Video(date.today(), nombre_archivo, ruta)
                session.add(nuevoVideo)
                session.commit()
                # Devolver una respuesta
                flash('El video fue guardado')
            else:
                flash('Se requier al menos un video para subir')
        except Exception as e:
            flash(e)
            session.rollback()
            flash('El archivo seleccionado no es seguro o válido, verifique que sea formato .mp4')
        
    return render_template('multimedia.html', videos = session.query(Video).order_by(Video.fecha.desc()).all())

#@requiredSession
@app.route('/eliminar/video/<int:id>')
def eliminarVideo(id):
    try:
        video = session.get(Video, id)
        os.remove(f'{video.ruta}')
        session.delete(video)
        session.commit()
        flash('Video eliminado de manera correcta')
    except Exception as e:
        flash(e)
        session.rollback()
    finally:
        return redirect('/subir_video')

#@requiredSession
@app.route('/agenda/cambiar', methods=['GET', 'POST'])
def cambiarAgenda():
    if request.method == 'POST':

        try:
            data = request.form

            print(data)

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

#@requiredSession
@app.route('/historial/citas')
def historialCitas():
    historial = session.query(Turno).filter(Turno.localidad != "Sin localidad", Turno.asiste != "Pendiente").order_by(Turno.fecha.desc()).all()
    return render_template('/historial/citas.html', citas = historial)

@app.route('/registrarVoluntario', methods = ['POST', 'GET'])
def registrarVoluntario():
    if request.method != 'POST':
        return render_template('registrarVoluntario.html', voluntarios = session.query(Voluntario).all())
    
    data = request.form

    nombre = data['nombre']
    localiddad = data['localidad']
    telegramId = data['telegramId']

    try:
        nuevoVoluntario = Voluntario(nombre, localiddad, telegramId)
        session.add(nuevoVoluntario)
        session.commit()
        flash("Registro exitoso")
        return redirect('/registrarVoluntario')
    except Exception as e:
        session.rollback()
        return e
    
@app.route('/eliminarVoluntario/<int:id>')
def eliminarVoluntario(id):
    voluntario = session.get(Voluntario, id)

    if voluntario != None:
        try:
            session.delete(voluntario)
            session.commit()
        except:
            session.rollback()
    
    return redirect('/registrarVoluntario')
    

#registro de familias

from familias import familias
app.register_blueprint(familias)

#registro de turnos
from turnos import turnos
app.register_blueprint(turnos)

#registro de apis
from apis import apis
app.register_blueprint(apis)

zona = pytz.timezone("America/Mexico_City")
Base.metadata.create_all(engine)