import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # 1. ARCHITECT IMPORTS (Added dynamic set to avoid duplicates)
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. DYNAMIC VARIABLE DISCOVERY
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "inputList"
    
    item_match = re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "obj"

    # 3. CLASS SCHEMA DISCOVERY (MetaData Extraction)
    # Catching all fields and their types dynamically
    fields_with_types = re.findall(r'(\w+)\s+(\w+);', code)
    numeric_fields = [f[1] for f in fields_with_types if f[0].lower() in ['double', 'int', 'long', 'bigdecimal', 'float']]
    id_fields = [f[1] for f in fields_with_types if f[0] == 'String']

    # Smart Heuristics for Calculation
    amt_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["amt", "price", "val", "amount", "cost"])), numeric_fields[0] if numeric_fields else "amount")
    qty_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["qty", "count", "quantity", "unit"]) and f != amt_f), numeric_fields[1] if len(numeric_fields) > 1 else "1")

    # 4. MAP & TASK DISCOVERY
    map_info = re.findall(r'(?:Map|ConcurrentMap)<\s*\w+\s*,\s*(\w+)\s*>\s+(\w+)\s*=', code)
    
    # 5. GLOBAL CLEANER (N-Scans to 1-Scan)
    clean_patterns = [
        rf'Map<.*?>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);',
        rf'{list_name}\.stream\(\).*?\.forEach\(.*?\);',
        rf'List<String>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);',
        rf'//\s*\d+️⃣.*?\n' # Deletes old comment markers
    ]
    for pattern in clean_patterns:
        code = re.sub(pattern, '', code, flags=re.DOTALL)
    
    # 6. DYNAMIC ARCHITECT ENGINE GENERATION WITH SMART KEY MAPPING
    init_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
    merge_logics = []

    for v_type, m_name in map_info:
        final_v_type = "LongAdder" if any(x in v_type for x in ["Integer", "Long", "Int"]) else "BigDecimal"
        
        # --- ENHANCED: Context-Aware Key Mapping ---
        # Logic: Find best ID field based on Map name context
        best_key = None
        # Priority 1: Direct name match (category in revenueByCategory)
        best_key = next((f for f in id_fields if f.lower() in m_name.lower()), None)
        
        # Priority 2: Semantic match for LongAdder (usually productId or itemId)
        if not best_key and final_v_type == "LongAdder":
            best_key = next((f for f in id_fields if any(x in f.lower() for x in ["product", "item", "sku", "code"])), None)
        
        # Priority 3: Default to first available ID or generic 'id'
        if not best_key:
            best_key = next((f for f in id_fields if any(x in f.lower() for x in ["id", "key", "name"])), id_fields[0] if id_fields else "id")
        
        # Capacity logic: Small for categories, large for IDs
        m_cap = '64' if 'cat' in best_key.lower() or 'type' in best_key.lower() else 'capacity'
        init_logic += f"\n        ConcurrentMap<String, {final_v_type}> {m_name} = new ConcurrentHashMap<>({m_cap});"
        
        if final_v_type == "BigDecimal":
            merge_logics.append(f"{m_name}.merge({item_name}.{best_key}, val, BigDecimal::add);")
        else:
            merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.{best_key}, k -> new LongAdder()).add({item_name}.{qty_f});")

    # Dynamic Calculation Logic
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
                if ({item_name} == null || {item_name}.failed) return; 
                BigDecimal val = {calc_val};
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errors.increment();
            }}
        }});
        System.out.printf("Done in: %.2f ms | Faults: %d%n", (System.nanoTime() - startTime) / 1e6, errors.sum());
    """

    # Injecting the block (finds first method call or comment to replace)
    code = re.sub(rf'//\s*1️⃣.*|{list_name}\.(?:parallelStream|stream).*?;', optimized_block, code, flags=re.DOTALL, count=1)
    
    tips.append("🚀 <b>Architect Meta-Discovery:</b> All keys were dynamically mapped by correlating Map names with Class fields.")
    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
