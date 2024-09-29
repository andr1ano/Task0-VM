import math
import json
import pickle

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

def parse_json_commands(json_text):
    commands = []
    data = json.loads(json_text)

    entry_point = data.get("$entrypoint$")
    if entry_point:
        for command in entry_point:
            op_code = command["op"]
            arg = command.get("arg", "")
            if arg:
                arg = f'"{arg}"'
            commands.append((op_code, (arg,)))

    return commands

class VM:
    def __init__(self, input_fn=None, print_fn=None):
        self.stack = []
        self.variables = {}
        self.input_fn = input_fn or input
        self.print_fn = print_fn or print
        self.labels = {}
        self.instruction_pointer = 0
        self.code = 0
        self.entry_code = 0
        self.call_stack = []

    def run_code_from_json(self, json_file_path):

        with open(json_file_path, 'r') as file:
            json_text = file.read()

        commands = parse_json_commands(json_text)
        return self.run_code(commands)

    def run_code(self, code: list):
        self.code = code

        if isinstance(code, dict) and code:
            for code_block in code.values():
                self.parse_labels(code_block)

            self.entry_code = code["$entrypoint$"]

            while self.instruction_pointer < len(self.entry_code):
                op_code, args = self.entry_code[self.instruction_pointer]
                self.execute_instruction(op_code, args)
                self.instruction_pointer += 1

        else:
            self.parse_labels(code)
            while self.instruction_pointer < len(code):
                op_code, args = self.code[self.instruction_pointer]
                self.execute_instruction(op_code, args)
                self.instruction_pointer += 1

        return self.stack, self.variables

    def parse_labels(self, code):
        for index, (op_code, args) in enumerate(code):
            if op_code == 'LABEL':
                label_name = args[0].strip('"')
                self.labels[label_name] = index

    def execute_instruction(self, op_code, args):

        if op_code == 'LOAD_CONST':
            if args[0].startswith('"') and args[0].endswith('"'):
                self.stack.append(args[0].strip('"'))
            else:
                try:
                    self.stack.append(int(args[0]))
                except ValueError:
                    self.stack.append(float(args[0]))

        elif op_code == 'INPUT_STRING':
            user_input = self.input_fn("Enter a string: ")
            self.stack.append(user_input)

        elif op_code == 'INPUT_NUMBER':
            user_input = self.input_fn("Enter a number: ")
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

        elif op_code == 'EQ':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a == b else 0)

        elif op_code == 'NEQ':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a != b else 0)

        elif op_code == 'GT':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a > b else 0)

        elif op_code == 'LT':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a < b else 0)

        elif op_code == 'GE':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a >= b else 0)

        elif op_code == 'LE':
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(1 if a <= b else 0)

        elif op_code == 'JMP':
            label_name = args[0].strip('"')
            self.instruction_pointer = self.labels[label_name]

        elif op_code == 'CJMP':
            label_name = args[0].strip('"')
            condition = self.stack.pop()
            if condition == 1:
                self.instruction_pointer = self.labels[label_name]

        elif op_code == 'LABEL':
            pass

        elif op_code == 'CALL':
            func = self.stack.pop()
            self.call_stack.append((self.entry_code, self.instruction_pointer, self.variables.copy()))
            self.entry_code = self.code[func]
            self.instruction_pointer = -1
            self.variables = {}

        elif op_code == 'RET':
            self.entry_code, self.instruction_pointer, self.variables = self.call_stack.pop()

        return self.stack, self.variables

    def dump_stack(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.stack, file)

    def load_stack(self, filename):
        with open(filename, 'rb') as file:
            self.stack = pickle.load(file)

    def dump_memory(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.variables, file)

    def load_memory(self, filename):
        with open(filename, 'rb') as file:
            self.variables = pickle.load(file)