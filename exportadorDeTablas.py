import openpyxl
from database import *

class ExportadorHistorial():

    def __init__(self, lista:list):
        self.citas = lista

    def generarExcel(self):

        libro = openpyxl.Workbook()

        hoja = libro.active
        print(self.citas[0])
        fecha = self.citas[0][0].fecha.strftime("%Y-%m-%d")
        hoja.title = f"Historial_de_{fecha}"

        encabezados = ["No.", "Nombre del jefe de familia", "Nombre completo del paciente", "Fecha de nacimiento", "Hora de cita", "Procedencia", "Volante derivación", "1A VEZ", "SUB", "Agendado", "Reasignado", "Espontaneo", "Asistió"]
        hoja.append(encabezados)

        contador = 1
        for cita in self.citas:
            cita = cita[0]
            if cita.veces == 'Primera vez':
                primeraVez = "X"
                sub = ""
            else:
                primeraVez = ""
                sub = "X"

            if cita.condicion == 'Agendado':
                agendado = "X"
                reasignado = ""
                espontaneo = ""
            elif cita.condicion == 'Reasignado':
                agendado = ""
                reasignado = "X"
                espontaneo = ""
            else:
                agendado = ""
                reasignado = ""
                espontaneo = "X"

            print(cita.__dict__)
            
            valores = [
                contador,
                cita.deriva,
                cita.paciente,
                cita.fechaNacimiento.strftime("%Y-%m-%d"),
                str(cita.hora)[:5],
                cita.localidad,
                f'C1-{cita.id}',
                primeraVez,
                sub,
                agendado,
                reasignado,
                espontaneo,
                cita.asiste
            ]

            hoja.append(valores)
            contador+=1
        
        rutaArchivo = "Historial.xlsx"
        libro.save(rutaArchivo)
        print("Se guardó")

        return rutaArchivo