import sqlite3
import time
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4
)

class AuthDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('usuarios.db',check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.crear_tabla_usuarios()

    # Creamos la tabla de usuarios
    
    def crear_tabla_usuarios(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS usuarios (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password_hash TEXT NOT NULL,
                                creado_en REAL NOT NULL
                            )
                        ''')
        self.conn.commit()
    
    # Crear el usuario
    
    def crear_usuario(self,username:str, password: str) -> bool:
        password_hash = ph.hash(password)
        try:
            self.cursor.execute(
                "INSERT INTO usuarios (username, password_hash, creado_en) VALUES (?,?,?)",
                (username,password_hash,time.time())
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def verificar_usuario(self,username: str, password:str):
        self.cursor.execute(
            "SELECT id, password_hash FROM usuarios WHERE username = ?",
            (username,)
        )
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        user_id, password_hash = row
    
        try:
            if ph.verify(password_hash,password):
                return user_id
        except VerifyMismatchError:
            return None
        
    def obtener_usuarios(self):
        self.cursor.execute(
            "SELECT id, username, creado_en FROM usuarios ORDER BY creado_en DESC"
        )
        return self.cursor.fetchall()
    
    def eliminar_usuario(self, user_id: int) -> bool:
        cur = self.cursor.execute(
            "DELETE FROM usuarios WHERE id = ?",
            (user_id,)
        )
        self.conn.commit()
        return cur.rowcount == 1
    
    def cambiar_password(self, user_id: int, nueva_password: str):
        nuevo_hash = ph.hash(nueva_password)
        self.cursor.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?",
            (nuevo_hash,user_id)
        )
        self.conn.commit()
    
    
    
    

