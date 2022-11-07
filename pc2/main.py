from browser import document, window
import traceback
from types import SimpleNamespace

page = SimpleNamespace()
local_vars = {}

def clear_canvas():
    width = page.canvas.width
    height = page.canvas.height
    
    context = page.canvas.getContext("2d")
    context.clearRect(-width, -height, width * 2, height * 2)
    draw_line(0, -height, 0, height)
    draw_line(-width, 0, width, 0)
    
    for sign in [1, -1]:
        for notch in range(0, width, 50):
            context.textBaseline = "top"
            context.textAlign = "center"
            draw_line(sign * notch, -2, sign * notch, 2)
            draw_text(sign * notch, -5, str(sign * notch))
        
        for notch in range(0, width, 50):
            context.textBaseline = "middle"
            context.textAlign = "right"
            draw_line(-2, sign * notch, 2, sign * notch)
            draw_text(-5, sign * notch, str(sign * notch))

def set_pen(colour):
    context = page.canvas.getContext("2d")
    context.strokeStyle = colour
    context.fillStyle = colour

def draw_text(x, y, text):
    context = page.canvas.getContext("2d")
    context.fillText(text, x, -y)

def draw_line(x1, y1, x2, y2):
    context = page.canvas.getContext("2d")
    context.beginPath()
    context.moveTo(x1, -y1)
    context.lineTo(x2, -y2)
    context.stroke()

def hide_popup(*args):
    page.popup_layer.setAttribute("class", "hidden")

def run_program(*args):
    text = page.editor.getValue()
    local_vars["clear"] = clear_canvas
    local_vars["drawline"] = draw_line
    clear_canvas()
    try:
        exec(text, globals(), dict(local_vars))
    except Exception as e:
        text = traceback.format_exc()
        page.stderr.textContent = text
        page.popup_layer.setAttribute("class", "")

def save_image(*args):
    page.download_link.href = page.canvas.toDataURL().replace("image/png", "image/octet-stream")
    page.download_link.click()

def main():
    window.ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.13/")

    page.run_button = document["run-button"]
    page.save_button = document["save-button"]
    page.stderr = document["stderr"]
    page.editor = window.ace.edit("editor")
    page.popup_layer = document["popup-layer"]
    page.canvas = document["my-canvas"]
    page.download_link = document["image-download-link"]
    
    context = page.canvas.getContext("2d")
    context.setTransform(1, 0, 0, 1, page.canvas.width // 2, page.canvas.height // 2)
    
    page.popup_layer.addEventListener("click", hide_popup)
    
    page.editor.setOptions({
        "mode": 'ace/mode/python',
    });

    page.run_button.bind("click", run_program)
    page.save_button.bind("click", save_image)
    clear_canvas()

main()