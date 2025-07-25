import streamlit as st
import random


st.set_page_config(
    page_title="Knightfall",
    page_icon="🐎",
    layout="centered",
    initial_sidebar_state="expanded"
)



# 🔧 Konstanten
BOARD_SIZE = 8
hell_colors = {
    "treasure": "#FFD700",     # Gold auf hellem Feld
    "near":     "#FF8168",     # Sanftes Rot
    "mid":      "#FF9A33",     # Orange
    "outer":    "#70BF73",     # Grünes Pastell
    "default":  "#4BA6FF",     # Hellblau
}

dunkel_colors = {
    "treasure": "#FAD000",     # Dunkler Goldton
    "near":     "#FF6242",     # Kräftiges Rot
    "mid":      "#FF8100",     # Dunkelorange
    "outer":    "#4CAF50",     # Waldgrün
    "default":  "#1E90FF",     # Dunkelblau
}


#"treasure": "#FFD700",   # Gold
 #   "near": "#FF6347",       # Rot
  #  "mid": "#FFA500",        # Orange
   # "outer": "#32CD32",      # Grün
    #"default": "#1E90FF",    # Blau


box_shadows = {
    "treasure": "inset 0 0 8px rgba(104, 0, 0, 0.6)",   # Goldglanz
    "near":     "inset 0 0 6px rgba(10, 0, 0, 0.5)",     # Rotwarnung
    "mid":      "inset 0 0 5px rgba(10, 10, 0, 0.4)",   # Orange
    "outer":    "inset 0 0 4px rgba(0, 10, 0, 0.4)",   # Grünsanft
    "default":  "inset 0 0 3px rgba(0, 0, 0, 0.4)",  # Standardblau
    "neutral":  "inset 0 0 3px rgba(0, 0, 0, 0.3)", #sonst
}





class Figur:
    def __init__(self, symbol, pos, bedroht_fn, bewegt=False, trigger=None, frisch = False):
        self.symbol = symbol
        self.pos = pos
        self.bedroht = bedroht_fn
        self.bewegt = bewegt        # z.B. Turm bewegt sich bei jedem Zug
        self.trigger = trigger      # z.B. Dame erscheint ab Zug 10
        self.frisch = frisch

if "knight_pos" not in st.session_state: st.session_state.knight_pos = (1, 0)

if "start_pos" not in st.session_state:
    st.session_state.start_pos = st.session_state.knight_pos



    
SCHATZ_ANZAHL = 3  # Anzahl der Schätze
def generiere_schätze(anzahl, start_pos):
    alle_felder = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if (x, y) != start_pos]
    return set(random.sample(alle_felder, anzahl))





def bischof_bedroht(pos, figuren):
    felder = []
    richtungen = [(1,1),(-1,1),(1,-1),(-1,-1)]
    x, y = pos
    belegte = {f.pos for f in figuren if f.pos and f.pos != pos}
    
    for dx, dy in richtungen:
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            felder.append((nx, ny))
            if (nx, ny) in belegte:
                break  # Blockiert – Sichtlinie endet hier
            nx += dx
            ny += dy
    return felder
           
def turm_bedroht(pos, figuren):
    felder = []
    richtungen = [(1,0),(-1,0),(0,1),(0,-1)]
    x, y = pos
    belegte = {f.pos for f in figuren if f.pos and f.pos != pos}
    
    for dx, dy in richtungen:
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            felder.append((nx, ny))
            if (nx, ny) in belegte:
                break  # Blockiert – Sichtlinie endet hier
            nx += dx
            ny += dy
    return felder
           
           
                      


def dame_bedroht(pos, figuren):
    felder = []
    richtungen = [(1,0),(-1,0),(0,1),(0,-1), (1,1),(-1,1),(1,-1),(-1,-1)]
    x, y = pos
    belegte = {f.pos for f in figuren if f.pos and f.pos != pos}
    
    for dx, dy in richtungen:
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            felder.append((nx, ny))
            if (nx, ny) in belegte:
                break  # Blockiert – Sichtlinie endet hier
            nx += dx
            ny += dy
    return felder




if "schätze" not in st.session_state:
    st.session_state.schätze = generiere_schätze(SCHATZ_ANZAHL, st.session_state.start_pos)






    
    

def get_field_color(x, y):
    pos = (x, y)
    schätze = st.session_state.schätze
    is_light_square = (x + y) % 2 == 0
    color_set = hell_colors if is_light_square else dunkel_colors

    if pos == st.session_state.knight_pos or pos in st.session_state.visited:
        if pos in schätze:
            return color_set["treasure"]

        min_dist = min([max(abs(x - sx), abs(y - sy)) for (sx, sy) in schätze])
        if min_dist == 1:
            return color_set["near"]
        elif min_dist == 2:
            return color_set["mid"]
        elif min_dist == 3:
            return color_set["outer"]
        else:
            return color_set["default"]

    else:
        return "#E3E3E3" if is_light_square else "#8E8E8E"


