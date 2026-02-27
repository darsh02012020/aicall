import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # 1. ARCHITECT IMPORTS (Ensuring everything is covered)
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. DYNAMIC VARIABLE DISCOVERY (No Hardcoding)
    # List name (e.g., 'transactions', 'orders', 'students')
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "inputList"
    
    # Lambda item name (e.g., 't ->', 'item ->', 'obj ->')
    item_match = re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "x"

    # 3. CLASS SCHEMA DISCOVERY (Dynamic Field Mapping)
    # Extracts all fields from the Java Class provided in input
    fields_with_types = re.findall(r'(String|double|int|long|BigDecimal|Float)\s+(\w+);', code)
    
    # Smart Mapping: Logic based on context, not just names
    # Finding Numeric fields for calculations
    numeric_fields = [f[1] for f in fields_with_types if f[0] in ['double', 'int', 'long', 'BigDecimal', 'Float']]
    # Finding String/ID fields for grouping
    id_fields = [f[1] for f in fields_with_types if f[0] == 'String']

    # Default heuristic if detection is fuzzy
    amt_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["amt", "price", "val", "amount", "cost"])), numeric_fields[0] if numeric_fields else "amount")
    qty_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["qty", "count", "quantity", "unit"]) and f != amt_f), numeric_fields[1] if len(numeric_fields) > 1 else "1")
    key_f = next((f for f in id_fields if any(x in f.lower() for x in ["id", "cat", "key", "name", "type"])), id_fields[0] if id_fields else "id")

    # 4. MAP & TASK DISCOVERY
    # Detects what maps the user wants to populate
    map_info = re.findall(r'(?:Map|ConcurrentMap)<\s*\w+\s*,\s*(\w+)\s*>\s+(\w+)\s*=', code)
    
    # 5. THE GLOBAL CLEANER (N-Scans to 1-Scan)
    # Removes any number of stream/groupingBy blocks
    clean_patterns = [
        rf'Map<.*?>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);',
        rf'{list_name}\.stream\(\).*?\.forEach\(.*?\);'
    ]
    for pattern in clean_patterns:
        if re.search(pattern, code, flags=re.DOTALL):
            code = re.sub(pattern, '', code, flags=re.DOTALL)
    
    tips.append(f"🧹 <b>Universal Cleaner:</b> Collapsed all redundant scans for <code>{list_name}</code>.")

    # 6. DYNAMIC ARCHITECT ENGINE GENERATION
    init_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
    merge_logics = []

    for v_type, m_name in map_info:
        # Convert simple Maps to Concurrent + Dynamic Capacity
        final_type = "LongAdder" if any(x in v_type for x in ["Integer", "Long", "Int"]) else "BigDecimal"
        init_logic += f"\n        ConcurrentMap<String, {final_type}> {m_name} = new ConcurrentHashMap<>(capacity);"
        
        # Build merge logic based on Type, not name
        if final_type == "BigDecimal":
            merge_logics.append(f"{m_name}.merge({item_name}.{key_f}, val, BigDecimal::add);")
        else:
            merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.{key_f}, k -> new LongAdder()).add({item_name}.{qty_f});")

    # Dynamic Calculation: BigDecimal safety
    calc_val = f"BigDecimal.valueOf({item_name}.{amt_f})"
    if qty_f != "1":
        calc_val += f".multiply(BigDecimal.valueOf({item_name}.{qty_f}))"

    optimized_block = f"""
        // --- Architect Level: Dynamic Unified Engine (O(n)) ---
        long startTime = System.nanoTime();
        LongAdder errors = new LongAdder();
        {init_logic}

        {list_name}.parallelStream().forEach({item_name} -> {{
            try {{
                if ({item_name} == null) return;
                BigDecimal val = {calc_val};
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errors.increment();
            }}
        }});
        System.out.printf("Done in: %.2f ms | Faults: %d%n", (System.nanoTime() - startTime) / 1e6, errors.sum());
    """

    # Inject the engine into the main method area
    code = re.sub(rf'// 1️⃣.*|{list_name}\.stream\(\).*?;', optimized_block, code, flags=re.DOTALL, count=1)

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
