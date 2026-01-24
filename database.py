import sqlite3
from models import Vino,Nota

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('vinos.db',check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") # Activa el uso de claves foráneas, por defecto desactivada en SQLite3
        self.crear_tabla_vinos()
        self.crear_tabla_catas()

    def crear_tabla_vinos(self):
        '''
            Función para crear la tabla donde se almacenarán los vinos

        
        :param self: self
        '''
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS vinos (
                                id INTEGER  PRIMARY KEY AUTOINCREMENT,
                                nombre TEXT,
                                tipo TEXT,
                                cosecha INTEGER,
                                bodega TEXT,
                                pais TEXT,
                                denominacion TEXT,
                                variedad1 TEXT,
                                porcentaje_variedad1 INTEGER,
                                variedad2 TEXT,
                                porcentaje_variedad2 INTEGER,
                                variedad3 TEXT,
                                porcentaje_variedad3 INTEGER,
                                variedad4 TEXT,
                                porcentaje_variedad4 INTEGER,                        
                                es_guarda BOOLEAN,
                                fecha_consumo INTEGER,
                                cantidad INTEGER,
                                nota_elaboracion TEXT                                                             
                                )
                            ''')
        self.conn.commit()

    def crear_tabla_catas(self):
        '''
            Función para crear la tabla donde se almacenarán las notas de cata.
        
        :param self: self
        '''
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS catas (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                vino_id INTEGER, -- Esta es la clave externa
                                nota_cata TEXT,
                                fecha_cata TEXT,
                                valoracion INTEGER,
                                FOREIGN KEY (vino_id) REFERENCES vinos (id) ON DELETE CASCADE
                                )
                            ''')
        self.conn.commit()
        
    def obtener_vinos(self,filtros=None) -> list:
        
        sql = "SELECT * FROM vinos WHERE 1=1"
        params = []

        if filtros:
            if filtros.cosecha:
                sql += " AND cosecha = ?"
                params.append(filtros.cosecha)

            if filtros.tipo:
                sql += " AND tipo = ?"
                params.append(filtros.tipo)

            if filtros.pais:
                sql += " AND pais LIKE ?"
                params.append(f"%{filtros.pais}%")

            if filtros.denominacion:
                sql += " AND denominacion LIKE ?"
                params.append(f"%{filtros.denominacion}%")
            if filtros.sinStock:
                sql += " AND cantidad = ?"
                params.append(0)

        self.cursor.execute(sql, params)

        columnas = [col[0] for col in self.cursor.description]

        vinos = []

        for row in self.cursor.fetchall():
            data = dict(zip(columnas,row))
            vinos.append(Vino(
                id=data['id'],
                nombre=data['nombre'],
                tipo=data['tipo'],
                cosecha=data['cosecha'],
                bodega=data['bodega'],
                pais=data['pais'],
                denominacion=data['denominacion'],
                variedad1=data['variedad1'],
                porcentajeVariedad1=data['porcentaje_variedad1'],
                variedad2=data['variedad2'],
                porcentajeVariedad2=data['porcentaje_variedad2'],
                variedad3=data['variedad3'],
                porcentajeVariedad3=data['porcentaje_variedad3'],
                variedad4=data['variedad4'],
                porcentajeVariedad4=data['porcentaje_variedad4'],
                guarda=bool(data['es_guarda']),
                fechaConsumo=data['fecha_consumo'],
                cantidad=data['cantidad'],
                fichaTecnica=data['nota_elaboracion'],
            ))

        return vinos
    
    def insertar_nuevo_vino(self,vino: Vino):
        '''
        Función para agregar un vino a la tabla vinos
        
        :param self: self
        :param vino: vino y sus características para agregar a la tabla
        '''
        sql= '''
                INSERT INTO vinos (
                    nombre,
                    tipo,
                    cosecha,
                    bodega,
                    pais,
                    denominacion,
                    variedad1,
                    porcentaje_variedad1,
                    variedad2,
                    porcentaje_variedad2,
                    variedad3,
                    porcentaje_variedad3,
                    variedad4,
                    porcentaje_variedad4,
                    es_guarda,
                    fecha_consumo,
                    cantidad,
                    nota_elaboracion
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            '''
        
        valores = (
            vino.nombre,vino.tipo,vino.cosecha,vino.bodega,
            vino.pais,vino.denominacion,
            vino.variedad1,vino.porcentajeVariedad1,
            vino.variedad2,vino.porcentajeVariedad2,
            vino.variedad3,vino.porcentajeVariedad3,
            vino.variedad4,vino.porcentajeVariedad4,
            vino.guarda,vino.fechaConsumo,vino.cantidad,
            vino.fichaTecnica
            )
        
        self.cursor.execute(sql,valores)
        self.conn.commit()

    def actualizar_vino(self, vino: Vino) -> None:

        sql = '''
        UPDATE vinos SET
            nombre = ?,
            tipo = ?,
            cosecha = ?,
            bodega = ?,
            pais = ?,
            denominacion = ?,
            variedad1 = ?,
            porcentaje_variedad1 = ?,
            variedad2 = ?,
            porcentaje_variedad2 = ?,
            variedad3 = ?,
            porcentaje_variedad3 = ?,
            variedad4 = ?,
            porcentaje_variedad4 = ?,
            es_guarda = ?,
            fecha_consumo = ?,
            cantidad = ?,
            nota_elaboracion = ?
        WHERE id = ?
        '''
        valores = (
            vino.nombre, vino.tipo, vino.cosecha, vino.bodega,
            vino.pais, vino.denominacion,
            vino.variedad1, vino.porcentajeVariedad1,
            vino.variedad2, vino.porcentajeVariedad2,
            vino.variedad3, vino.porcentajeVariedad3,
            vino.variedad4, vino.porcentajeVariedad4,
            vino.guarda, vino.fechaConsumo, vino.cantidad,
            vino.fichaTecnica, vino.id
        )
        self.cursor.execute(sql, valores)
        self.conn.commit()
    
    def borrar_vino(self,vino_id:int) :
        cur = self.cursor.execute("DELETE FROM vinos WHERE id = ?",(vino_id,))
        self.conn.commit()

        return cur.rowcount == 1
    
    def actualizar_stock(self,vino_id:int,stock) -> None:
        self.cursor.execute("UPDATE vinos SET cantidad = ? WHERE id = ?",(stock,vino_id))
        self.conn.commit()
        

        
    def guardar_nota_elaboracion(self,vino_id,texto):
        '''
        Función para guardar una nota de elaboración (ficha técnica) de forma independiente al incorporar un nuevo vino
        
        :param self: self
        :param vino_id: la id del vino del que se agregará la nota de elaboración
        :param texto: texto de la ficha técnica
        '''
        self.cursor.execute ( "UPDATE vinos SET nota_elaboracion = ? WHERE id = ?",(texto,vino_id))
        self.conn.commit()

    def agregar_cata(self,vino_id,nota,fecha,puntuacion):
       
        self.cursor.execute("INSERT INTO catas (vino_id,nota_cata,fecha_cata,valoracion) VALUES (?,?,?,?)",(vino_id,nota,fecha,puntuacion))
        self.cursor.execute("UPDATE vinos SET cantidad = cantidad -1 WHERE id = ? AND cantidad > 0",(vino_id,))
        self.conn.commit()

    def obtener_catas(self,vino_id):
        self.cursor.execute("SELECT * FROM  catas WHERE vino_id = ? ORDER BY fecha_cata DESC", (vino_id,))
        return [ Nota(
                    id=row[0],
                    vinoId=row[1],
                    notaCata=row[2],
                    fechaCata=row[3],
                    valoracion=row[4]
                )
                for row in self.cursor.fetchall()
                ]
        
    

        
