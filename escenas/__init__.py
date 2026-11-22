"""Lista de escenas disponibles. Para agregar una nueva, créala en esta carpeta
e impórtala aquí."""
from .resbalon import Resbalon
from .parkour import Parkour
from .juntas_concreto import JuntasConcreto

ESCENAS = {e.nombre: e for e in (Resbalon, Parkour, JuntasConcreto)}
