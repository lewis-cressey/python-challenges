import { EditorView, basicSetup } from "https://esm.sh/@codemirror/basic-setup";
import { python } from "https://esm.sh/@codemirror/lang-python";
import {Bitmap} from "./Bitmap.js"

const completionRecord = new Bitmap(window.localStorage.getItem("reptrile"))
const consoleDiv = document.getElementById("console")
let editorView = null

window.pyx = {
    getCode: function() {
        return editorView.state.doc.toString()
    },
    
    setCode: function(code) {
        editorView.dispatch({
          changes: {
            from: 0,
            to: editorView.state.doc.length,
            insert: code
          }
        })
    },

    clear: function() {
        consoleDiv.textContent = ""
    },

    print: function(text) {
        consoleDiv.textContent += text + "\n"
        consoleDiv.scrollTop = consoleDiv.scrollHeight
        window.pyx.showPane("console")
    },

    testCompleted: function(qno) {
        return completionRecord.testBit(qno)
    },

    markCompleted: function(qno) {
        completionRecord.setBit(qno)
        window.localStorage.setItem('reptrile', completionRecord.toString())
        document.getElementById("dialog-completed").showModal()
    },

    showPane: function(selectedName) {
        const tabBar = document.querySelector("#tab-bar")
        for (const node of tabBar.querySelectorAll("button")) {
            const name = node.getAttribute("data-name")
            node.disabled = (selectedName === name)
        }

        const outputFrame = document.querySelector("#output-frame")
        for (const node of outputFrame.querySelectorAll("div.pane")) {
            const name = node.getAttribute("data-name")
            node.style.visibility = (selectedName === name) ? "visible" : "hidden"
        }
    },
};

window.addEventListener("load", async function() {
	editorView = new EditorView({
		extensions: [basicSetup, python()],
		parent: document.querySelector("#editor")
	})

    const tabBar = document.querySelector("#tab-bar")
    for (const button of tabBar.querySelectorAll("button")) {
        const name = button.getAttribute("data-name")
        button.addEventListener("click", function() {
            pyx.showPane(name)
        })
    }

    pyx.showPane("FOO")
})
