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
    language = data.get('lang', 'java') # Frontend se language aayegi

    try:
        # --- PYTHON LOGIC ---
        if language == 'python':
            file_path = "/tmp/script.py"
            with open(file_path, "w") as f:
                f.write(code)
            
            run_res = subprocess.run(['python3', file_path], input=stdin_data, capture_output=True, text=True)
            return jsonify({"output": run_res.stdout + run_res.stderr})

        # --- JAVA LOGIC ---
        else:
            match = re.search(r'public\s+class\s+(\w+)', code)
            if not match:
                match = re.search(r'class\s+(\w+)', code)
            
            class_name = match.group(1) if match else "HelloWorld"
            file_path = f"/tmp/{class_name}.java"
            
            with open(file_path, "w") as f:
                f.write(code)

            # Compile
            compile_res = subprocess.run(['javac', '-d', '/tmp', file_path], capture_output=True, text=True)
            if compile_res.returncode != 0:
                return jsonify({"output": "Compile Error:\n" + compile_res.stderr})

            # Run
            run_res = subprocess.run(['java', '-cp', '/tmp', class_name], input=stdin_data, capture_output=True, text=True)
            return jsonify({"output": run_res.stdout + run_res.stderr})

    except Exception as e:
        return jsonify({"output": "System Error: " + str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
