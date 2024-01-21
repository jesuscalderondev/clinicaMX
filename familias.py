from flask import Blueprint, render_template, request, redirect, flash

from functions import *
from database import *


familias = Blueprint('familia', __name__, url_prefix='/familias')

#@requiredSession
@familias.route('/registrar', methods=['POST', 'GET'])
def registrarFamili():
    if request.method == 'POST':
        
        try:
            data = request.form
            
            nombre = data['nombre']
            colonia = data['colonia']
            direccion = data['direccion']
            try:
                voluntario = data['voluntario']
            except:
                voluntario = None
                
            nuevaFamilia = Familia(nombre, direccion, colonia)
            nuevaFamilia.voluntario =  voluntario
            session.add(nuevaFamilia)
            session.commit()
            flash('La familia fue registrada de manera exitosa')
        except:
            flash('Error, por favor verifique qeu no flaten datos en el formulario')
        
        return redirect('/familias/registrar')
    
    else:
        return render_template('/familias/registrar.html', promotores = session.query(Voluntario).all())
    
#@requiredSession
@familias.route('/ver')
def verFamilias():
    return render_template('/familias/verLista.html', familias = session.query(Familia).all())

#@requiredSession
@familias.route('/ver/<int:id>')
def verUnaFamilia(id):
    familia = session.get(Familia, id)
    return render_template('/familias/ver.html', familia = familia, session = session, promotor = Voluntario)
