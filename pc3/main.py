from browser import document, window
import traceback
from types import SimpleNamespace

page = SimpleNamespace()

class Square:
    def __init__(self, name):
        self.name = name
        self.element = document[name]
        self.value = ""
    
    def to_canonical(self, value):
        return str(value).strip().upper()
    
    def __eq__(self, value):
        if value is self: return True
        value = self.to_canonical(value)
        if value == self.value: return True
        return False
        
    def __ne__(self, value):
        return not self.__eq__(value)
    
    def is_empty(self):
        return self.value == ""
    
    def set_contents(self, value = ""):
        value = self.to_canonical(value)
        if value not in ("X", "O", ""): value = ""
        self.value = value
        self.element.innerHTML = self.get_glyph(value)
        self.element.setAttribute("class", value)
    
    def get_glyph(self, value):
        if value == "X": return "&#x274C;"
        if value == "O": return "&#x2b55;"
        return value
    
    def __str__(self):
        return self.name

SQUARES = [ Square(name) for name in ("a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3") ]
SQUARES_BY_NAME = { square.name : square for square in SQUARES }

def show_popup(text):
    page.stderr.textContent = text
    page.popup_layer.setAttribute("class", "")

def hide_popup(*args):
    page.popup_layer.setAttribute("class", "hidden")

def clear_board(event):
    for square in SQUARES:
        square.set_contents()

def make_move(event):
    square = SQUARES_BY_NAME.get(event.target.id)
    if not square:
        return
    elif square.is_empty():
        square.set_contents("O")
        run_ai()
    else:
        show_popup(f"You cannot move in square {square} because it is already occupied!")
        return

def run_ai():        
    text = page.editor.getValue()   
    local_vars = {}
    
    for square in SQUARES:
        local_vars[square.name] = square
    
    try:
        exec(text, globals(), local_vars)
    except Exception as e:
        show_popup(traceback.format_exc())
    
    move = local_vars.get("move")
    if not isinstance(move, Square):
        show_popup("The AI did not choose a move!")
    elif move.is_empty():
        move.set_contents("X")
    else:
        show_popup(f"The AI tried to move in square {move} which is already occupied!")
    
def main():
    window.ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.13/")

    page.stderr = document["stderr"]
    page.editor = window.ace.edit("editor")
    page.popup_layer = document["popup-layer"]    
    page.popup_layer.addEventListener("click", hide_popup)
       
    page.editor.setOptions({
        "mode": 'ace/mode/python',
    });

    document["clear-button"].bind("click", clear_board)

    for square in SQUARES:
        square.element.bind("click", make_move)

main()
