import pymysql


conexion = pymysql.connect(
    host="clinicMX.mysql.pythonanywhere-services.com",
    user="clinicMX",
    port=3306,
    passwd="mysqlroot",
    db="clinicMX$database",
)


mycur = conexion.cursor()
mycur.execute("""
CREATE TABLE Carros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marca VARCHAR(255) NOT NULL,
    modelo VARCHAR(255) NOT NULL,
    anio INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL
)""")
conexion.commit()
conexion.close()

print("siiiiu")