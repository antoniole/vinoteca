from dataclasses import dataclass
import datetime
from typing import Optional

@dataclass
class Vino: 
    id: Optional[int] = None   
    nombre: str = ''
    tipo: str = 'Tinto'
    cosecha: int = 2024
    bodega: str =''
    pais: str = 'España'
    denominacion: str = ''   
    variedad1: str = ''
    porcentajeVariedad1: int = 0
    variedad2: str = ''
    porcentajeVariedad2: int = 0
    variedad3: str = ''
    porcentajeVariedad3: int = 0
    variedad4: str = ''
    porcentajeVariedad4: int = 0
    guarda: bool = False
    fechaConsumo: int = None
    cantidad: int = 1
    fichaTecnica: str = ''
    
@dataclass
class Nota:
    id: Optional[int] = None
    vinoId: Optional[int]= None
    notaCata: str=''
    fechaCata: Optional[str] = None
    valoracion: Optional[int] = None

@dataclass
class FiltrosVino:
    cosecha: Optional[int] = None
    tipo: Optional[str] = None
    pais: Optional[str] = None
    denominacion: Optional[str] = None
    