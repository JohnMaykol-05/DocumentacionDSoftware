"""Pixel art original: solo dos fotogramas por personaje, creados al iniciar."""
import pygame

BORDE = (25, 23, 49)
BLANCO = (255, 250, 226)


def rect(s, color, x, y, w, h):
    pygame.draw.rect(s, color, (x, y, w, h))


def jugador(color, frame):
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    oscuro = tuple(int(c * 0.62) for c in color)
    rect(s, BORDE, 6, 0, 4, 3)
    rect(s, color, 7, 0, 2, 2)
    rect(s, BORDE, 3, 2, 10, 1)
    rect(s, BORDE, 2, 3, 12, 8)
    rect(s, (176, 192, 219), 3, 3, 10, 7)
    rect(s, BLANCO, 3, 3, 9, 5)
    rect(s, BORDE, 4, 5, 8, 5)
    rect(s, (250, 202, 145), 5, 6, 6, 3)
    rect(s, (255, 226, 180), 5, 6, 6, 1)
    rect(s, BORDE, 6, 6, 1, 3)
    rect(s, BORDE, 9, 6, 1, 3)
    rect(s, BORDE, 4, 10, 8, 6)
    rect(s, oscuro, 5, 11, 6, 4)
    rect(s, color, 5, 11, 5, 2)
    rect(s, (255, 216, 81), 5, 13, 6, 1)
    rect(s, BORDE, 7, 13, 2, 1)
    for x, paso in ((2, frame), (11, 1 - frame)):
        rect(s, BORDE, x, 10 + paso, 3, 4)
        rect(s, BLANCO, x, 11 + paso, 2, 2)
    for x, paso in ((3, frame), (9, 1 - frame)):
        rect(s, BORDE, x, 15 - paso, 4, 3)
        rect(s, color, x, 15 - paso, 3, 2)
    return s


