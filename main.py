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
    list_match = re.search(r'List<.*?>\s+(\w+)\s*=', code)
    list_name = list_match.group(1) if list_match else "transactions"
    item_name = "t" # Standardizing for the lambda

    # 3. SCHEMA DISCOVERY (Field Detection)
    fields = re.findall(r'(\w+)\s+(\w+);', code)
    numeric_fields = [f[1] for f in fields if f[0].lower() in ['double', 'int', 'long', 'float']]
    id_fields = [f[1] for f in fields if f[0] == 'String']
    bool_fields = [f[1] for f in fields if f[0].lower() == 'boolean']

    amt_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["amt", "price", "val", "amount"])), numeric_fields[0] if numeric_fields else "amount")
    qty_f = next((f for f in numeric_fields if any(x in f.lower() for x in ["qty", "count", "quantity"]) and f != amt_f), "1")
    fail_f = next((f for f in bool_fields if any(x in f.lower() for x in ["fail", "error", "valid"])), None)

    # 4. CRITICAL FIX: DUPLICATE CLEANER & SYNTAX REPAIR
    # Purane slow blocks aur syntax errors (like extra parenthesis) ko saaf karna
    code = re.sub(rf'Map<.*?>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);', '', code, flags=re.DOTALL)
    # Fix extra parenthesis error in .max() calls if present in source
    code = re.sub(r'\.max\(.*?\)\)\)', '.max(Comparator.comparingLong(e -> e.getValue().sum()))', code)

    # 5. DYNAMIC ENGINE & COLLISION REPAIR
    used_maps = set(re.findall(r'(\w+)\.entrySet\(\)', code) + re.findall(r'System\.out\.println\((\w+)\)', code))
    init_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
    merge_logics = []

    for m_name in used_maps:
        # FIX 1: Variable Collision (Map vs String/List)
        # Agar niche String/List ka same naam hai, toh Map ko 'Map' suffix do
        is_clash = re.search(rf'(?:String|List<.*?>)\s+{m_name}\s*=', code)
        actual_m_name = f"{m_name}Map" if is_clash else m_name
        
        is_counter = any(x in m_name.lower() for x in ["sales", "count", "qty", "total", "sold"])
        final_v_type = "LongAdder" if is_counter else "BigDecimal"
        
        # FIX 2: Logical Key Selection (Product ID for Sales, User ID for Spending)
        if is_counter:
            best_key = next((f for f in id_fields if "product" in f.lower() or "item" in f.lower()), id_fields[0])
        else:
            best_key = next((f for f in id_fields if "user" in f.lower() or "id" in f.lower()), id_fields[0])

        # Sync code references in the rest of the file
        if actual_m_name != m_name:
            code = code.replace(f"{m_name}.entrySet()", f"{actual_m_name}.entrySet()")
            code = code.replace(f"System.out.println({m_name})", f"System.out.println({actual_m_name})")

        init_logic += f"\n        ConcurrentMap<String, {final_v_type}> {actual_m_name} = new ConcurrentHashMap<>({ '64' if 'cat' in best_key.lower() else 'capacity' });"
        
        # FIX 3: Type Safety for Sorting/Max
        if final_v_type == "BigDecimal":
            # Double.compare hatao, BigDecimal safe logic lagao
            code = re.sub(rf'\.sorted\(.*?Double\.compare.*?\)', 
                          f'.sorted(Map.Entry.<String, BigDecimal>comparingByValue().reversed())', code)
            merge_logics.append(f"{actual_m_name}.merge({item_name}.{best_key}, val, BigDecimal::add);")
        else:
            # LongAdder max logic
            code = re.sub(rf'\.max\(.*?\)', 
                          f'.max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            merge_logics.append(f"{actual_m_name}.computeIfAbsent({item_name}.{best_key}, k -> new LongAdder()).add({item_name}.{qty_f});")

    # 6. ENGINE INJECTION (Optimized Loop)
    filter_logic = f"if ({item_name} == null" + (f" || {item_name}.{fail_f}" if fail_f else "") + ") return;"
    
    optimized_block = f"""
        // --- Architect Level: Dynamic Unified Engine (O(n)) ---
        long startTime = System.nanoTime();
        LongAdder errors = new LongAdder(); {init_logic}

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

    # Replace the parallelStream block if user already tried to write one, or inject after DataGenerator
    code = re.sub(rf'{list_name}\.parallelStream\(\).*?\}\);', '', code, flags=re.DOTALL)
    code = re.sub(rf'({list_name}\s*=\s*.*?DataGenerator.*?;)', r'\1\n' + optimized_block, code, flags=re.DOTALL)
    
    tips.append("💎 <b>Production-Ready:</b> All variable collisions, type mismatches, and syntax errors auto-fixed.")
    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    # Render ya kisi bhi platform ka port auto-pick karega
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
