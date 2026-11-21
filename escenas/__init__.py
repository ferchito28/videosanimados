"""Lista de escenas disponibles. Para agregar una nueva, créala en esta carpeta
e impórtala aquí."""
from .resbalon import Resbalon
from .parkour import Parkour

ESCENAS = {e.nombre: e for e in (Resbalon, Parkour)}
