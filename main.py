import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SMART OPTIMIZER ENGINE (Bina API wala Dimaag) ---
def heuristic_optimizer(code):
    tips = []
    optimized_code = code

    # 1. Detect Large Data + Parallel Stream Suggestion
    if ("1_000_000" in code or "1000000" in code) and ".parallelStream()" not in code:
        if ".stream()" in code:
            optimized_code = optimized_code.replace(".stream()", ".parallelStream()")
            tips.append("⚡ <b>Performance:</b> 1M records detected. Switched to <b>parallelStream()</b> for multi-core speed.")
        else:
            tips.append("💡 <b>Scalability:</b> For 1M records, consider using <b>Parallel Streams</b> to optimize CPU usage.")

    # 2. Detect Multiple Loops on same collection (Single Pass Check)
    loop_count = len(re.findall(r'for\s*\(\s*Order\s+\w+\s*:\s*orders\s*\)', code))
    if loop_count > 1:
        tips.append(f"🔄 <b>Efficiency:</b> Detected {loop_count} separate loops over 'orders'. Merging them into one will save O(n) time.")

    # 3. Top-K sorting vs PriorityQueue
    if ".sorted(" in code and ".limit(" in code:
        tips.append("📉 <b>Algorithm:</b> You are using full Sort O(n log n). For Top-3, a <b>PriorityQueue</b> is faster O(n log k).")

    # 4. StringBuilder Check (String concatenation in loops)
    if re.search(r'for\s*\(.*\)\s*\{[^{}]*\+=\s*".*"', code) and "StringBuilder" not in code:
        tips.append("📦 <b>Memory:</b> String concatenation found in loop. Use <b>StringBuilder</b> to avoid excessive Garbage Collection.")

    # 5. Modern Java Collectors
    if "Collectors.toList()" in code:
        tips.append("✨ <b>Modern Java:</b> Use <b>Collectors.toUnmodifiableList()</b> if you don't need to change the list later.")

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

# --- EXISTING RUN LOGIC (DO NOT TOUCH) ---
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    language = data.get('lang', 'java') 

    try:
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
