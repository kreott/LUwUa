import random


env = {
    # your existing vars/functions
    "math": {
        "random": lambda *args: (
    random.randint(0, int(args[0])) if len(args) == 1 else
    random.randint(int(args[0]), int(args[1])) if len(args) == 2 else
    random.random()
        )
    }
}

functions = {}

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

def parse_value(token, env):
    # If token is a variable name in env, return its value
    if token in env:
        return env[token]

    if token == "twuu":
        return True
    elif token == "fawse":
        return False
    elif token == "nuwu":
        return None

    # Try to convert to int (including negative)
    try:
        return int(token)
    except ValueError:
        pass

    # Try to convert to float
    try:
        return float(token)
    except ValueError:
        pass

    # String literal
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    try:
        if '.' in token:
            return float(token)
        else: 
            return int(token)
    except ValueError:
        pass
    if token in env:
        return env[token]
    
    # If variable not found, raise error instead of returning raw string
    raise ValueError(f"Unknown token or variable: {token}")


def eval_expression(tokens, env):
    # Function call handling (keep as is)
    if len(tokens) >= 1 and '(' in tokens[0]:
        full_call = tokens[0]
        fn_name_end = full_call.find('(')
        fn_name = full_call[:fn_name_end]
        args_str = full_call[fn_name_end+1:-1]
        args = [eval_expression([arg.strip()], env) for arg in args_str.split(',')] if args_str else []

        parts = fn_name.split('.')
        fn = env
        try:
            for part in parts:
                fn = fn[part]
        except KeyError:
            raise ValueError(f"Function '{fn_name}' not found")

        return fn(*args)

    if not tokens:
        return None

    # Unary not
    if tokens[0] == "nawt":
        return not eval_expression(tokens[1:], env)

    # Logical operators
    logical_ops = [("and", lambda a,b: a and b), ("awnd", lambda a,b: a and b),
                   ("or", lambda a,b: a or b), ("owwo", lambda a,b: a or b)]
    for op, func in logical_ops:
        if op in tokens:
            i = tokens.index(op)
            left = eval_expression(tokens[:i], env)
            right = eval_expression(tokens[i+1:], env)
            return func(left, right)

    # Handle concatenation '..' as left-associative chain:
    if ".." in tokens:
        # Split tokens into parts separated by '..'
        parts = []
        current_part = []
        for t in tokens:
            if t == "..":
                # Evaluate current part and append
                parts.append(str(eval_expression(current_part, env)))
                current_part = []
            else:
                current_part.append(t)
        # Last part
        if current_part:
            parts.append(str(eval_expression(current_part, env)))

        return "".join(parts)

    # Handle other binary operators (only single operator here)
    ops = [
        ("==", lambda a, b: a == b),
        ("~=", lambda a, b: a != b),
        ("<=", lambda a, b: a <= b),
        (">=", lambda a, b: a >= b),
        ("<", lambda a, b: a < b),
        (">", lambda a, b: a > b),
        ("+", lambda a, b: a + b),
        ("-", lambda a, b: a - b),
        ("*", lambda a, b: a * b),
        ("/", lambda a, b: a / b),
    ]

    for op, func in ops:
        if op in tokens:
            i = tokens.index(op)
            left = eval_expression(tokens[:i], env)
            right = eval_expression(tokens[i+1:], env)
            return func(left, right)

    # Fallback single value
    return parse_value(tokens[0], env)