def get_feldtyp(x, y):
    pos = (x, y)
    schätze = st.session_state.schätze

    if pos == st.session_state.knight_pos or pos in st.session_state.visited:
        if pos in schätze:
            return "treasure"

        min_dist = min([max(abs(x - sx), abs(y - sy)) for (sx, sy) in schätze])
        if min_dist == 1:
            return "near"
        elif min_dist == 2:
            return "mid"
        elif min_dist == 3:
            return "outer"
        else:
            return "default"
    else:
        return "neutral"







def parse_input(move):
    files = "abcdefgh"
    ranks = "123456789"
    if len(move) != 2:
        return None
    file, rank = move[0].lower(), move[1]
    if file in files and rank in ranks:
        x = files.index(file)
        y = BOARD_SIZE - int(rank)  # Schach hat y von unten nach oben
        return (x, y)
    return None

def get_figurenfarbe(symbol):
    farben = {
        "♘": "white",
        "♛": "black",
        "♜": "black",
        "♝": "black",
        "•": "crimson",
        "♞": "black"
    }
    return farben.get(symbol, "black")





def zeige_spielfeld():
    buchstaben = "abcdefgh"
    
    grid_html = "<table style='border-collapse: separate; border-spacing: 0px;'>"
    for y in range(BOARD_SIZE):
        grid_html += f"<tr><th style='padding:4px; border:none;'>{8 - y}</th>"
        for x in range(BOARD_SIZE):
            pos = (x, y)
            color = get_field_color(x, y)
            feldtyp = get_feldtyp(x, y)
            border_style = "1px solid #BC8400" if feldtyp == "treasure" else "1px solid transparent"
            shadow = box_shadows.get(feldtyp, "inset 0 0 2px rgba(0,0,0,0.1)")  # fallback
            # 🔎 Figurensymbol
            symbol = "♘" if pos == st.session_state.knight_pos else ""
            punkt_symbol = "•"
            if pos in st.session_state.angriffspfad and pos != st.session_state.knight_pos:
                symbol = punkt_symbol
            if pos == st.session_state.start_pos:
                border_style = "2px solid black"
                symbol = "⌂" if symbol == "" else symbol
            if pos == st.session_state.knight_pos and st.session_state.unverwundbar_züge > 1:
                shadow = "inset 0 0 6px black"
                symbol = "♞"



            for figur in st.session_state.figuren:
                if figur.pos == pos and symbol != "♘":
                    symbol = figur.symbol
            text_color = get_figurenfarbe(symbol)
            grid_html += f"<td style='width:40px;height:40px; padding: 0;text-align:center;vertical-align:middle;background-color:{color};color:{text_color};box-shadow:{shadow}; border:{border_style}; overflow:hidden;position:relative;'> <div style=' transform: scale(2.4);  display:inline-block;line-height:1; '>{symbol}</div></td>"
        grid_html += "</tr>"
    # Spaltenbeschriftung unten
    grid_html += "<tr><th style='border:none;'></th>" + "".join([f"<th style='border:none;'>{b}</th>" for b in buchstaben]) + "</tr>"
    grid_html += "</table>"
    st.markdown(grid_html, unsafe_allow_html=True)

   
alle_felder = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]

# 🧭 Initialisierung
if "spiel_aktiv" not in st.session_state: st.session_state.spiel_aktiv = True
if "züge" not in st.session_state: st.session_state.züge = 0
if "visited" not in st.session_state: st.session_state.visited = set()
if "schätze" not in st.session_state:
    st.session_state.schätze = set(random.sample(alle_felder, SCHATZ_ANZAHL))
if "gefunden" not in st.session_state: st.session_state.gefunden = set()
if "figuren" not in st.session_state:
    belegte = {st.session_state.knight_pos}
    bishop_pos = random.choice([
    pos for pos in alle_felder
    if st.session_state.knight_pos not in bischof_bedroht(pos, [])
       and pos != st.session_state.knight_pos
])
    

    belegte.add(bishop_pos)
    turm_pos = random.choice([pos for pos in alle_felder if pos not in belegte])
    st.session_state.figuren = [
        Figur("♝", bishop_pos, bischof_bedroht, bewegt=True),
        Figur("♜", turm_pos, turm_bedroht, bewegt=True),
    ]

if "gegner_züge" not in st.session_state:
    st.session_state.gegner_züge = []
if "angriffspfad" not in st.session_state:
    st.session_state.angriffspfad = []
if "gewonnen" not in st.session_state:
    st.session_state.gewonnen = False
if "tot" not in st.session_state:
    st.session_state.tot = False
