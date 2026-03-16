import browser
import io
from browser import document, window, worker

class State:
    qno = 0
    max_qno = 9

class LineIo:
    def __init__(self, lines = None, read_index = 0):
        self.lines = lines or []
        self.read_index = read_index

    def clone(self):
        return LineIo(self.lines[:], 0)

    def write(self, line):
        self.lines.append(line)
        return self

    def read(self):
        if self.read_index == len(self.lines): return None
        line = self.lines[self.read_index]
        line = " ".join(line.split()).upper()
        self.read_index += 1
        return line

    def get_lines(self):
        return self.lines[:]

def refresh_nav():
    def onclick(event):
        qno = event.target.getAttribute("data-qno")
        qno = int(qno)
        browser.aio.run(set_qno(qno))
    
    nav_node = document["level-buttons"]
    nav_node.innerHTML = ""
    
    for i in range(State.max_qno + 1):
        button = document.createElement("button")
        if window.pyx.testCompleted(i):
            button.class_name = "completed"
        button.textContent = f"Problem {i + 1}"
        button.attrs["data-qno"] = i
        button.bind("click", onclick)
        nav_node.append(button)

async def set_qno(qno = None):
    if qno is None:
        qno = 0
        while window.pyx.testCompleted(qno): qno += 1
        
    qno = max(0, min(qno, State.max_qno))
    State.qno = qno
    print(f"Setting question number to: {qno}")

    question_node = document["question"]
    description_node = document["description"]
    help_node = document["help"]
    
    response = await browser.aio.get(f"/challenges/c{qno + 1}.html")
    document["title"].textContent = f"Problem {qno + 1}"

    description_node.innerHTML = ""
    help_node.innerHTML = "<h2>Task hints</h2>"

    question_node.innerHTML = response.data
    
    question_code = []
    validator_code = []
    
    for child in question_node.children:
        if child.class_name == "validate":
            lines = child.textContent.split("\n")
            validator_code.extend([ line.rstrip() for line in lines ])
        elif child.class_name == "code":
            lines = child.textContent.split("\n")
            question_code.extend([ line.rstrip() for line in lines ])
        elif child.class_name == "help":
            help_node <= child
        else:
            description_node <= child

    question_code = "\n".join(question_code).strip()
    validator_code = "\n".join(validator_code).strip()
    my_globals = {}
    exec(validator_code, my_globals)
    State.generate = my_globals.get("generate")
    State.validate = my_globals.get("validate")
    if window.localStorage:
        user_code = window.localStorage.getItem(f"q{qno}")
        if isinstance(user_code, str) and len(user_code) > 0:
            question_code = user_code
    window.pyx.setCode(question_code)
    window.pyx.showPane("help")
    
async def change_question(d):
    await set_qno(State.qno + d)

def onmessage(e):
    cmd, *args = e.data
    if cmd == "print":
        line = args[0]
        State.stdout.write(line)
        window.pyx.print(line)
    elif cmd == "exit":
        success = True
        try:
            State.validate(State.stdin.clone(), State.stdout.clone())
        except RuntimeError as e:
            print("Error during validation: {e}")
            success = False
        print(f"Result: {success}")
        if success:
            window.pyx.markCompleted(State.qno)
            refresh_nav()
            set_qno()
        end_code()
    elif cmd == "error":
        window.pyx.print(args[0])
        end_code()
    else:
        print(f"Unknown response: {cmd}")
        end_code()

def pyworker_ready(pyworker):
    code = window.pyx.getCode()
    if window.localStorage:
        window.localStorage.setItem(f"q{State.qno}", code)
    stdin = State.stdin.get_lines()
    print(f"Init input with: {stdin}")
    pyworker.send([ "run", code, stdin ])

def run_code(event):
    document["btn-run"].disabled = True
    window.pyx.clear()
    State.stdin = LineIo()
    State.stdout = LineIo()
    if State.generate: State.generate(State.stdin)
    worker.create_worker("pyworker", pyworker_ready, onmessage)

def end_code():
    document["btn-run"].disabled = False
  
def onload():
    document["btn-prev"].bind("click", lambda e: browser.aio.run(change_question(-1)))
    document["btn-next"].bind("click", lambda e: browser.aio.run(change_question(1)))
    document["btn-run"].bind("click", run_code)

    refresh_nav()
    browser.aio.run(set_qno())

onload()
