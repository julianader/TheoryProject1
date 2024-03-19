class NodeType:
    SYMBOL = 1
    CONCAT = 2
    OR = 3
    KLEENE = 4

class ExpTree:

    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
        self.left = None
        self.right = None
    

def buildTree(regex):
    stack = []
    for c in regex:
        if c.isalpha():
            stack.append(ExpTree(NodeType.SYMBOL, c))
        else:
            if c == "+":
                z = ExpTree(NodeType.OR)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == ".":
                z = ExpTree(NodeType.CONCAT)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == "*":
                z = ExpTree(NodeType.KLEENE)
                z.left = stack.pop()
            stack.append(z)

    return stack[0]

def inorder_traversal(et):
    if et._type == NodeType.SYMBOL:
        print(et.value)
    elif et._type == NodeType.CONCAT:
        inorder_traversal(et.left)
        print(".")
        inorder_traversal(et.right)
    elif et._type == NodeType.OR:
        inorder_traversal(et.left)
        print("+")
        inorder_traversal(et.right)
    elif et._type == NodeType.KLEENE:
        inorder_traversal(et.left)
        print("*")

def has_higher_precedence(a, b):
    precedence = ["+", ".", "*"]
    return precedence.index(a) > precedence.index(b)

def to_postfix(regex):
    temp = []
    for i in range(len(regex)):
        if i != 0 and (regex[i-1].isalpha() or regex[i-1] == ")" or regex[i-1] == "*")\
            and (regex[i].isalpha() or regex[i] == "("):
            temp.append(".")
        temp.append(regex[i])
    regex = temp
    
    stack = []
    output = ""

    for c in regex:
        if c.isalpha():
            output = output + c
            continue

        if c == ")":
            while len(stack) != 0 and stack[-1] != "(":
                output = output + stack.pop()
            stack.pop()
        elif c == "(":
            stack.append(c)
        elif c == "*":
            output = output + c
        elif len(stack) == 0 or stack[-1] == "(" or has_higher_precedence(c, stack[-1]):
            stack.append(c)
        else:
            while len(stack) != 0 and stack[-1] != "(" and not has_higher_precedence(c, stack[-1]):
                output = output + stack.pop()
            stack.append(c)

    while len(stack) != 0:
        output = output + stack.pop()

    return output

class State:
    def __init__(self):
        self.next_state = {}
        self.is_end = False 

def evaluate_regex(et):
    start_state, end_state = evaluate_regex_helper(et)
    end_state.is_end = True  # Mark the end state
    return start_state, end_state

def evaluate_regex_helper(et):
    if et._type == NodeType.SYMBOL:
        return evaluate_symbol(et)
    elif et._type == NodeType.CONCAT:
        return evaluate_concat(et)
    elif et._type == NodeType.OR:
        return evaluate_union(et)
    elif et._type == NodeType.KLEENE:
        return evaluate_kleene(et)

def evaluate_symbol(et):
    start_state = State()
    end_state   = State()
    
    start_state.next_state[et.value] = [end_state]
    return start_state, end_state

def evaluate_concat(et):
    left_start, left_end = evaluate_regex(et.left)
    right_start, right_end = evaluate_regex(et.right)

    left_end.next_state['epsilon'] = [right_start]
    return left_start, right_end

def evaluate_union(et):
    start_state = State()
    end_state   = State()

    up_nfa   = evaluate_regex(et.left)
    down_nfa = evaluate_regex(et.right)

    start_state.next_state['epsilon'] = [up_nfa[0], down_nfa[0]]
    up_nfa[1].next_state['epsilon'] = [end_state]
    down_nfa[1].next_state['epsilon'] = [end_state]

    return start_state, end_state

def evaluate_kleene(et):
    start_state = State()
    end_state   = State()

    sub_nfa = evaluate_regex(et.left)

    start_state.next_state['epsilon'] = [sub_nfa[0], end_state]
    sub_nfa[1].next_state['epsilon'] = [sub_nfa[0], end_state]

    return start_state, end_state

def print_transitions(state, states_visited, symbol_table):
    if state in states_visited:
        return

    states_visited.append(state)

    for symbol in list(state.next_state):
        line_output = "q" + str(symbol_table[state]) + "\t\t" + symbol + "\t\t\t"
        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
            line_output = line_output + "q" + str(symbol_table[ns]) + " "

        print(line_output)

        for ns in state.next_state[symbol]:
            print_transitions(ns, states_visited, symbol_table)

def print_transition_table(finite_automata):
    print("State\t\tSymbol\t\t\tNext state")
    end_state = None
    symbol_table = {finite_automata[0]: 0}

    def print_transitions(state, states_visited, symbol_table):
        nonlocal end_state
        if state in states_visited:
            return

        states_visited.append(state)

        for symbol in list(state.next_state):
            line_output = "q" + str(symbol_table[state]) + "\t\t" + symbol + "\t\t\t"
            for ns in state.next_state[symbol]:
                if ns not in symbol_table:
                    symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
                line_output = line_output + "q" + str(symbol_table[ns]) + " "
                if ns.is_end:
                    end_state = ns

            print(line_output)

            for ns in state.next_state[symbol]:
                print_transitions(ns, states_visited, symbol_table)

    print_transitions(finite_automata[0], [], symbol_table)
    print("\nEnd State: q" + str(symbol_table[end_state]) if end_state else "No end state found.")

regex_input = input("Enter regex: ")
postfix_regex = to_postfix(regex_input)
expr_tree = buildTree(postfix_regex)

nfa = evaluate_regex(expr_tree)
print_transition_table(nfa)
