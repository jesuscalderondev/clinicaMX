from flask import Flask, render_template, request, redirect, flash, url_for
from flask import session as cookies
from flask_cors import CORS
from os import getenv
from dotenv import load_dotenv
from datetime import timedelta
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os

from database import *
from functions import *

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')
Bootstrap(app)

CORS(app, origins=['*'], supports_credentials=True)

#programador.add_job(saludar, 'cron', hour=20, minute=50, second=45, args=['holaaa'])

def agendar():
    try:
        nuevaAgenda = DiaTrabajo(datetime.strftime(date.today(), '%Y-%m-%d'), 15, '8:00', '15:30')
        session.add(nuevaAgenda)
        session.commit()
    except Exception as e:
        print("Error: ", e)
        session.rollback()

@app.route('/')
def index():
    if 'token' in cookies:
        return redirect('/home')
    return render_template('login.html')

@app.route('/web')
def pruebas():
    return render_template('prueba.html')

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
        print(e)
        return redirect('/')
    

#@requiredSession
@app.route('/home')
def home():
        return render_template('inicio.html')

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
            print(e)
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
        print(e)
        session.rollback()
    finally:
        return redirect('/subir_video')

#@requiredSession
@app.route('/agenda/cambiar', methods=['GET', 'POST'])
def cambiarAgenda():
    if request.method == 'POST':

        try:
            data = request.form

            fecha = data['fecha']
            inicio = data['inicio']
            fin = data['fin']
            intervalo = data['intervalo']

            nuevo = session.query(DiaTrabajo).filter(DiaTrabajo.fecha == fecha).first()

            #turnos = session.query(Turno).filter(Turno.fecha == fecha).all()

            if nuevo != None:
                nuevo.inicio = datetime.strptime(inicio, "%H:%M").time()
                nuevo.fin = datetime.strptime(fin, "%H:%M").time()
                nuevo.intervalo = intervalo
            else:
                nuevo = DiaTrabajo(fecha, intervalo, inicio, fin)
            
            session.add(nuevo)
            session.commit()

            flash('Se ha actualizado de manera correcta la fecha para trabajo')
        except Exception as e:
            print(e)
            session.rollback()
            flash('Ha ocurrido un error a la hora de modificar la fecha')
    return render_template('agenda.html', fechaMin = date.today() + timedelta(days=3))
            
    
#registro de familias

from familias import familias
app.register_blueprint(familias)

#registro de turnos
from turnos import turnos
app.register_blueprint(turnos)

#registro de apis
from apis import apis
app.register_blueprint(apis)

if __name__ == '__main__':
    load_dotenv()
    Base.metadata.create_all(engine)
    agendar()
    programador.start()
    programador.add_job(agendar, 'cron', hour=0, minute=0)
    app.run(debug=True, host='0.0.0.0')