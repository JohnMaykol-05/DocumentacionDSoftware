"""Cinco mapas reproducibles y una arena final. Colores y enemigos editables."""

NIVELES = [
    {"nombre": "Patio", "color": (255, 206, 71), "suelo": (65, 152, 77),
     "semilla": 11, "bloques": 0.30,
     "enemigos": [(7, 5, "babosa"), (11, 9, "babosa"), (3, 7, "corredor")]},
    {"nombre": "Almacenes", "color": (255, 163, 76), "suelo": (47, 139, 143),
     "semilla": 25, "bloques": 0.35,
     "enemigos": [(7, 5, "babosa"), (3, 9, "cazador"), (11, 7, "corredor"), (9, 3, "cazador")]},
    {"nombre": "Jardin", "color": (150, 241, 97), "suelo": (83, 143, 97),
     "semilla": 37, "bloques": 0.34,
     "enemigos": [(5, 5, "cazador"), (11, 5, "fantasma"), (3, 9, "corredor"), (9, 9, "babosa")]},
    {"nombre": "Tuneles", "color": (194, 145, 255), "suelo": (95, 100, 164),
     "semilla": 49, "bloques": 0.36,
     "enemigos": [(7, 3, "cazador"), (3, 7, "fantasma"), (11, 7, "corredor"), (7, 9, "cazador"), (3, 9, "babosa")]},
    {"nombre": "Fortaleza", "color": (255, 116, 138), "suelo": (143, 90, 116),
     "semilla": 61, "bloques": 0.33,
     "enemigos": [(7, 3, "cazador"), (3, 5, "fantasma"), (11, 5, "corredor"),
                  (5, 9, "cazador"), (11, 9, "fantasma"), (7, 7, "corredor")]},
    {"nombre": "Guardian", "color": (255, 202, 69), "suelo": (100, 76, 139),
     "semilla": 73, "bloques": 0, "enemigos": []},
]
