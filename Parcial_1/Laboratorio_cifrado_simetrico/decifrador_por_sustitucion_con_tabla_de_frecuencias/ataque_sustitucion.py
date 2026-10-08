#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ataque por análisis de frecuencias + optimización contra un cifrado por
SUSTITUCIÓN SIMPLE (español), con editor interactivo en la terminal.

Pasos:
 1) Pegas el texto cifrado (con espacios, lo que sea).
 2) Se genera una primera clave por frecuencias de letras (tu tabla).
 3) Un optimizador (recocido simulado) mejora esa clave probando miles de
    combinaciones y puntuándolas con trigramas y palabras típicas del español.
 4) Se abre el editor, donde corriges a mano:

   ← → ↑ ↓     moverte por las letras del texto
   (escribir)   una letra: la letra cifrada bajo el cursor pasa a ser esa
                letra clara (se intercambia con la que la tuviera)
   Tab          bloquear / desbloquear esa letra cifrada (queda fija)
   Ctrl+O       volver a optimizar el resto SIN tocar las letras bloqueadas
   Retroceso    devolver esa letra cifrada a la sugerencia inicial
   Ctrl+R       reiniciar todo a la sugerencia inicial
   Ctrl+S       guardar el texto actual en resultado.txt
   Esc          salir (el texto final se imprime en la terminal)

Truco: cuando reconozcas una palabra, ve a una de sus letras, pulsa Tab en
cada letra segura y luego Ctrl+O: el programa reajusta todo lo demás.

