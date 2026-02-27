import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
            
            # Added timeout for safety
            run_res = subprocess.run(
                ['python3', file_path], 
                input=stdin_data, 
                capture_output=True, 
                text=True,
                timeout=10 # Program 10s se zyada nahi chalega
            )
            return jsonify({"output": run_res.stdout + run_res.stderr})

        # --- JAVA LOGIC ---
        else:
            # Enhanced regex to find class name safely
            match = re.search(r'public\s+class\s+(\w+)', code)
            if not match:
                match = re.search(r'class\s+(\w+)', code)
            
            class_name = match.group(1) if match else "Main"
            file_path = f"/tmp/{class_name}.java"
            
            with open(file_path, "w") as f:
                f.write(code)

            # Compile with Optimization
            # -g:none flag debug info hata deta hai (file size optimized)
            compile_res = subprocess.run(['javac', '-g:none', '-d', '/tmp', file_path], capture_output=True, text=True)
            if compile_res.returncode != 0:
                return jsonify({"output": "Compile Error:\n" + compile_res.stderr})

            # Run with JVM Performance Flags
            # -Xmx128m: Memory limit (Best for Render Free Tier)
            # -XX:+TieredCompilation: Fast startup for small & large programs
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
    # Render usually provides PORT env variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
