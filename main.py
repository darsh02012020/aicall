from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route('/run', methods=['POST'])
def run_java():
    data = request.json
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')

    # Java file ka naam hamesha HelloWorld.java rakhenge
    file_name = "HelloWorld.java"
    with open(file_name, "w") as f:
        f.write(code)

    try:
        # Step 1: Compile
        compile_process = subprocess.run(['javac', file_name], capture_output=True, text=True)
        if compile_process.returncode != 0:
            return jsonify({"output": compile_process.stderr})

        # Step 2: Run with Input
        run_process = subprocess.run(['java', 'HelloWorld'], input=stdin_data, capture_output=True, text=True)
        return jsonify({"output": run_process.stdout + run_process.stderr})

    except Exception as e:
        return jsonify({"output": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)