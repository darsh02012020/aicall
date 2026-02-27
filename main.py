import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # 1. ARCHITECT IMPORTS
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. DYNAMIC VARIABLE DISCOVERY
    list_match = re.search(r'List<\w+>\s+(\w+)\s*=', code)
    list_name = list_match.group(1) if list_match else "inputList"
    
    item_match = re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "t"

    # 3. CLASS SCHEMA DISCOVERY
    fields_with_types = re.findall(r'(\w+)\s+(\w+);', code)
    numeric_fields = [f[1] for f in fields_with_types if f[0].lower() in ['double', 'int', 'long', 'bigdecimal', 'float']]
    id_fields = [f[1] for f in fields_with_types if f[0] == 'String']
    bool_fields = [f[1] for f in fields_with_types if f[0].lower() == 'boolean']

    amt_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["amt", "price", "val", "amount"])), numeric_fields[0] if numeric_fields else "amount")
    qty_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["qty", "count", "quantity"]) and f != amt_f), numeric_fields[1] if len(numeric_fields) > 1 else "1")
    fail_f = next((f for f in bool_fields if any(x in f.lower() for x in ["fail", "error", "valid"])), None)

    # 4. DEEP MAP DISCOVERY & CLEANER
    used_maps = set(re.findall(r'(\w+)\.entrySet\(\)', code) + re.findall(r'System\.out\.println\((\w+)\)', code))
    
    clean_patterns = [
        rf'ConcurrentMap<.*?>\s+\w+\s*=\s*new\s*ConcurrentHashMap.*?;',
        rf'Map<.*?>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);',
        rf'{list_name}\.(?:parallelStream|stream).*?;',
        rf'List<String>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);'
    ]
    for pattern in clean_patterns:
        code = re.sub(pattern, '', code, flags=re.DOTALL)

    # 5. DYNAMIC ENGINE & SORTING FIXER
    init_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
    merge_logics = []

    for m_name in used_maps:
        # Collision Check
        is_clashing = re.search(rf'(?:List<String>|String)\s+{m_name}\s*=', code)
        actual_m_name = f"{m_name}Map" if is_clashing else m_name
        
        is_counter = any(x in m_name.lower() for x in ["sales", "count", "qty", "total"])
        final_v_type = "LongAdder" if is_counter else "BigDecimal"
        
        # KEY MAPPING FIX: Accurate key selection
        best_key = next((f for f in id_fields if f.lower() in m_name.lower()), None)
        if not best_key:
            best_key = next((f for f in id_fields if ("product" in f.lower() or "item" in f.lower()) and is_counter), 
                       next((f for f in id_fields if "user" in f.lower() or "id" in f.lower()), id_fields[0]))
        
        init_logic += f"\n        ConcurrentMap<String, {final_v_type}> {actual_m_name} = new ConcurrentHashMap<>({ '64' if 'cat' in best_key.lower() else 'capacity' });"
        
        # Global Reference Update
        if actual_m_name != m_name:
            code = code.replace(f"{m_name}.entrySet()", f"{actual_m_name}.entrySet()")
            code = code.replace(f"System.out.println({m_name})", f"System.out.println({actual_m_name})")

        # FIXING SORTING/MAX LOGIC IN EXISTING CODE
        if final_v_type == "BigDecimal":
            # Fix BigDecimal sorting (Replace Double.compare)
            code = re.sub(rf'\.sorted\(.*?Double\.compare.*?\)', 
                          f'.sorted(Map.Entry.<String, BigDecimal>comparingByValue().reversed())', code)
            merge_logics.append(f"{actual_m_name}.merge({item_name}.{best_key}, val, BigDecimal::add);")
        else:
            # Fix LongAdder Max logic
            code = re.sub(rf'\.max\(Map\.Entry\.comparingByValue\(\)\)', 
                          f'.max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            merge_logics.append(f"{actual_m_name}.computeIfAbsent({item_name}.{best_key}, k -> new LongAdder()).add({item_name}.{qty_f});")

    # 6. FINAL BLOCK GENERATION
    filter_logic = f"if ({item_name} == null" + (f" || {item_name}.{fail_f}" if fail_f else "") + ") return;"
    
    optimized_block = f"""
        // --- Architect Level: Dynamic Unified Engine (O(n)) ---
        long startTime = System.nanoTime();
        LongAdder errors = new LongAdder();
        {init_logic}

        {list_name}.parallelStream().forEach({item_name} -> {{
            try {{
                {filter_logic}
                BigDecimal val = BigDecimal.valueOf({item_name}.{amt_f}).multiply(BigDecimal.valueOf({item_name}.{qty_f}));
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errors.increment();
            }}
        }});
        System.out.printf("Done in: %.2f ms | Faults: %d%n", (System.nanoTime() - startTime) / 1e6, errors.sum());
    """

    code = re.sub(rf'({list_name}\s*=\s*.*?DataGenerator.*?;)', r'\1\n' + optimized_block, code, flags=re.DOTALL)
    
    tips.append("🚀 <b>Full-Cycle Optimization:</b> Fixed Engine, Resolved Collisions, and Patched Sorting/Max logic for BigDecimal/LongAdder.")
    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