En Windows: pip install windows-curses
"""

import curses
import math
import os
import random
import re
import sys
import time
import unicodedata
from collections import Counter

# Tabla de frecuencias (%) del español
FREQ = {
    "e": 16.78, "a": 11.96, "o": 8.69, "l": 8.37, "s": 7.88, "n": 7.01,
    "d": 6.87, "r": 4.94, "u": 4.80, "i": 4.15, "t": 3.31, "c": 2.92,
    "p": 2.776, "m": 2.12, "y": 1.54, "q": 1.53, "b": 0.92, "h": 0.89,
    "g": 0.73, "f": 0.52, "v": 0.39, "j": 0.30, "ñ": 0.29, "z": 0.15,
    "x": 0.06, "k": 0.00, "w": 0.00,
}
ORDEN = sorted(FREQ, key=FREQ.get, reverse=True)
ALFABETO = "abcdefghijklmnñopqrstuvwxyz"


# ---------------------------------------------------------------- utilidades
def normalizar(texto):
    """Minúsculas y sin tildes (conserva la ñ)."""
    salida = []
    for ch in texto.lower():
        if ch == "ñ":
            salida.append(ch)
        else:
            d = unicodedata.normalize("NFD", ch)
            salida.append("".join(c for c in d if unicodedata.category(c) != "Mn"))
    return "".join(salida)


def preparar_cifrado(texto, distinguir_mayusculas):
    """Prepara el texto cifrado. Si las mayúsculas y minúsculas son símbolos
    distintos del cifrado (p. ej. 'V' = y, 'v' = v), no se toca la caja."""
    if distinguir_mayusculas:
        return unicodedata.normalize("NFC", texto)
    return normalizar(texto)


def contar_letras(texto):
    """Cuenta símbolos de letra del texto CIFRADO (cualquier letra, con su caja)."""
    return Counter(c for c in texto if c.isalpha())


def ataque_automatico(cifrado):
    """Clave inicial: cifrada -> clara emparejando por rango de frecuencia."""
    cont = contar_letras(cifrado)
    ranking = sorted(cont, key=lambda c: (-cont[c], c))
    return {c: ORDEN[i] for i, c in enumerate(ranking)}


def descifrar(cifrado, mapa):
    return "".join(mapa.get(c, c) for c in cifrado)


# ------------------------------------------- estadísticas del español (n-gramas)
# Texto de referencia para estimar trigramas. Cuanto más texto, mejor.
CORPUS = """
el sol salia por el este cuando los vecinos del pueblo empezaron a reunirse en la
plaza para hablar de lo que habia pasado durante la noche. nadie sabia con certeza
que era lo que habia ocurrido pero todos tenian una opinion sobre el asunto. la mujer
que vivia junto a la iglesia decia que habia oido ruidos extranos en el tejado mientras
que su marido aseguraba que no habia escuchado nada. los ninos jugaban cerca de la
fuente sin prestar atencion a las conversaciones de los mayores. el alcalde llego
tarde y pidio silencio para poder explicar lo que sabia. segun dijo, un camion habia
chocado contra el muro del cementerio y el conductor se habia marchado sin avisar a
nadie. por suerte no hubo heridos y los danos eran pequenos, pero habia que repararlo
cuanto antes. varios hombres se ofrecieron a ayudar y quedaron en verse despues de
comer con las herramientas necesarias. mientras tanto, las mujeres prepararon cafe
y pan para todos los que habian trabajado desde primera hora de la manana.
la historia de esta region es muy larga y esta llena de cosas interesantes que
mucha gente desconoce. durante siglos fue un lugar de paso para comerciantes y
viajeros que cruzaban las montanas en busca de mejores tierras. con el tiempo se
fueron construyendo casas, caminos y puentes, y asi nacieron los primeros pueblos.
hoy en dia la mayoria de los jovenes se marcha a la ciudad para estudiar o buscar
trabajo, y solo vuelven en verano cuando llega la fiesta. los abuelos recuerdan
con carino aquellos tiempos y cuentan a sus nietos como era la vida antes de que
llegara la luz electrica. no tenian television ni telefono, pero se reunian cada
noche alrededor del fuego para contar historias y cantar canciones.
es importante saber que la lengua cambia con el paso de los anos y que las palabras
que usamos hoy no son siempre las mismas que usaban nuestros antepasados. algunas
desaparecen y otras se inventan para nombrar cosas nuevas. por eso los diccionarios
se actualizan constantemente y los escritores buscan nuevas formas de expresar lo
que sienten. leer libros es una buena manera de aprender y de conocer otras
culturas, y tambien una forma de pasar el tiempo cuando no hay nada mejor que hacer.
para preparar una buena comida hace falta tiempo, paciencia y buenos ingredientes.
primero se corta la cebolla y se pone en la sarten con un poco de aceite hasta que
quede dorada. despues se anaden los tomates y se deja cocinar a fuego lento durante
casi una hora. al final se agrega sal, pimienta y un poco de ajo, y se sirve caliente
con arroz o con pasta. a todos les gusta y siempre piden repetir. nunca he visto a
nadie que no quiera un plato mas cuando la salsa esta bien hecha.
los medicos recomiendan dormir ocho horas, beber mucha agua y hacer ejercicio todos
los dias. sin embargo, la mayoria de las personas no sigue estos consejos porque
tiene demasiado trabajo o simplemente no encuentra el momento adecuado. es cierto
que cuesta cambiar los habitos, pero con un poco de esfuerzo y voluntad se puede
lograr. empezar poco a poco es mejor que querer hacerlo todo de golpe y despues
abandonar. quien persevera obtiene resultados y se siente mucho mejor consigo mismo.
mi hermano vive en otra ciudad desde hace cinco anos y nos llama cada domingo para
saber como estamos. dice que echa de menos la comida de mi madre y las tardes de
verano en el patio de la casa. el proximo mes vendra a visitarnos con su esposa y sus
dos hijos, y toda la familia esta muy contenta. ya hemos empezado a preparar las
habitaciones y a pensar en lo que vamos a hacer durante esos dias. quiero llevarlos
al lago y despues a cenar a ese restaurante que tanto les gusto la ultima vez.
cuando termine la reunion, el director explico que la empresa iba a cambiar de
sistema y que todos los empleados tendrian que asistir a un curso. algunos se quejaron
porque no tenian tiempo, otros dijeron que era una buena oportunidad para aprender.
al final se decidio que las clases serian por la tarde, dos veces por semana, y que
quien no pudiera venir podria ver las grabaciones desde su casa.
el equipo gano el partido con un gol en el ultimo minuto y la gente salio a la calle
para celebrarlo. hubo musica, bengalas y mucha alegria hasta bien entrada la madrugada.
los jugadores agradecieron el apoyo de la aficion y prometieron seguir luchando hasta
conseguir el titulo. el entrenador dijo que habia sido un esfuerzo de todos y que no
habia que olvidar a quienes habian ayudado desde el principio.
la casa tenia un jardin enorme lleno de flores y arboles frutales. por las tardes la
abuela se sentaba bajo el limon con su libro y su taza de te, y nadie se atrevia a
molestarla. en invierno la lluvia golpeaba las ventanas y el viento movia las ramas
con fuerza, pero dentro siempre hacia calor y olia a pan recien hecho.
el gobierno anuncio que el proximo noviembre habria elecciones y que los partidos
tendrian que presentar a sus candidatos antes de septiembre. los dirigentes de la
oposicion criticaron la medida y dijeron que el objetivo real era ganar tiempo. durante
meses la gente salio a las calles para exigir cambios y mejores condiciones de vida.
muchos trabajadores se declararon en huelga y la situacion se volvio muy tensa en varias
provincias. el golpe de estado fracaso y los responsables fueron juzgados, aunque algunos
lograron huir del pais. la victoria llego despues de una larga lucha en la que
participaron miles de voluntarios. nuestro grupo eligio un nuevo representante que debia
defender los intereses de todos, y asi se evito una division que habria sido muy grave.
la guerra dejo una enorme huella en la sociedad y los historiadores todavia discuten sus
causas y consecuencias. en enero, febrero, marzo, abril, mayo, junio, julio, agosto,
septiembre, octubre, noviembre y diciembre, el calendario de la comunidad incluye fiestas,
reuniones y conferencias abiertas a todos los vecinos. los jovenes vieron con claridad
que sin organizacion y sin un programa claro no era posible vencer. la gran mayoria de
los ciudadanos queria vivir en paz y volver a trabajar con normalidad. el juez ordeno
investigar la verdad de lo ocurrido, y el viejo archivo ofrecio nuevas pruebas del caso.
"""

PALABRAS = set("""
de la que el en y a los se del las un por con no una su para es al lo como mas pero sus
le ya o este si porque esta entre cuando muy sin sobre tambien me hasta hay donde quien
desde todo nos durante todos uno les ni contra otros ese eso ante ellos e esto mi antes
algunos unos yo otro otras otra tanto esa estos mucho quienes nada muchos cual poco ella
estar estas algunas algo nosotros mis tu te ti tus ellas son era fue ser tiene tener hacer
hace dice puede han hemos has he ha estaba estan estoy eres somos fui fueron sido siendo
casa tiempo vida dia dias ano anos cosas cosa mundo forma parte lugar gente persona
trabajo hombre mujer ninos nino pueblo ciudad pais agua tierra noche manana tarde hoy
ayer siempre nunca ahora luego despues aqui alli asi bien mal mejor peor mayor menor
grande pequeno nuevo nueva nuevos viejo buena bueno buenos buenas mucha muchas primero
primera ultimo ultima otro otra mismo misma cada entonces mientras aunque sino segun
hacia bajo tras ellos nosotras vosotros vamos va voy ir vez veces uno dos tres cuatro
cinco seis siete ocho nueve diez cien mil lo la le les nos os me se que quien cuyo
donde como cuando cuanto porque pues si no ni tambien tampoco solo solamente quiza
quiero quieres quiere queremos quieren puedo puedes podemos pueden debe deben haber
habia hubo hay sabe saber saben sabia dijo dicen decir dijeron veo ver vio vimos vieron
dar da dio damos dan paso pasar pasa paso mismo todavia ademas incluso entre otros
familia amigo amigos amiga madre padre hijo hijos hija hermano hermana abuelo abuela
comida cena cenar comer beber pan cafe plato platos restaurante camarero sonrisa semana
mes meses hora horas minuto minutos momento calle calles plaza iglesia escuela libro
libros palabra palabras historia historias lengua idioma texto mensaje clave letra letras
llegamos llegar llegamos llego llegaron salir sale salio salimos buscamos buscar busca
encontramos encontrar encontro explico explicar recibio recibir esperabamos esperar
hablamos hablar habla hablan planes plan viaje viajes visitar visitamos queriamos
estaban estabamos estaba estamos estamos abierto cerrado vacias vacio vacia tarde
casi finalmente todavia pequeno lugar donde cuales cual platos mientras todo lo que
gobierno golpe golpes objetivo objetivos dirigente dirigentes revolucion revoluciones
revolucionario revolucionaria victoria vida vivir volver nuevo guerra grupo luego juego
grande gran amigo mayoria enero febrero marzo abril mayo junio julio agosto septiembre
octubre noviembre diciembre pueblo clase obrera trabajadores estado partido partidos
politica politico sociedad historia
""".split())


def _construir_modelo():
    """Prepara log-probabilidades de trigramas (con espacio como separador)."""
    texto = normalizar(CORPUS)
    texto = "".join(c if c in ALFABETO else " " for c in texto)
    texto = " ".join(texto.split())
    t = " " + texto + " "
    sim = ALFABETO + " "

    c1 = Counter(t)
    c2 = Counter(t[i:i + 2] for i in range(len(t) - 1))
    c3 = Counter(t[i:i + 3] for i in range(len(t) - 2))
    n1 = sum(c1.values())

    # unigramas: mezcla de la tabla dada y el corpus
    p1 = {}
    for ch in sim:
        pf = FREQ[ch] / 100 * 0.84 if ch in FREQ else 0.16
        p1[ch] = 0.5 * pf + 0.5 * (c1[ch] + 1) / (n1 + len(sim))

    ctx1 = Counter()
    for bg, n in c2.items():
        ctx1[bg[0]] += n
    ctx2 = Counter()
    for tg, n in c3.items():
        ctx2[tg[:2]] += n

    lp = {}
    for a in sim:
        for b in sim:
            if a == " " and b == " ":
                continue
            for c in sim:
                if b == " " and c == " ":
                    continue
                pu = p1[c]
                pb = (c2[b + c] + 0.5 * pu) / (ctx1[b] + 0.5)
                pt = (c3[a + b + c] + 0.8 * pb) / (ctx2[a + b] + 0.8)
                lp[a + b + c] = math.log(pt)
    return lp


LP3 = _construir_modelo()
PESO_PALABRA = 1.2


def puntuar(txt):
    """Cuanto mayor, más parece español. txt: letras y espacios simples."""
    t = " " + txt + " "
    g = LP3.get
    total = 0.0
    for i in range(len(t) - 2):
        total += g(t[i:i + 3], -9.0)
    for w in txt.split():
        if len(w) > 1 and w in PALABRAS:
            total += PESO_PALABRA * len(w)
    return total


def preparar_base(cifrado):
    """Texto cifrado con todo lo que no sea letra convertido en un espacio."""
    b = "".join(c if c.isalpha() else " " for c in cifrado)
    return " ".join(b.split())


def optimizar(cifrado, mapa, bloqueadas=(), segundos=4.0, avance=None):
    """Recocido simulado sobre la clave. Respeta las letras bloqueadas."""
    rng = random.Random()
    base = preparar_base(cifrado)
    bloqueadas = set(bloqueadas)
    libres = [c for c in mapa if c not in bloqueadas]
    if len(libres) < 2:
        return dict(mapa)
    fijas = {mapa[c] for c in bloqueadas}
    disponibles = [p for p in ALFABETO if p not in fijas]

    def evaluar(m):
        tabla = {ord(c): p for c, p in m.items()}
        return puntuar(base.translate(tabla))

    mejor = dict(mapa)
    mejor_s = evaluar(mejor)
    fin = time.time() + segundos
    ronda = 0
    while time.time() < fin:
        actual = dict(mejor)
        if ronda > 0:                      # sacudir un poco para escapar de óptimos locales
            for _ in range(rng.randint(2, 6)):
                a, b = rng.sample(libres, 2)
                actual[a], actual[b] = actual[b], actual[a]
        s = evaluar(actual)
        pasos = 2500
        T0, T1 = 3.0, 0.05
        for i in range(pasos):
            T = T0 * (T1 / T0) ** (i / pasos)
            usadas = set(actual.values())
            sueltas = [p for p in disponibles if p not in usadas]
            if sueltas and rng.random() < 0.25:
                c = rng.choice(libres)
                p = rng.choice(sueltas)
                viejo = actual[c]
                actual[c] = p
                ns = evaluar(actual)
                if ns >= s or rng.random() < math.exp((ns - s) / T):
                    s = ns
                else:
                    actual[c] = viejo
            else:
                a, b = rng.sample(libres, 2)
                actual[a], actual[b] = actual[b], actual[a]
                ns = evaluar(actual)
                if ns >= s or rng.random() < math.exp((ns - s) / T):
                    s = ns
                else:
                    actual[a], actual[b] = actual[b], actual[a]
            if s > mejor_s:
                mejor_s, mejor = s, dict(actual)
        ronda += 1
        if avance:
            avance(ronda)
    return mejor


# -------------------------------------------------------------- edición
def partir_lineas(texto, ancho):
    """Ajuste de línea por palabras. Devuelve lista de (inicio, fin)."""
    lineas, inicio, n = [], 0, len(texto)
    while inicio < n:
        fin = min(inicio + ancho, n)
        if fin < n:
            esp = texto.rfind(" ", inicio, fin)
            if esp > inicio:
                fin = esp + 1
        lineas.append((inicio, fin))
        inicio = fin
    return lineas or [(0, 0)]


def asignar(mapa, bloqueadas, cifrada, plana):
    """cifrada -> plana, intercambiando con quien la tuviera.
    Devuelve (ok, mensaje)."""
    actual = mapa[cifrada]
    if actual == plana:
        return True, ""
    if cifrada in bloqueadas:
        return False, f"'{cifrada}' está bloqueada (Tab para desbloquear)."
    for k, v in mapa.items():
        if v == plana and k != cifrada:
            if k in bloqueadas:
                return False, f"'{plana}' está fijada por la letra cifrada '{k}' (bloqueada)."
            mapa[k] = actual
            break
    mapa[cifrada] = plana
    return True, ""


def editor(stdscr, cifrado, auto):
    curses.curs_set(0)
    curses.raw()                 # Ctrl+S / Ctrl+R / Ctrl+O llegan como teclas normales
    stdscr.keypad(True)

    try:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # misma letra
        curses.init_pair(2, curses.COLOR_GREEN, -1)                   # bloqueadas
        curses.init_pair(3, curses.COLOR_CYAN, -1)                    # info
        c_igual = curses.color_pair(1)
        c_lock = curses.color_pair(2) | curses.A_BOLD
        c_info = curses.color_pair(3)
    except curses.error:
        c_igual, c_lock, c_info = curses.A_STANDOUT, curses.A_BOLD, curses.A_BOLD

    mapa = dict(auto)
    bloqueadas = set()
    cont = contar_letras(cifrado)
    total = sum(cont.values()) or 1
    posiciones = [i for i, c in enumerate(cifrado) if c.isalpha()]
    cursor = posiciones[0]
    mensaje = "Escribe una letra para asignarla a la letra cifrada marcada."
    top = 0
    PANEL = 7

    def put(y, x, s, attr=0):
        try:
            stdscr.addstr(y, x, s, attr)
        except curses.error:
            pass

    def linea_de(idx, lineas):
        for n, (a, b) in enumerate(lineas):
            if a <= idx < b:
                return n
        return len(lineas) - 1

    while True:
        h, w = stdscr.getmaxyx()
        ancho = max(10, w - 2)
        lineas = partir_lineas(cifrado, ancho)
        n_cur = linea_de(cursor, lineas)
        visibles = max(1, (h - PANEL) // 3)
        if n_cur < top:
            top = n_cur
        if n_cur >= top + visibles:
            top = n_cur - visibles + 1

        stdscr.erase()
        cur_cif = cifrado[cursor]

        # --- texto
        for fila, n in enumerate(range(top, min(len(lineas), top + visibles))):
            a, b = lineas[n]
            y = fila * 3
            for i in range(a, b):
                c = cifrado[i]
                x = 1 + (i - a)
                put(y, x, c, curses.A_DIM)
                if c.isalpha():
                    claro = mapa[c]
                    if i == cursor:
                        attr = curses.A_REVERSE | curses.A_BOLD
                    elif c == cur_cif:
                        attr = c_igual | curses.A_BOLD
                    elif c in bloqueadas:
                        attr = c_lock
                    else:
                        attr = curses.A_BOLD
                else:
                    claro, attr = c, 0
                put(y + 1, x, claro, attr)

        # --- panel inferior
        base = h - PANEL
        if base > 0:
            put(base, 0, "─" * (w - 1))
            claro_cur = mapa[cur_cif]
            veces = cont[cur_cif]
            estado = "  [BLOQUEADA]" if cur_cif in bloqueadas else ""
            put(base + 1, 1,
                f"Letra cifrada '{cur_cif}': {veces} veces ({veces * 100 / total:.2f}%)"
                f"  →  '{claro_cur}' (esperado {FREQ[claro_cur]:.2f}%){estado}",
                c_info | curses.A_BOLD)

            items = []
            for c in sorted(cont, key=lambda k: (-cont[k], k)):
                items.append(f"{c}→{mapa[c]}{'*' if c in bloqueadas else ' '}")
            fila_m, linea_txt = base + 2, ""
            for it in items:
                if len(linea_txt) + len(it) + 2 > w - 2:
                    put(fila_m, 1, linea_txt)
                    fila_m += 1
                    linea_txt = ""
                    if fila_m >= base + 5:
                        break
                linea_txt += it + "  "
            if fila_m < base + 5:
                put(fila_m, 1, linea_txt)

            put(base + 5, 1, mensaje[: w - 2], curses.A_BOLD)
            put(base + 6, 1,
                "←→↑↓ mover | letra: asignar | Tab: bloquear | ^O optimizar | "
                "Retroc: inicial | ^R reiniciar | ^S guardar | Esc salir"[: w - 2],
                curses.A_DIM)

        stdscr.refresh()

        # --- teclas
        try:
            k = stdscr.get_wch()
        except KeyboardInterrupt:
            break
        except curses.error:
            continue

        idx = posiciones.index(cursor)
        if k == curses.KEY_LEFT:
            cursor = posiciones[max(0, idx - 1)]
            mensaje = ""
        elif k == curses.KEY_RIGHT:
            cursor = posiciones[min(len(posiciones) - 1, idx + 1)]
            mensaje = ""
        elif k in (curses.KEY_UP, curses.KEY_DOWN):
            destino = n_cur + (-1 if k == curses.KEY_UP else 1)
            if 0 <= destino < len(lineas):
                col = cursor - lineas[n_cur][0]
                a, b = lineas[destino]
                objetivo = min(a + col, b - 1)
                cursor = min(posiciones, key=lambda p: abs(p - objetivo))
            mensaje = ""
        elif k == curses.KEY_HOME:
            cursor = posiciones[0]
        elif k == curses.KEY_END:
            cursor = posiciones[-1]
        elif k == curses.KEY_RESIZE:
            pass
        elif k in ("\x1b", "\x03"):          # Esc / Ctrl+C
            break
        elif k == "\t":
            if cur_cif in bloqueadas:
                bloqueadas.discard(cur_cif)
                mensaje = f"'{cur_cif}' desbloqueada."
            else:
                bloqueadas.add(cur_cif)
                mensaje = f"'{cur_cif}' bloqueada: no cambiará al asignar ni al optimizar."
        elif k == "\x0f":                    # Ctrl+O
            mensaje = "Optimizando (unos segundos)..."
            put(h - 2, 1, mensaje[: w - 2], curses.A_BOLD | curses.A_REVERSE)
            stdscr.refresh()
            mapa = optimizar(cifrado, mapa, bloqueadas, segundos=4.0)
            mensaje = "Optimizado respetando las letras bloqueadas (^O otra vez para otro intento)."
        elif k in (curses.KEY_BACKSPACE, "\x7f", "\b", curses.KEY_DC):
            if cur_cif in bloqueadas:
                mensaje = f"'{cur_cif}' está bloqueada."
            else:
                ok, msg = asignar(mapa, bloqueadas, cur_cif, auto[cur_cif])
                mensaje = msg or f"'{cur_cif}' vuelve a la sugerencia inicial."
        elif k == "\x12":                    # Ctrl+R
            mapa = dict(auto)
            bloqueadas.clear()
            mensaje = "Todo reiniciado a la sugerencia inicial."
        elif k == "\x13":                    # Ctrl+S
            with open("resultado.txt", "w", encoding="utf-8") as f:
                f.write(descifrar(cifrado, mapa) + "\n")
            mensaje = "Guardado en resultado.txt"
        elif isinstance(k, str) and len(k) == 1:
            letra = normalizar(k)
            if len(letra) == 1 and letra in ALFABETO:
                ok, msg = asignar(mapa, bloqueadas, cur_cif, letra)
                mensaje = msg or f"'{cur_cif}' → '{letra}'"

    return descifrar(cifrado, mapa)


def leer_texto():
    """Lee el texto cifrado: de un archivo (python script.py mensaje.txt)
    o pegado en la terminal con varias líneas, terminado con FIN."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            return f.read()
    print("Pega el texto cifrado (puede tener varias líneas y párrafos).")
    print("Cuando termines, escribe FIN en una línea aparte y pulsa Enter.\n")
    lineas = []
    while True:
        try:
            linea = input()
        except EOFError:
            break
        if linea.strip().upper() == "FIN":
            break
        lineas.append(linea)
    return "\n".join(lineas)


