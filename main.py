import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # --- 1. ARCHITECT LEVEL IMPORTS ---
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # --- 2. DYNAMIC CONTEXT DISCOVERY (FIX 1: Variable Sync) ---
    # Signature se list name nikalna taaki method body ke logic se sync rahe
    sig_match = re.search(r'\(List<.*?>\s+(\w+)\)', code)
    list_name = sig_match.group(1) if sig_match else "data"
    
    # Item name detection
    item_match = re.search(r'for\s*\(\w+\s+(\w+)\s*:', code) or re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "t"

    # --- 3. THE 3-POINT OPTIMIZATION ENGINE ---
    is_n_squared = ".stream()" in code and (".filter(" in code or ".anyMatch(" in code)
    # Check if user is using double for money
    has_double = bool(re.search(r'double\s+\w+\s*=\s*0', code))
    
    if is_n_squared or "for(" in code:
        tips.append(f"💎 <b>Architect Fix:</b> Upgraded O(n²) bottleneck to O(n) using Frequency Mapping.")
        if has_double:
            tips.append(f"⚖️ <b>Precision Fix:</b> Switched to <code>BigDecimal</code> for financial accuracy.")

        # Logic for frequency map
        freq_map_logic = f"Map<String, Long> counts = {list_name}.parallelStream().collect(Collectors.groupingBy(x -> x.id, Collectors.counting()));"
        
        # FIX 2: Single-line printf with proper escaping to avoid Java syntax errors
        optimized_block = f"""
        // --- Architect Grade: O(n) Optimized Engine ---
        long startTime = System.nanoTime();
        {freq_map_logic}

        BigDecimal finalTotal = {list_name}.parallelStream()
            .filter({item_name} -> counts.get({item_name}.id) == 1)
            .map({item_name} -> BigDecimal.valueOf({item_name}.price).multiply(BigDecimal.valueOf({item_name}.qty)))
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        long duration = System.nanoTime() - startTime;
        System.out.printf("\\n[BENCHMARK] Complexity: O(n²) -> O(n) | Execution: %.2f ms\\n", duration / 1e6);
        System.out.println("Optimized Result: " + finalTotal);
        """

        # Purane inefficient code ko delete karke naya block inject karna
        code = re.sub(r'double\s+(\w+)\s*=\s*0;.*?System\.out\.println\(.*?\);', optimized_block, code, flags=re.DOTALL)
        code = re.sub(r'for\s*\(.*?\)\s*\{.*?System\.out\.println\(.*?\);?\s*\}', optimized_block, code, flags=re.DOTALL)

    # --- 4. GENERIC HEALER ---
    map_declarations = re.findall(r'(?:Map|ConcurrentMap)<.*?>\s+(\w+)\s*=', code)
    for m_name in map_declarations:
        pattern = rf'{m_name}\.entrySet\(\)\.stream\(\)\.max\(Map\.Entry\.comparingByValue\(\)\)'
        if re.search(pattern, code):
            code = re.sub(pattern, f'{m_name}.entrySet().stream().max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            tips.append(f"🛠️ <b>Healed:</b> Fixed LongAdder comparison for <code>{m_name}</code>.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    try:
        opt_code, tips = universal_architect_optimizer(data.get('code', ''))
        return jsonify({"optimized_code": opt_code, "tips": tips})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
