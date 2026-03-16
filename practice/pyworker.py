from browser import bind, self
import traceback
import io

stdin = []
global_env = {}

def my_input():
    if len(stdin) > 0: return stdin.pop(0)
    raise RuntimeError("Input data exhausted!")

def my_print(*args, **kwargs):
    stdout = io.StringIO()
    print(*args, file=stdout, **kwargs)
    self.send([ "print", stdout.getvalue() ])

def run_code(code, stdin_lines):
    stdin.clear()
    stdin.extend(stdin_lines)

    global_env.clear()
    global_env.update({
        "input" : my_input,
        "print" : my_print,
    })
    
    try:
        result = exec(code, global_env)
        self.send([ "exit", result ])
    except Exception as e:
        # Get a trace of line numbers.
        # Cut off the first two entries, which are internal.
        linenos = []
        tb = e.__traceback__
        while tb:
            linenos.append(str(tb.tb_lineno))
            tb = tb.tb_next
        linenos = "->".join(linenos[2:])
        message = ", ".join([ str(x) for x in e.args ])
        self.send([ "error", f"Error line {linenos}: {message}" ])

@bind(self, "message")
def message(evt):
    cmd, *args = evt.data
    if cmd == "run":
        run_code(*args)
    else:
        print(f"Unknown command: {cmd}")
