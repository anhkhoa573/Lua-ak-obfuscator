from flask import Flask, render_template, request, jsonify
import os
import base64
import random
import string

app = Flask(__name__)

def obfuscate_lua(code, options):
    lines = code.split(chr(10))
    result = []
    result.append("-- Obfuscated by Python Flask Obfuscator")
    result.append("")

    if options.get('encodeStrings'):
        encoded = base64.b64encode(code.encode()).decode()
        wrapper = (
            'local __c = "' + encoded + '"\n'
            'local __b = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"\n'
            'local __d = (function(s)\n'
            '  s = s:gsub("[^"..__b.."=]", "")\n'
            '  return (s:gsub(".", function(x)\n'
            '    if x == "=" then return "" end\n'
            '    local r, f = "", (__b:find(x, 1, true) - 1)\n'
            '    for i = 6, 1, -1 do r = r .. (f % 2^i - f % 2^(i-1) > 0 and "1" or "0") end\n'
            '    return r\n'
            '  end):gsub("%d%d%d?%d?%d?%d?%d?%d?", function(x)\n'
            '    if #x ~= 8 then return "" end\n'
            '    local c = 0\n'
            '    for i = 1, 8 do c = c + (x:sub(i, i) == "1" and 2^(8-i) or 0) end\n'
            '    return string.char(c)\n'
            '  end))\n'
            'end)(__c)\n'
            '(loadstring or load)(__d)()'
        )
        return wrapper

    if options.get('vmProtect'):
        result.append("local __vm = function()")
        for line in lines:
            result.append("    " + line)
        result.append("end")
        result.append("__vm()")
        return chr(10).join(result)

    if options.get('scramble'):
        random.shuffle(lines)
        result.extend(lines)
        return chr(10).join(result)

    result.extend(lines)
    return chr(10).join(result)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/obfuscate", methods=["POST"])
def api_obfuscate():
    try:
        data = request.get_json()
        code = data.get("code", "").strip()
        options = data.get("options", {})
        if not code:
            return jsonify({"ok": False, "error": "Vui long nhap code Lua!"})
        output = obfuscate_lua(code, options)
        return jsonify({"ok": True, "output": output})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