def enemigo(tipo, frame):
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    if tipo == "babosa":
        y = 4 + frame
        rect(s, BORDE, 4, y - 1, 8, 1)
        rect(s, BORDE, 2, y, 12, 10)
        rect(s, BORDE, 1, y + 3, 14, 5)
        rect(s, (19, 127, 73), 3, y, 10, 9)
        rect(s, (91, 237, 86), 3, y, 9, 6)
        rect(s, (183, 255, 114), 4, y, 4, 2)
        for x in (5, 10):
            rect(s, BLANCO, x - 1, y + 2, 3, 4)
            rect(s, BORDE, x, y + 3, 1, 3)
        rect(s, BORDE, 6, y + 7, 4, 1)
        for x in (2 + frame, 10 - frame):
            rect(s, (45, 187, 65), x, 14, 4, 2)
    elif tipo == "cazador":
        for x in (2, 11):
            rect(s, BORDE, x, 1, 3, 5)
            rect(s, (255, 224, 153), x + 1, 1, 1, 4)
        rect(s, BORDE, 2, 4, 12, 10)
        rect(s, (179, 37, 67), 3, 5, 10, 8)
        rect(s, (255, 91, 83), 3, 5, 9, 5)
        rect(s, (255, 160, 126), 4, 5, 3, 1)
        for x in (4, 9):
            rect(s, (255, 231, 100), x, 7, 3, 3)
            rect(s, BORDE, x + 1, 7, 1, 3)
        rect(s, BORDE, 4, 6, 2, 1)
        rect(s, BORDE, 10, 6, 2, 1)
        rect(s, BORDE, 5, 11, 6, 2)
        rect(s, BLANCO, 5, 11, 1, 2)
        rect(s, BLANCO, 10, 11, 1, 2)
        for x, paso in ((3, frame), (9, 1 - frame)):
            rect(s, BORDE, x, 14 - paso, 4, 3)
            rect(s, (227, 53, 77), x, 14 - paso, 3, 2)
    elif tipo == "corredor":
        rect(s, BORDE, 3, 1, 2, 4)
        rect(s, BORDE, 11, 1, 2, 4)
        rect(s, (73, 211, 255), 2, 1, 2, 2)
        rect(s, (73, 211, 255), 12, 1, 2, 2)
        rect(s, BORDE, 3, 3, 10, 11)
        rect(s, BORDE, 1, 6, 14, 6)
        rect(s, (227, 147, 32), 3, 4, 10, 9)
        rect(s, (255, 219, 65), 3, 4, 9, 7)
        rect(s, (255, 246, 160), 5, 4, 3, 2)
        rect(s, BORDE, 3, 7, 10, 3)
        rect(s, (113, 238, 255), 4, 8, 3, 1)
        rect(s, (113, 238, 255), 9, 8, 3, 1)
        rect(s, BORDE, 7, 4, 1, 3)
        rect(s, BORDE, 7, 11, 1, 2)
        for x, paso in ((1, frame), (11, 1 - frame)):
            rect(s, BORDE, x, 13 + paso, 4, 2)
            rect(s, (255, 173, 40), x, 13 + paso, 3, 1)
    elif tipo == "fantasma":
        y = frame
        rect(s, BORDE, 5, 2 + y, 6, 1)
        rect(s, BORDE, 3, 3 + y, 10, 2)
        rect(s, BORDE, 2, 5 + y, 12, 9)
        rect(s, (114, 70, 197), 3, 4 + y, 10, 10)
        rect(s, (189, 132, 255), 4, 4 + y, 8, 7)
        rect(s, (227, 193, 255), 5, 4 + y, 4, 2)
        for x in (4, 9):
            rect(s, BORDE, x, 7 + y, 3, 4)
            rect(s, (104, 255, 232), x + 1, 8 + y, 1, 2)
        rect(s, BORDE, 7, 12 + y, 2, 1)
        for x in (2, 6, 10):
            rect(s, BORDE, x, 14, 4, 2 + ((x // 4 + frame) % 2))
            rect(s, (158, 98, 229), x + 1, 13, 2, 2 + ((x // 4 + frame) % 2))
    return s


def jefe(frame):
    s = pygame.Surface((24, 24), pygame.SRCALPHA)
    for x in (2, 19):
        rect(s, BORDE, x, 1, 3, 7)
        rect(s, (255, 216, 72), x + 1, 1, 2, 6)
    rect(s, BORDE, 5, 3, 14, 17)
    rect(s, (138, 36, 121), 6, 4, 12, 15)
    rect(s, (235, 73, 153), 6, 4, 11, 9)
    rect(s, (255, 143, 193), 8, 4, 5, 2)
    for x in (6, 14):
        rect(s, BORDE, x, 8, 4, 5)
        rect(s, (255, 224, 92), x + 1, 9, 2, 3)
        rect(s, BLANCO, x + 1, 9, 1, 1)
    rect(s, BORDE, 8, 15, 8, 3)
    for x in (9, 13):
        rect(s, BLANCO, x, 15, 2, 2)
    for x, paso in ((1, frame), (19, 1 - frame)):
        rect(s, BORDE, x, 10 - paso, 4, 8)
        rect(s, (255, 178, 49), x + 1, 11 - paso, 3, 5)
    for x, paso in ((5, frame), (14, 1 - frame)):
        rect(s, BORDE, x, 20 - paso, 5, 4)
        rect(s, (255, 178, 49), x, 20 - paso, 4, 3)
    return s


def icono(tipo):
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    if tipo == "bomba":
        rect(s, (255, 211, 52), 10, 0, 2, 3)
        rect(s, (255, 242, 167), 12, 1, 2, 1)
        rect(s, BORDE, 8, 2, 3, 3)
        rect(s, (26, 31, 55), 4, 5, 9, 10)
        rect(s, (26, 31, 55), 2, 7, 13, 6)
        rect(s, (63, 78, 111), 4, 6, 7, 6)
        rect(s, (161, 190, 220), 5, 7, 3, 2)
        rect(s, (17, 22, 44), 6, 13, 6, 2)
    elif tipo == "fuego":
        for color, x, y, w, h in [((168, 36, 54), 3, 7, 11, 8),
                                 ((255, 95, 39), 4, 5, 9, 9),
                                 ((255, 95, 39), 7, 0, 3, 9),
                                 ((255, 160, 40), 5, 7, 7, 7),
                                 ((255, 160, 40), 9, 4, 3, 8),
                                 ((255, 236, 102), 7, 9, 4, 6),
                                 ((255, 251, 201), 8, 12, 2, 3)]:
            rect(s, color, x, y, w, h)
    elif tipo == "botas":
        rect(s, BORDE, 5, 1, 7, 10)
        rect(s, BORDE, 3, 9, 11, 6)
        rect(s, (242, 119, 37), 6, 2, 5, 9)
        rect(s, (255, 194, 60), 6, 2, 4, 6)
        rect(s, (255, 194, 60), 4, 10, 9, 3)
        rect(s, (255, 241, 148), 6, 3, 2, 3)
        rect(s, BLANCO, 4, 13, 10, 1)
        rect(s, BLANCO, 9, 7, 3, 1)
        rect(s, BLANCO, 9, 9, 3, 1)
        rect(s, (87, 227, 255), 0, 5, 3, 1)
        rect(s, (87, 227, 255), 1, 7, 3, 1)
    elif tipo == "vida":
        filas = [(2, 3, 4), (9, 3, 4), (1, 4, 13), (1, 5, 13),
                 (2, 8, 11), (3, 10, 9), (4, 11, 7), (5, 12, 5), (6, 13, 3), (7, 14, 1)]
        for x, y, w in filas:
            rect(s, BORDE, x, y, w, 2 if y in (5, 8) else 1)
        rect(s, (222, 47, 94), 2, 4, 5, 5)
        rect(s, (222, 47, 94), 8, 4, 5, 5)
        rect(s, (255, 83, 120), 3, 5, 9, 5)
        rect(s, (255, 83, 120), 4, 9, 7, 2)
        rect(s, (255, 83, 120), 5, 11, 5, 1)
        rect(s, (255, 83, 120), 6, 12, 3, 1)
        rect(s, (255, 83, 120), 7, 13, 1, 1)
        rect(s, (255, 191, 204), 3, 5, 3, 1)
    elif tipo == "escudo":
        rect(s, BORDE, 2, 2, 12, 9)
        rect(s, (93, 218, 255), 3, 3, 10, 7)
        rect(s, (45, 111, 222), 7, 3, 5, 7)
        rect(s, (93, 218, 255), 4, 10, 8, 2)
        rect(s, (93, 218, 255), 6, 12, 4, 2)
        rect(s, BLANCO, 5, 4, 1, 5)
    return s


def crear_sprites():
    """Dos imágenes por tipo; alternar el índice 0/1 es toda la animación."""
    imagenes = {}
    for numero, color in enumerate(((255, 100, 178), (64, 175, 255))):
        imagenes[f"p{numero}"] = [pygame.transform.scale(jugador(color, f), (48, 54)) for f in range(2)]
    for tipo in ("babosa", "cazador", "corredor", "fantasma"):
        imagenes[tipo] = [pygame.transform.scale(enemigo(tipo, f), (48, 54)) for f in range(2)]
    imagenes["jefe"] = [pygame.transform.scale(jefe(f), (72, 72)) for f in range(2)]
    return imagenes


# Fuente mínima de 5x7 para menú y HUD.
LETRAS = {
    "A": [14, 17, 17, 31, 17, 17, 17], "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [14, 17, 16, 16, 16, 17, 14], "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31], "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [14, 17, 16, 23, 17, 17, 14], "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [31, 4, 4, 4, 4, 4, 31], "J": [7, 2, 2, 2, 18, 18, 12],
    "K": [17, 18, 20, 24, 20, 18, 17], "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17], "N": [17, 25, 21, 19, 17, 17, 17],
    "O": [14, 17, 17, 17, 17, 17, 14], "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13], "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [15, 16, 16, 14, 1, 1, 30], "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14], "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 21, 10], "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4], "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 17, 19, 21, 25, 17, 14], "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 2, 4, 8, 31], "3": [30, 1, 1, 14, 1, 1, 30],
    "4": [2, 6, 10, 18, 31, 2, 2], "5": [31, 16, 16, 30, 1, 1, 30],
    "6": [14, 16, 16, 30, 17, 17, 14], "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14], "9": [14, 17, 17, 15, 1, 1, 14],
    "/": [1, 1, 2, 4, 8, 16, 16], "-": [0, 0, 0, 31, 0, 0, 0],
    "!": [4, 4, 4, 4, 4, 0, 4], "+": [0, 4, 4, 31, 4, 4, 0],
    ">": [16, 8, 4, 2, 4, 8, 16], " ": [0] * 7,
}


def texto_pixel(texto, escala, color):
    imagen = pygame.Surface((max(1, len(texto) * 6 - 1) * escala, 7 * escala), pygame.SRCALPHA)
    for i, letra in enumerate(texto.upper()):
        for y, fila in enumerate(LETRAS.get(letra, LETRAS[" "])):
            for x in range(5):
                if fila & (1 << (4 - x)):
                    rect(imagen, color, (i * 6 + x) * escala, y * escala, escala, escala)
    return imagen
