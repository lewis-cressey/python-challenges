from browser import document, window
import traceback
from types import SimpleNamespace

NUM_ROWS = 10
NUM_COLUMNS = 20

page = SimpleNamespace()
local_vars = {}
cells = []

class Cell:
    def __init__(self, value, element):
        self.value = value
        self.element = element
        self.element.textContent = str(value)
        self.reset(False)

    def reset(self, required_status):
        self.required_status = required_status
        self.element.style["background-color"] = "white"
        self.set_actual_status(False)

    def set_actual_status(self, actual_status):
        self.actual_status = actual_status
        classnames = []
        if self.required_status: classnames.append("required")
        if self.actual_status: classnames.append("actual")
        self.element.setAttribute("class", " ".join(classnames))        

    def mark(self):
        self.is_correct = self.actual_status == self.required_status
        self.element.style["background-color"] = "#bfb" if self.is_correct else "#fbb"
        return self.is_correct

class Challenge:
    def __init__(self, number, html, values):
        self.number = number
        self.html = html
        self.values = values
        
    def run(self):
        document["task-number"].textContent = self.number
        document["task-description"].innerHTML = self.html
        
        for cell in cells:
            cell.reset(cell.value in self.values)

def gen_box():
    values = []
    center = 90
    min = -4
    max = 4
    for i in range(min, max + 1):
        values.append(center + 20 * i + min)
        values.append(center + 20 * i + max)
        values.append(center + 20 * min + i)
        values.append(center + 20 * max + i)
    return values

def gen_primes(limit):
    primes = []
    for n in range(2, limit):
        for prime in primes:
            if n % prime == 0: break
        else: primes.append(n)
    return primes


def seq(n, f):
    values = [n]
    while n < 200:
        n = f(n)
        values.append(n)
    return values

def spiral(x):
    values = [x]
    direction = [1, 20, -1, -20]
    for length in range(10):
        for i in range(length):
            x += direction[0]
            values.append(x)
        direction.append(direction.pop(0))
    return values
    
challenges = [
    Challenge(1, "Mark the number 10", [10]),
    Challenge(2, "Mark every number in the horizontal line", range(45, 56)),
    Challenge(3, "Mark every number from 20 up to 40", range(20, 40)),
    Challenge(4, "Mark every number in the horizontal line", range(45, 56)),
    Challenge(5, "Mark every even number in the table", range(0, 200, 2)),
    Challenge(6, "Mark every odd number in the table", range(1, 200, 2)),
    Challenge(7, "Mark every number in the vertical line", range(8, 200, 20)),
    Challenge(8, "Mark every multiple of 3 in the table", range(0, 200, 3)),    
    Challenge(9, "Mark the diagonal line", [ x for x in range(5, 200, 21) ]),
    Challenge(10, "Mark every multiple of 3 which is not also a multiple of 9", [ x for x in range(0, 200, 3) if x % 9 != 0 ]),
    Challenge(11, "Mark every power of 2", [ 2**x for x in range(8) ]),
    Challenge(12, "Mark the cross", [ x for x in range(5, 200, 21) ] + [ x for x in range(15, 200, 19) ]),
    Challenge(13, "Mark every number in the box shape", gen_box()),
    Challenge(14, "Mark every prime_number", gen_primes(200)),
    Challenge(15, "Mark every number in the geometric sequence", seq(1, lambda x: 2 * x + 1)),
    Challenge(16, "Mark the spiral", spiral(90)),
    Challenge(17, "You have completed every challenge!", [584639]),
]
current_challenge = challenges.pop(0)

def set_status(n, status):
    if n < 0 or n >= len(cells): return False
    cells[n].set_actual_status(status)
    return True

def show_popup(text):
    page.stderr.textContent = text
    page.popup_layer.setAttribute("class", "")

def hide_popup(*args):
    current_challenge.run()
    page.popup_layer.setAttribute("class", "hidden")
    
def run_program(*args):
    text = page.editor.getValue()
    local_vars["mark"] = lambda n: set_status(n, True)
    local_vars["erase"] = lambda n: set_status(n, False)
    hide_popup()
    
    try:
        exec(text, globals(), dict(local_vars))
    except Exception as e:
        show_popup(traceback.format_exc())

    success = True
    for i in range(len(cells)):
        if not cells[i].mark(): success = False

    if success:
        show_popup("Congratulations! You are onto the next challenge...")
        global current_challenge
        current_challenge = challenges.pop(0)
    else:
        show_popup("The numbers marked in red are incorrect.")
        
def main():
    window.ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.13/")

    page.run_button = document["run-button"]
    page.stderr = document["stderr"]
    page.editor = window.ace.edit("editor")
    page.popup_layer = document["popup-layer"]    
    page.popup_layer.addEventListener("click", hide_popup)
    page.numtab = document["numtab"]
    
    for row in range(NUM_ROWS):
        row_element = document.createElement("tr")
        page.numtab.append(row_element)
        for column in range(NUM_COLUMNS):
            value = row * NUM_COLUMNS + column
            cell_element = document.createElement("td")
            row_element.append(cell_element)
            cells.append(Cell(value, cell_element))
    
    page.editor.setOptions({
        "mode": 'ace/mode/python',
    });

    page.run_button.bind("click", run_program)
    
    current_challenge.run()

main()
