def parse_string(text):
    opcodes = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        op_code = parts[0]
        arg = tuple(parts[1:]) if len(parts) > 1 else ()

        opcodes.append((op_code, arg))

    return opcodes


import math


class VM:
    def __init__(self, input_fn=None, print_fn=None):
        self.stack = []
        self.variables = {}
        self.input_fn = input_fn or input
        self.print_fn = print_fn or print

    def run_code(self, code: list):
        for op_code, args in code:
            if op_code == 'LOAD_CONST':
                try:
                    if args[0].startswith('"') and args[0].endswith('"'):
                        self.stack.append(args[0].strip('"'))
                    else:
                        self.stack.append(int(args[0]))
                except ValueError:
                    self.stack.append(float(args[0]))

            elif op_code == 'INPUT_STRING':
                user_input = self.input_fn("Enter a string: ")
                self.stack.append(user_input)

            elif op_code == 'INPUT_NUMBER':
                user_input = float(self.input_fn("Enter a number: "))
                self.stack.append(user_input)

            elif op_code == 'PRINT':
                value = self.stack.pop()
                self.print_fn(value)

            elif op_code == 'LOAD_VAR':
                var_name = args[0].strip('"')
                self.stack.append(self.variables[var_name])

            elif op_code == 'STORE_VAR':
                var_name = args[0].strip('"')
                self.variables[var_name] = self.stack.pop()

            elif op_code == 'ADD':
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a + b)

            elif op_code == 'SUB':
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a - b)

            elif op_code == 'MUL':
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a * b)

            elif op_code == 'DIV':
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a / b)

            elif op_code == 'EXP':
                a = self.stack.pop()
                self.stack.append(math.exp(a))

            elif op_code == 'SQRT':
                a = self.stack.pop()
                self.stack.append(math.sqrt(a))

            elif op_code == 'NEG':
                a = self.stack.pop()
                self.stack.append(-a)

        return self.stack, self.variables

    def run_code_from_json(self, json_path: str):
        pass

    def dump_stack(self, pkl_path: str):
        import pickle
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.stack, f)

    def load_stack(self, pkl_path: str):
        import pickle
        with open(pkl_path, 'rb') as f:
            self.stack = pickle.load(f)

    def dump_memory(self, pkl_path: str):
        import pickle
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.variables, f)

    def load_memory(self, pkl_path: str):
        import pickle
        with open(pkl_path, 'rb') as f:
            self.variables = pickle.load(f)