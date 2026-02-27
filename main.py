import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 🧠 DYNAMIC ARCHITECT ENGINE (Java Optimization) ---
def dynamic_java_optimizer(code):
    tips = []
    
    # 1. 💰 Dynamic BigDecimal Fix (Any money related variable)
    money_pattern = r'\b(double|float)\b(\s+\w*(?:price|amount|revenue|cost|balance|total|salary)\w*)'
    if re.search(money_pattern, code, re.IGNORECASE):
        code = re.sub(money_pattern, r'BigDecimal\2', code, flags=re.IGNORECASE)
        if "import java.math.BigDecimal;" not in code:
            code = "import java.math.BigDecimal;\n" + code
        tips.append("💰 <b>Money Precision:</b> <code>double</code> ko <code>BigDecimal</code> mein badal diya financial accuracy ke liye.")

    # 2. 🚀 Generic Map.merge Fix (Fast updates)
    atomic_pattern = r'(\w+)\.put\(\s*(.*?),\s*\1\.getOrDefault\(\2,\s*(.*?)\)\s*\+\s*(.*?)\)'
    if re.search(atomic_pattern, code):
        code = re.sub(atomic_pattern, r'\1.merge(\2, \4, (oldVal, newVal) -> oldVal + newVal)', code)
        tips.append("🚀 <b>Speed:</b> <code>Map.merge()</code> use kiya jo <code>put/get</code> se fast hai.")

    # 3. 🏗️ Loop Multiplicity Detection (O(n) Optimization)
    iterated_collections = re.findall(r'for\s*\(\s*\w+\s+\w+\s*:\s*(\w+)\s*\)', code)
    if len(set(iterated_collections)) < len(iterated_collections):
        tips.append("🏗️ <b>Architectural Fix:</b> Multiple loops detect huye. Single-pass processing suggest ki jati hai.")

    # 4. 📉 Top-K PriorityQueue Suggestion
    if ".sorted(" in code and ".limit(" in code:
        tips.append("📉 <b>Algo:</b> Sorting ki jagah <b>PriorityQueue</b> use karein (O(n log k)).")

    # 5. 🔒 Immutability (Final fields)
    if "class " in code and "final " not in code:
        code = re.sub(r'(private|public)\s+(String|int|long|BigDecimal|List)\s+(\w+);', r'\1 final \2 \3;', code)
        tips.append("🔒 <b>Thread Safety:</b> Fields ko <code>final</code> banaya gaya.")

    return code, tips

# --- 🚀 ROUTES: OPTIMIZE & RUN ---

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    code = data.get('code', '')
    optimized_code, tips = dynamic_java_optimizer(code)
    return jsonify({"optimized_code": optimized_code, "tips": tips})

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    language = data.get('lang', 'java') # Default Java

    try:
        # --- 🐍 PYTHON COMPILER LOGIC ---
        if language == 'python':
            file_path = "/tmp/script.py"
            with open(file_path, "w") as f: f.write(code)
            run_res = subprocess.run(['python3', file_path], input=stdin_data, capture_output=True, text=True, timeout=10)
            return jsonify({"output": run_res.stdout + run_res.stderr})

        # --- ☕ JAVA COMPILER LOGIC ---
        else:
            match = re.search(r'public\s+class\s+(\w+)', code)
            class_name = match.group(1) if match else "Main"
            file_path = f"/tmp/{class_name}.java"
            with open(file_path, "w") as f: f.write(code)
            
            # Compile
            compile_res = subprocess.run(['javac', '-d', '/tmp', file_path], capture_output=True, text=True)
            if compile_res.returncode != 0:
                return jsonify({"output": "Compile Error:\n" + compile_res.stderr})
            
            # Run
            run_res = subprocess.run(['java', '-Xmx128m', '-cp', '/tmp', class_name], input=stdin_data, capture_output=True, text=True, timeout=10)
            return jsonify({"output": run_res.stdout + run_res.stderr})

    except subprocess.TimeoutExpired:
        return jsonify({"output": "Error: Timeout (10 seconds)"})
    except Exception as e:
        return jsonify({"output": "System Error: " + str(e)})

if __name__ == '__main__':
    # Render ya local dono ke liye port setup
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