def run_block(lines, start=0):
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if line == "" or line.startswith("#"):
            i += 1
            continue
        

        tokens = line.split()
        #assign default values to avoid unboundlocalerror
        else_index = -1

        # local variable assignment
        if len(tokens) >= 4 and tokens[0] == "wocaw" and tokens[2] == "=":
            var_name = tokens[1]
            expr = tokens[3:]
            env[var_name] = eval_expression(expr, env)
            i += 1
            continue

        if tokens[0].startswith("woof"):
            joined_line = " ".join(tokens)
            start_paren = joined_line.find("(")
            end_paren = joined_line.rfind(")")
            expr_str = joined_line[start_paren + 1:end_paren].strip()

            # Proper tokenizer: handles quoted strings and '..'
            expr_tokens = []
            temp = ""
            in_string = False
            i = 0
            while i < len(expr_str):
                c = expr_str[i]
                if c == '"':
                    temp += c
                    i += 1
                    while i < len(expr_str):
                        temp += expr_str[i]
                        if expr_str[i] == '"':
                            break
                        i += 1
                    expr_tokens.append(temp.strip())
                    temp = ""
                    i += 1
                elif expr_str[i:i+2] == "..":
                    if temp.strip():
                        expr_tokens.append(temp.strip())
                    expr_tokens.append("..")
                    temp = ""
                    i += 2
                elif expr_str[i].isspace():
                    if temp.strip():
                        expr_tokens.append(temp.strip())
                        temp = ""
                    i += 1
                else:
                    temp += expr_str[i]
                    i += 1

            if temp.strip():
                expr_tokens.append(temp.strip())

            print(eval_expression(expr_tokens, env))
            i += 1
            continue


        if tokens[0] == "ifuwu":
            else_index = -1  # reset else_index per block

            # Find the full block lines of this if-elif-else
            start_idx = i
            end_idx = i + 1
            elif_indices = []

            while end_idx < len(lines):
                l = lines[end_idx].strip()
                if l.startswith("enduwu"):
                    break
                if l.startswith("ewseifuwu"):
                    elif_indices.append(end_idx)
                if l.startswith("othewwise"):
                    else_index = end_idx
                end_idx += 1

            # Check for 'denn' in the ifuwu line tokens
            if "denn" not in tokens:
                raise SyntaxError(f"Missing 'denn' keyword in ifuwu statement on line {start_idx + 1}")

            denn_pos = tokens.index("denn")
            condition_tokens = tokens[1:denn_pos]

            # Evaluate if condition
            if_condition = eval_expression(condition_tokens, env)
            if if_condition:
                block_end = elif_indices[0] if elif_indices else (else_index if else_index != -1 else end_idx)
                run_block(lines[start_idx + 1 : block_end])
                i = end_idx + 1
                continue

            # Evaluate ewseifuwu conditions
            executed = False
            for idx, elif_line_index in enumerate(elif_indices):
                line = lines[elif_line_index].strip()
                elif_tokens = line.split()

                if "denn" not in elif_tokens:
                    raise SyntaxError(f"Missing 'denn' keyword in ewseifuwu statement on line {elif_line_index + 1}")

                denn_pos = elif_tokens.index("denn")
                elif_condition_tokens = elif_tokens[1:denn_pos]

                elif_condition = eval_expression(elif_condition_tokens, env)

                next_block_start = (
                    elif_indices[idx + 1]
                    if idx + 1 < len(elif_indices)
                    else (else_index if else_index != -1 else end_idx)
                )

                if elif_condition:
                    run_block(lines[elif_line_index + 1 : next_block_start])
                    executed = True
                    break

            # If no previous blocks matched, run othewwise
            if not executed and else_index != -1:
                run_block(lines[else_index + 1 : end_idx])

            i = end_idx + 1
            continue



        
        # fowo block
        if tokens[0] == "fowo":
            # Parse syntax: fowo i = start, end [, step]
            try:
                loop_header = ' '.join(tokens[1:])
                var_name, rest = loop_header.split("=", 1)
                var_name = var_name.strip()

                # Support optional step
                parts = [p.strip() for p in rest.split(",")]
                start_val = eval_expression(parts[0].split(), env)
                end_val = eval_expression(parts[1].split(), env)
                step_val = eval_expression(parts[2].split(), env) if len(parts) > 2 else 1
            except Exception:
                print(f'UwU invalid fowo syntax: {" ".join(tokens)}')
                i += 1
                continue

            # Find enduwu
            end_idx = i + 1
            while end_idx < len(lines):
                if lines[end_idx].strip().startswith("enduwu"):
                    break
                end_idx += 1

            # Run the loop
            j = start_val
            while (j <= end_val and step_val > 0) or (j >= end_val and step_val < 0):
                env[var_name] = j
                run_block(lines[i + 1 : end_idx])
                j += step_val

            i = end_idx + 1
            continue




        # nyewfunctiown
        if tokens[0] == "nyewfunctiown":
            rest = line[len("nyewfunctiown "):]
            name_end = rest.find("(")
            func_name = rest[:name_end].strip()
            args_str = rest[name_end + 1:rest.find(")")]
            args = [a.strip() for a in args_str.split(",") if a.strip()]
            func_start = i + 1
            func_end = func_start
            while func_end < len(lines) and not lines[func_end].strip().startswith("enduwu"):
                func_end += 1

            def func(*passed_args):
                old_env = env.copy()
                for arg, val in zip(args, passed_args):
                    env[arg] = val
                try:
                    run_block(lines[func_start:func_end])
                except ReturnException as ret:
                    env.clear()
                    env.update(old_env)
                    return ret.value
                env.clear()
                env.update(old_env)
                return None

            functions[func_name] = func
            i = func_end + 1
            continue

        # function call (simple, no nested calls)
        if "(" in line and line.endswith(")"):
            func_name = line[:line.find("(")].strip()
            arg_str = line[line.find("(")+1:-1]
            args = [eval_expression([arg.strip()], env) for arg in arg_str.split(",") if arg.strip()]
            if func_name in functions:
                result = functions[func_name](*args)
                if result is not None:
                    print(result)
                i += 1
                continue

        # wetuwn statement
        if tokens[0] == "wetuwn":
            value = eval_expression(tokens[1:], env)
            raise ReturnException(value)

        # bweak statement (only works inside loops)
        if tokens[0] == "bweak":
            raise StopIteration()

        # variable assignment
        elif '=' in line:
            var, expr = line.split('=', 1)
            var = var.strip()
            expr = expr.strip()
            value = eval_expression(expr.split(), env)
            env[var] = value
            i += 1
            continue

        # wepeat ... untiw loop
        elif tokens[0] == "wepeat":
            repeat_lines = []
            i += 1
            # collect loop body lines until 'untiw' line
            while i < len(lines) and not lines[i].strip().startswith("untiw"):
                repeat_lines.append(lines[i])
                i += 1

            if i >= len(lines):
                print("UwU I don't see an 'untiw' after 'wepeat'!")
                return

            # get the condition tokens from the untiw line
            untiw_line = lines[i].strip()
            condition_tokens = untiw_line.split()[1:]

            # run the loop until the condition is True
            while not eval_expression(condition_tokens, env):
                run_block(repeat_lines)

            i += 1
            continue

        # fallback unknown line
        print(f"UwU I don't understand this line: {line}")
        i += 1


def main():
    with open("script.luwua", "r") as f:
        lines = f.readlines()
    try:
        run_block(lines)
    except StopIteration:
        pass

if __name__ == "__main__":
    main()
