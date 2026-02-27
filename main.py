import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def dynamic_java_optimizer(code):
    tips = []
    
    # --- 🔴 1. FINANCIAL DATA TYPE INTELLIGENCE ---
    # Agar code mein money/price/revenue jese words hain aur double use ho raha hai
    money_words = ['price', 'revenue', 'amount', 'salary', 'balance', 'cost', 'money']
    if any(word in code.lower() for word in money_words) and "double" in code:
        code = code.replace("double", "BigDecimal")
        if "import java.math.BigDecimal;" not in code:
            code = "import java.math.BigDecimal;\n" + code
        tips.append("💰 <b>Financial Integrity:</b> Detected financial variables. Replaced <code>double</code> with <code>BigDecimal</code> to prevent precision loss.")

    # --- 🔴 2. COLLECTION OPTIMIZATION (Map.merge) ---
    # Agar getOrDefault aur put ka pattern dikhta hai (common in aggregations)
    map_update_pattern = r'(\w+)\.put\((.*?),\s*\1\.getOrDefault\(\2,\s*(.*?)\)\s*\+\s*(.*?)\)'
    if re.search(map_update_pattern, code):
        code = re.sub(map_update_pattern, r'\1.merge(\2, \4, (oldVal, newVal) -> oldVal + newVal)', code)
        tips.append("🚀 <b>Performance:</b> Refactored Map updates to <code>merge()</code>. This reduces internal hash lookups by 50%.")

    # --- 🔴 3. ITERATION INTELLIGENCE (O(n) Optimization) ---
    # Detect multiple loops on the same collection (Dynamic detection)
    collections = re.findall(r'for\s*\(.*:\s*(\w+)\)', code)
    duplicate_collections = [c for c in set(collections) if collections.count(c) > 1]
    if duplicate_collections:
        tips.append(f"🏗️ <b>Architectural Review:</b> Detected multiple loops over <code>{duplicate_collections[0]}</code>. Tech Lead suggests merging these into a <b>Single Pass</b> for O(n) efficiency.")

    # --- 🔴 4. MEMORY & IMMUTABILITY ---
    # Automatically add 'final' to class fields if missing (Architect favorite)
    if "class " in code and "final " not in code:
        # Avoid final on method parameters or local variables for now
        code = re.sub(r'(private|public|protected)\s+(String|int|double|long|BigDecimal|List)\s+(\w+);', r'\1 final \2 \3;', code)
        tips.append("🔒 <b>Thread Safety:</b> Applied <code>final</code> modifiers to class fields to ensure immutability.")

    # --- 🔴 5. ALGORITHM INTELLIGENCE (Top-K) ---
    # Detect sorting for small limits (O(n log n) -> O(n log k))
    if ".sorted(" in code and ".limit(" in code:
        limit_match = re.search(r'\.limit\((\d+)\)', code)
        limit_val = limit_match.group(1) if limit_match else "K"
        tips.append(f"📉 <b>Algorithm Fix:</b> Full sorting for Top-{limit_val} is inefficient. Use a <b>PriorityQueue (Heap)</b> to achieve O(n log {limit_val}) complexity.")

    # --- 🔴 6. HASHMAP INITIALIZATION ---
    # Detect map creation and suggest initial capacity if it's inside a method with a list
    if "new HashMap<>()" in code and "List" in code:
        code = code.replace("new HashMap<>()", "new HashMap<>(expectedSize)")
        tips.append("📏 <b>Memory:</b> Set initial capacity for HashMaps to prevent costly internal resizing/rehashing.")

    return code, tips

# --- EXISTING RUN LOGIC (WORKING 100%) ---
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
    language = data.get('lang', 'java') 
    try:
        if language == 'python':
            file_path = "/tmp/script.py"
            with open(file_path, "w") as f: f.write(code)
            run_res = subprocess.run(['python3', file_path], input=stdin_data, capture_output=True, text=True, timeout=10)
            return jsonify({"output": run_res.stdout + run_res.stderr})
        else:
            match = re.search(r'public\s+class\s+(\w+)', code); class_name = match.group(1) if match else "Main"
            file_path = f"/tmp/{class_name}.java"
            with open(file_path, "w") as f: f.write(code)
            compile_res = subprocess.run(['javac', '-g:none', '-d', '/tmp', file_path], capture_output=True, text=True)
            if compile_res.returncode != 0: return jsonify({"output": "Compile Error:\n" + compile_res.stderr})
            run_res = subprocess.run(['java', '-Xmx128m', '-Xms64m', '-XX:+TieredCompilation', '-cp', '/tmp', class_name], input=stdin_data, capture_output=True, text=True, timeout=10)
            return jsonify({"output": run_res.stdout + run_res.stderr})
    except Exception as e: return jsonify({"output": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
