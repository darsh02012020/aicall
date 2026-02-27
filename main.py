import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # 1. ARCHITECT LEVEL IMPORTS
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. DYNAMIC DISCOVERY (No Hardcoded Names)
    # List name aur Item name dhoondna
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "dataList"
    
    item_match = re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "obj"

    # User ne jo Maps pehle se banaye hain unhe detect karna
    # Pattern: Map name aur uska Generic Type (BigDecimal ya LongAdder/Integer)
    map_info = re.findall(r'(?:Map|ConcurrentMap)<.*?,?\s*(\w+)>\s+(\w+)\s*=', code)
    # map_info format: [('BigDecimal', 'myMap'), ('LongAdder', 'counterMap')]

    # 3. DYNAMIC CAPACITY CALCULATION (No Hardcoded Numbers)
    if f"{list_name}.size()" in code and "capacity" not in code.lower():
        capacity_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
        # Insert capacity before the first Map declaration
        code = re.sub(r'(?:Map|ConcurrentMap)<.*?>\s+\w+\s*=', capacity_logic + r'\n        \0', code, count=1)
        tips.append("🧠 <b>Dynamic Memory:</b> Calculated Map capacity based on input list size.")

    # 4. UNIVERSAL TRANSFORMATION ENGINE
    if map_info and (".stream()" in code or ".parallelStream()" in code):
        tips.append(f"🚀 <b>Architect Flow:</b> Performed Context-Aware O(n) Optimization on <code>{list_name}</code>.")
        
        merge_logics = []
        for v_type, m_name in map_info:
            # Logic identify karna type ke basis par (Not Name!)
            if "BigDecimal" in v_type:
                # Automatic field detection (amount/value/price)
                val_field = "amount" if "amount" in code else "value" 
                merge_logics.append(f"{m_name}.merge({item_name}.getCategory(), val, BigDecimal::add);")
            elif any(x in v_type for x in ["LongAdder", "Integer", "Long"]):
                merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.getId(), k -> new LongAdder()).add({item_name}.getQuantity());")

        # Dynamic Calculation Logic
        is_bd = "BigDecimal" in code
        calc_source = "amount" if "amount" in code else "value"
        calc = f"{item_name}.{calc_source}" if is_bd else f"BigDecimal.valueOf({item_name}.{calc_source})"
        
        optimized_block = f"""
        // --- Architect Level: Unified Single-Pass Engine (Universal) ---
        long startTime = System.nanoTime();
        LongAdder errorCount = new LongAdder();

        {list_name}.parallelStream().forEach({item_name} -> {{
            try {{
                if ({item_name} == null) return;
                BigDecimal val = {calc}.multiply(BigDecimal.valueOf({item_name}.quantity));
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errorCount.increment();
            }}
        }});
        long endTime = System.nanoTime();
        System.out.printf("Processed in: %.2f ms | Errors: %d%n", (endTime - startTime) / 1e6, errorCount.sum());
        """
        
        # Redundant logic ko replace karna bina code delete kiye
        code = re.sub(r'//\s*---\s*Optimized.*?\}\);', optimized_block, code, flags=re.DOTALL)

    # 5. GENERIC LONGADDER HEALER (Type Based)
    for v_type, m_name in map_info:
        if "LongAdder" in v_type:
            pattern = rf'{m_name}\.entrySet\(\)\.stream\(\)\.max\(Map\.Entry\.comparingByValue\(\)\)'
            if re.search(pattern, code):
                code = re.sub(pattern, f'{m_name}.entrySet().stream().max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
                tips.append(f"🛠️ <b>Healed:</b> Fixed <code>LongAdder</code> comparison for <code>{m_name}</code>.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