if "unverwundbar_züge" not in st.session_state:
    st.session_state.unverwundbar_züge = 0




# 🐴 Springer-Zugberechnung
def knight_moves(pos):
    x, y = pos
    moves = [(x+dx, y+dy) for dx, dy in 
             [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]]
    return [(a,b) for (a,b) in moves if 0 <= a < BOARD_SIZE and 0 <= b < BOARD_SIZE]

def koordinaten_zu_notation(pos):
    x, y = pos
    buchstaben = "abcdefgh"
    return f"{buchstaben[x]}{8 - y}"


def berechne_sichere_position(bedroht_fn, symbol="?", figur_list=None):
    figuren = figur_list if figur_list is not None else st.session_state.figuren
    alle_felder = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]
    belegte = {f.pos for f in figuren if f.pos}
    belegte.add(st.session_state.knight_pos)

    mögliche_felder = [pos for pos in alle_felder
                       if pos not in belegte
                       and st.session_state.knight_pos not in bedroht_fn(pos, figuren)]
    if mögliche_felder:
        return random.choice(mögliche_felder)
    return None

def berechne_schrittpfad(start, ziel):
    pfad = []
    x, y = start
    x2, y2 = ziel
    while (x, y) != (x2, y2):
        if x < x2: x += 1
        elif x > x2: x -= 1
        if y < y2: y += 1
        elif y > y2: y -= 1
        pfad.append((x, y))
    return pfad






# 🚀 UI
st.title("♘ Knightfall")

col1, col2 = st.columns([6,4])
with col1:

  if st.session_state.spiel_aktiv:
      
# Eingabe
  
    move_input = st.text_input("Zielposition (z.B. **a6**)", value="a6")
  
    if st.button("Zug bestätigen"):
        target = parse_input(move_input)
        legal = knight_moves(st.session_state.knight_pos)
        

           
        if target in legal:
           st.session_state.visited.add(st.session_state.knight_pos)
           st.session_state.knight_pos = target
           st.session_state.züge += 1
           if st.session_state.unverwundbar_züge > 0:
               st.session_state.unverwundbar_züge -= 1
               if st.session_state.unverwundbar_züge == 1:
                   st.toast("⚠️ Du bist wieder sichtbar!")

            # ☠️ Bedrohungslogik
           for figur in st.session_state.figuren:
                    if figur.pos:
                        bedroht = figur.bedroht(figur.pos, st.session_state.figuren)
                        if target == figur.pos:
                            figur.pos = None
                            st.success(f"♘ hat {figur.symbol} geschlagen!")
                        
                        if target in bedroht and figur.pos != target:
                          if st.session_state.unverwundbar_züge == 0: 
                            angreifer = figur
                            st.session_state.gegner_züge.append(f"{angreifer.symbol} schlägt ♘ auf {koordinaten_zu_notation(st.session_state.knight_pos)}")
                            st.session_state.angreifer_feedback = f"💀 Game Over! {angreifer.symbol} schlägt ♘!"
                            st.session_state.spiel_aktiv = False
                            st.session_state.tot = True
                            st.session_state.angriffspfad = berechne_schrittpfad(angreifer.pos, st.session_state.knight_pos)
                            st.rerun()
                          else:
                              st.toast("🛡️ Du bleibst unbemerkt!")   
                            
              # Gewonnen:              
           if target == st.session_state.start_pos and len(st.session_state.gefunden) == SCHATZ_ANZAHL:
             st.session_state.gewonnen_feedback = "🎉 Du bist mit allen Schätzen entkommen! 🏆"
             st.session_state.spiel_aktiv = False
             st.session_state.gewonnen = True
             st.rerun() 
           if st.session_state.knight_pos in st.session_state.schätze:
             st.session_state.gefunden.add(st.session_state.knight_pos)
             st.session_state.unverwundbar_züge = 4
             if not st.session_state.tot:
                st.session_state.unverwundbar_feedback = "🛡️ Du bist für 3 Züge unsichtbar!"
                st.rerun()
                            
                            
        # 🎯 Neue Figur: Dame ab Zug 5
           if st.session_state.züge == 5:
              pos = berechne_sichere_position(dame_bedroht, "♛")
              if pos:
                  dame = Figur("♛", pos, dame_bedroht, bewegt=True, frisch=True)
                  st.session_state.figuren.append(dame)
                  st.warning(f"♛ ist gekommen – neues Unheil auf {koordinaten_zu_notation(pos)}!")
              
                   
           if st.session_state.züge % 9 == 0:
               tote_figuren = [f for f in st.session_state.figuren if f.pos is None]
               if tote_figuren:
                   figur = random.choice(tote_figuren)
                   pos = berechne_sichere_position(figur.bedroht, figur.symbol)
                   if pos:
                       figur.pos = pos
                       figur.frisch = True
                       st.warning(f"{figur.symbol} ist zurück – auf {koordinaten_zu_notation(pos)}!")

                   
           
        
           # ↔ Turm bewegen (wenn aktiviert)
           bewegliche = []
           for figur in st.session_state.figuren:
               if figur.bewegt and figur.pos and not figur.frisch:
                   bedroht = figur.bedroht(figur.pos, st.session_state.figuren)
                   belegte = {f.pos for f in st.session_state.figuren if f.pos and f != figur}
                   belegte.add(st.session_state.knight_pos)
                   erlaubte = [pos for pos in bedroht if pos not in belegte]
                   if erlaubte:
                       bewegliche.append((figur, erlaubte))
                   
           if bewegliche:
               figur, erlaubte = random.choice(bewegliche)
               alte_pos = figur.pos
               figur.pos = random.choice(erlaubte)
               start = koordinaten_zu_notation(alte_pos)
               ziel = koordinaten_zu_notation(figur.pos)
               st.toast(f"{figur.symbol} bewegt sich von {start} nach {ziel}")
               st.session_state.gegner_züge.append(f"{figur.symbol}: {start} → {ziel}")

          # 🔄 Nach dem gesamten Springer-Zug
           for figur in st.session_state.figuren:
              if figur.frisch:
                  figur.frisch = False
           
      

        else:
            st.warning("Ungültiger Zug! Nur legale Springerzüge erlaubt.")
  
  else:
    if st.session_state.gewonnen and not st.session_state.tot:  
      if "gewonnen_feedback" in st.session_state:
          st.success(st.session_state.gewonnen_feedback)
          st.balloons()
    if st.session_state.tot:
      if "angreifer_feedback" in st.session_state:
        st.error(st.session_state.angreifer_feedback)
        
  
    

