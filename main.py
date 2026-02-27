import os
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/run', methods=['POST'])
def run_java():
    data = request.json
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')

    # 1. Code mein se Class ka naam dhoondna (Regex use karke)
    match = re.search(r'public\s+class\s+(\w+)', code)
    if match:
        class_name = match.group(1)
    else:
        # Agar public class nahi hai toh pehli class dhoondo
        match_any = re.search(r'class\s+(\w+)', code)
        class_name = match_any.group(1) if match_any else "HelloWorld"

    file_name = f"{class_name}.java"
    file_path = os.path.join("/tmp", file_name)

    # 2. File ko save karna
    with open(file_path, "w") as f:
        f.write(code)

    try:
        # 3. Compile (javac)
        compile_res = subprocess.run(['javac', '-d', '/tmp', file_path], capture_output=True, text=True)
        if compile_res.returncode != 0:
            return jsonify({"output": compile_res.stderr})

        # 4. Run (java)
        run_res = subprocess.run(['java', '-cp', '/tmp', class_name], input=stdin_data, capture_output=True, text=True)
        return jsonify({"output": run_res.stdout + run_res.stderr})

    except Exception as e:
        return jsonify({"output": "System Error: " + str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