def main():
    os.environ.setdefault("ESCDELAY", "25")   # que Esc responda rápido
    print("ATAQUE POR FRECUENCIAS - CIFRADO POR SUSTITUCIÓN SIMPLE\n")
    entrada = leer_texto()

    distinguir = False
    if any(c.islower() for c in entrada) and any(c.isupper() for c in entrada):
        r = input("\nEl texto mezcla mayúsculas y minúsculas. ¿Son símbolos distintos del "
                  "cifrado (p. ej. 'V' y 'v' son letras diferentes)? [S/n]: ").strip().lower()
        distinguir = r != "n"
    cifrado = preparar_cifrado(entrada, distinguir)

    if not contar_letras(cifrado):
        print("El texto no contiene letras.")
        return
    if len(contar_letras(cifrado)) > len(ALFABETO):
        if distinguir:
            print("Hay más de 27 símbolos distintos; trato mayúsculas y minúsculas como iguales.")
            cifrado = preparar_cifrado(entrada, False)
        if len(contar_letras(cifrado)) > len(ALFABETO):
            print("Hay más de 27 símbolos distintos: no parece una sustitución simple de letras.")
            return

    inicial = ataque_automatico(cifrado)
    print("\nPrimera aproximación (solo frecuencias de letras):")
    print(descifrar(cifrado, inicial))

    print("\nOptimizando con estadísticas del español (unos segundos)...")
    mejorada = optimizar(cifrado, inicial, segundos=6.0)
    print("\nResultado optimizado:")
    print(descifrar(cifrado, mejorada))

    input("\nPulsa Enter para abrir el editor y corregir a mano...")
    final = curses.wrapper(editor, cifrado, mejorada)
    print("\nTEXTO FINAL:")
    print(final)


if __name__ == "__main__":
    main()