# Grid anzeigen

# Erfolgsnachricht, wenn alle gefunden
  
     
  zeige_spielfeld()
    

    # Anzahl der gefundenen Schätze zählen
  st.write(f"✨ Gefundene Schätze: {len(st.session_state.gefunden)} / {SCHATZ_ANZAHL}")
  if st.session_state.knight_pos in st.session_state.schätze and not st.session_state.tot:
      if "unverwundbar_feedback" in st.session_state:
          st.toast(st.session_state.unverwundbar_feedback)
  if len(st.session_state.gefunden) == SCHATZ_ANZAHL and st.session_state.spiel_aktiv:
      st.info("Alle Schätze gefunden! Schnell, zurück zum Ausgang!")

    
    
with col2:
    st.write("📜 Gegnerische Züge:")
    gegner_html = """
    <div style='max-height:480px; overflow-y:auto; padding:4px;'>
    """
    for zug in st.session_state.gegner_züge:
        gegner_html += f"<div style='margin-bottom:4px;'>• {zug}</div>"
    gegner_html += "</div>"

    st.markdown(gegner_html, unsafe_allow_html=True)


with st.sidebar:
    st.title("♘ So räuberst du die Festung:")
    st.markdown(f"""
                Finde alle {SCHATZ_ANZAHL} Schätze. Entkomme mit der Beute!
                Aber hüte dich vor den Wächtern!
                
                **Schlachtplan:**
                
                - Deine Figur **♘** kann sich gemäß zulässigen Springerzügen bewegen.
                - Gib dazu die **Koordinaten** in das Feld ein und **bestätige den Zug**.
                - Alle Schätze gefunden? Schnell! Zurück zum Ausgang **⌂**!
                
                **Farben**:
                - Besuchst du ein Feld, leuchtet es in einer Farbe:
                    - 🟨 Eine Schatzkammer!
                    - 🟥 Um die Schatzkammer!
                    - 🟧 Um die roten Felder!
                    - 🟩 Um die orangenen Felder!
                    - 🟦 Alle übrigen Felder.
                - Zur besseren Orientierung erhalten **dunkle Felder dunklere Farbtöne** als helle Felder.     
                
                **Wächter**:
                - ♛, ♜, ♝ verhalten sich wie im **klassischen Schach**. Nach jedem deiner Züge bewegt sich einer der Wächter.    
                - Das Spiel beginnt mit ♜ und ♝, nach **5 Zügen** kommt ♛ hinzu.
                - Begibst du dich in das **Sichtfeld eines Wächters**, wirst du angegriffen und das **Spiel endet**.
                - Betrittst du eine **Schatzkammer**, bist du für die nächsten drei Züge **unsichtbar** und kannst **nicht angegriffen** werden!
                - Alle **9 Züge** ersteht eine **geschlagene Figur** wieder auf.
    
                """)
    


### Weitere Ideen: Level, Boardgröße, mehr oder weniger oft auferstehende Figuren, andere Schatzanzahl
