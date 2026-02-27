import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SMART OPTIMIZER ENGINE (Architect Mode) ---
def heuristic_optimizer(code):
    tips = []
    optimized_code = code

    # 1. ARCHITECT REVIEW: Detect O(3n) vs O(n) - Multiple passes on same collection
    # Agar orders list par baar baar loop chal raha hai (For revenue, then for spending, etc.)
    loop_pattern = r'for\s*\(\s*Order\s+\w+\s*:\s*orders\s*\)'
    loops = re.findall(loop_pattern, code)
    if len(loops) > 1:
        tips.append(f"🏗️ <b>Architectural Flaw:</b> You are iterating 'orders' {len(loops)} times. Use a <b>Single Pass Stream</b> to compute Revenue, Spending, and Product counts simultaneously.")

    # 2. ALGO OPTIMIZATION: Sorting 1M records for Top 3 (O(n log n))
    if ".sorted(" in code and ".limit(" in code:
        tips.append("📉 <b>Algorithm Fix:</b> Sorting 1M records for just Top-3 is O(n log n). Use a <b>PriorityQueue (Min-Heap)</b> to do it in O(n log 3).")

    # 3. PERFORMANCE: Parallel Stream on Large Data
    if ("1_000_000" in code or "1000000" in code) and ".parallelStream()" not in code:
        if ".stream()" in code:
            optimized_code = optimized_code.replace(".stream()", ".parallelStream()")
            tips.append("⚡ <b>Performance:</b> Large dataset (1M) detected. Switched to <b>parallelStream()</b>.")
        else:
            tips.append("💡 <b>Scalability:</b> For 1,000,000+ records, consider using <b>Parallel Streams</b>.")

    # 4. SAFETY: Thread Safety in Parallel Processing
    if ".parallelStream()" in optimized_code and "new HashMap<>" in optimized_code:
        tips.append("⚠️ <b>Thread Safety:</b> You are using parallelStream with a non-thread-safe HashMap. Use <b>ConcurrentHashMap</b> or <b>Collectors.groupingBy</b>.")

    # 5. MEMORY: StringBuilder for loop concatenations
    if re.search(r'for\s*\(.*\)\s*\{[^{}]*\+=\s*".*"', code) and "StringBuilder" not in code:
        tips.append("📦 <b>Memory:</b> Detected String concatenation in a loop. Use <b>StringBuilder</b> to reduce Heap pressure.")

    # 6. RECALCULATION: Check if revenue (qty * price) is repeated
    if code.count("quantity * item.price") > 2:
        tips.append("🔢 <b>Efficiency:</b> Revenue (qty * price) is recalculated multiple times. Store it in a variable during the first pass.")

    return optimized_code, tips

# --- NEW OPTIMIZE ROUTE ---
@app.route('/optimize', methods=['POST'])
def optimize_code():
    data = request.json
    code = data.get('code', '')
    
    # Run our smart engine
    optimized_code, tips = heuristic_optimizer(code)
    
    return jsonify({
        "optimized_code": optimized_code,
        "tips": tips
    })

# --- EXISTING RUN LOGIC (DO NOT TOUCH - WORKING 100%) ---
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    language = data.get('lang', 'java') 

    try:
        # --- PYTHON LOGIC ---
        if language == 'python':
            file_path = "/tmp/script.py"
            with open(file_path, "w") as f:
                f.write(code)
            
            run_res = subprocess.run(
                ['python3', file_path], 
                input=stdin_data, 
                capture_output=True, 
                text=True,
                timeout=10 
            )
            return jsonify({"output": run_res.stdout + run_res.stderr})

        # --- JAVA LOGIC ---
        else:
            match = re.search(r'public\s+class\s+(\w+)', code)
            if not match:
                match = re.search(r'class\s+(\w+)', code)
            
            class_name = match.group(1) if match else "Main"
            file_path = f"/tmp/{class_name}.java"
            
            with open(file_path, "w") as f:
                f.write(code)

            compile_res = subprocess.run(['javac', '-g:none', '-d', '/tmp', file_path], capture_output=True, text=True)
            if compile_res.returncode != 0:
                return jsonify({"output": "Compile Error:\n" + compile_res.stderr})

            run_res = subprocess.run(
                ['java', '-Xmx128m', '-Xms64m', '-XX:+TieredCompilation', '-cp', '/tmp', class_name], 
                input=stdin_data, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            output = run_res.stdout + run_res.stderr
            if not output and run_res.returncode == 0:
                output = "Program executed successfully (No Output)."
                
            return jsonify({"output": output})

    except subprocess.TimeoutExpired:
        return jsonify({"output": "Execution Timeout: Your code took too long to run."})
    except Exception as e:
        return jsonify({"output": "System Error: " + str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
