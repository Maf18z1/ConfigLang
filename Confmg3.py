import json
import argparse
import re
import sys

operator_precedence = {'+': 1, '-': 1, '*': 2, '/': 2, 'max': 3}

def infix_to_prefix(expression):
    def is_operator(c):
        return c in operator_precedence

    def precedence(op):
        return operator_precedence.get(op, 0)

    def apply_operator(operators, values):
        operator = operators.pop()
        right = values.pop()
        left = values.pop()
        values.append(f"^{{{operator} {left} {right}}}")
        

    def tokenize(expression):
        tokens = re.findall(r'\d+|[a-zA-Z]+|[-+*/()]', expression)
        return tokens

    def to_prefix(tokens):
        operators = []
        values = []
        for token in tokens:
            if (token.isdigit() or re.match(r'^[a-zA-Z_]\w*$', token)) and token!="max":
                values.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    apply_operator(operators, values)
                operators.pop()
            elif is_operator(token):
                while (operators and operators[-1] != '(' and
                        precedence(operators[-1]) >= precedence(token)):
                    apply_operator(operators, values)
                operators.append(token)

        while operators:
            apply_operator(operators, values)

        return values[-1]

    tokens = tokenize(expression)
    return to_prefix(tokens)

def evaluate_prefix_expression(expression, constants):
    expression = expression.replace("{", "").replace("}", "").replace("^", "")
    tokens = expression.split()
    stack = []
    for token in reversed(tokens):
        if token.isdigit():
            stack.append(int(token))
        elif token in constants:
            stack.append(constants[token])
        elif token == '+':
            stack.append(stack.pop() + stack.pop())
        elif token == '-':
            stack.append(stack.pop() - stack.pop())
        elif token == '*':
            stack.append(stack.pop() * stack.pop())
        elif token == '/':
            stack.append(stack.pop() / stack.pop())
        elif token == 'max':
            stack.append(max(stack.pop(), stack.pop()))
    return stack[0]

def parse_json_to_ukya(json_data):
    constants = {}
    result = []

    def detect_comment(key):
        if key.startswith("//"):
            return f"C {value.strip()}"
        elif key.startswith("/*") and key.endswith("*/"):
            content = value.strip()
            return f"=begin\n{content}\n=end"
        return None

    def process_value(value, key=None):
        if isinstance(value, dict):
            for key, val in value.items():
                if key[0]=="/":
                    combined = {key: val}
                    items += (f"\n{parse_json_to_ukya(combined)}")
                else:
                    items = (f"{process_value(val, key)}")

            return f"$[\n{items}\n]"

        elif isinstance(value, int):
            if key and re.match(r"^[_a-zA-Z]+$", key):
                constants[key] = value
                return f"global {key} = {value}"
            return str(value)

        elif isinstance(value,str) and ("^" not in value):
            if key and re.match(r"^[_a-zA-Z]+$", key):
                constants[key] = value
                return f"global {key} = '{value}'"
            return str(value)

        elif isinstance(value, str):
            if value.startswith("^{"):
                expression = value[2:-1]
                prefix_expr = infix_to_prefix(expression)
                result = evaluate_prefix_expression(prefix_expr, constants)
                return f"{prefix_expr} = {result}"
            return value
        else:
            raise ValueError(f"Unsupported value type: {value}")

    for key, value in json_data.items():
        comment = detect_comment(key)
        if comment:
            result.append(comment)
        else:
            result.append(process_value(value, key))

    return "\n".join(result)

def main():
    parser = argparse.ArgumentParser(description="JSON to UKYA converter")
    parser.add_argument("input_file", help="Path to the JSON file")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON syntax error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("File not found.")
        sys.exit(1)

    try:
        ukya_output = parse_json_to_ukya(json_data)
        print(ukya_output)
    except ValueError as e:
        print(f"Translation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
