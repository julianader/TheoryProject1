import sys

states = 0

def checkformat(y):
    if (y < 48 or y > 57) and (y < 97 or y > 122) and (y < 65 or y > 90):
        return False
    return True

def get_pre(ch):
    if ch in ['+']:
        return 1
    elif ch in ['*']:
        return 2
    elif ch in ['.']:
        return 3
    elif ch in ['(']:
        return 4
    else:
        return 0  # Default return value for unrecognized operators


def shunt(x):
    stack = []
    outstring = ""
    for i in x:
        ch = i
        if checkformat(ord(ch)):
            outstring = outstring + ch
        elif ch == '(':
            stack.insert(len(stack), ch)
        elif ch == ')':
            while len(stack) > 0 and stack[len(stack) - 1] != '(':
                outstring = outstring + stack[len(stack) - 1]
                stack.pop(len(stack) - 1)
            stack.pop(len(stack) - 1)
        else:
            while len(stack) > 0 and get_pre(ch) >= get_pre(stack[len(stack) - 1]):
                outstring = outstring + stack[len(stack) - 1]
                stack.pop(len(stack) - 1)
            stack.insert(len(stack), ch)
    while len(stack) > 0:
        outstring = outstring + stack[len(stack) - 1]
        stack.pop(len(stack) - 1)
    return outstring

def pars_str(x):
    res = []
    for i in range(len(x) - 1):
        res.append(x[i])
        if checkformat(ord(x[i])) and checkformat(ord(x[i + 1])):
            res.append('.')
        elif x[i] == ')' and x[i + 1] == '(':
            res.append('.')
        elif checkformat(ord(x[i + 1])) and x[i] == ')':
            res.append('.')
        elif x[i + 1] == '(' and checkformat(ord(x[i])):
            res.append('.')
        elif x[i] == '*' and (checkformat(ord(x[i + 1])) or x[i + 1] == '('):
            res.append('.')
    if len(x) > 0:
        check = x[len(x) - 1]
        if check != res[len(res) - 1]:
            res.append(check)
    return ''.join(res)

def NFA_sym(ch):
    global letters
    letters.update(set({ch}))
    global states
    val = ["Q{}".format(states), ch, "Q{}".format(states + 1)]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    states = states + 2
    ret = list(["Q{}".format(states - 2), "Q{}".format(states - 1)])
    return ret

def nfa_unio(nfa1, nfa2):
    global states
    val = ["Q{}".format(states), '$', nfa1[0]]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = ["Q{}".format(states), '$', nfa2[0]]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = [nfa1[1], '$', "Q{}".format(states + 1)]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = [nfa2[1], '$', "Q{}".format(states + 1)]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    states = states + 2
    return ["Q{}".format(states - 2), "Q{}".format(states - 1)]

def loop(nfa1):
    global states
    val = [nfa1[1], '$', nfa1[0]]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = ["Q{}".format(states), '$', nfa1[0]]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = [nfa1[1], '$', "Q{}".format(states + 1)]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    val = ["Q{}".format(states), '$', "Q{}".format(states + 1)]
    nfa["transition_function"].insert(len(nfa["transition_function"]), val)
    states = states + 2
    return ["Q{}".format(states - 2), "Q{}".format(states - 1)]

def concatenation(nfa1, nfa2):
    global states
    indx = len(nfa['transition_function'])
    val = [nfa1[1], '$', nfa2[0]]
    nfa['transition_function'].insert(indx, val)
    return [nfa1[0], nfa2[1]]
def re2nfa(x):
    stack = []
    for i in x:
        if checkformat(ord(i)):
            stack.append(NFA_sym(i))
        elif i == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            xt = nfa_unio(nfa1, nfa2)
            stack.append(xt)
        elif i == "*":
            xt = loop(stack.pop())
            stack.append(xt)
        else:
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            xt = concatenation(nfa1, nfa2)
            stack.append(xt)
    nfa["start_states"] = [stack[0][0]]
    nfa["final_states"] = [stack[0][1]]


def simulate_NFA(input_string, current_states, transition_function, visited_states=None):
    if visited_states is None:
        visited_states = set()

    if len(input_string) == 0:
        return current_states

    next_states = set()
    for state in current_states:
        for transition in transition_function:
            if transition[0] == state and (transition[1] == input_string[0] or transition[1] == '$'):
                next_states.add(transition[2])

    epsilon_closure = set(next_states)
    for state in next_states:
        if state not in visited_states:
            visited_states.add(state)
            epsilon_closure.update(simulate_NFA(input_string, [state], transition_function, visited_states))
    
    return epsilon_closure



letters = set({})

x = input("Enter a regular expression: ")
nfa = {}
nfa["states"] = []
nfa["letters"] = []
nfa["transition_function"] = []

x = pars_str(x)
x = shunt(x)
re2nfa(x)

s = set({})
for x in range(len(nfa["transition_function"])):
    s.update(set({nfa["transition_function"][x][0]}))
    s.update(set({nfa["transition_function"][x][2]}))

templis = list(letters)
nfa["letters"] = templis
s = list(s)
s.sort(key=lambda a: int(a[1:]))
nfa["states"] = s

print("NFA states:", nfa["states"])
print("NFA transition function:", nfa["transition_function"])
print("NFA letters:", nfa["letters"])
print("NFA start states:", nfa["start_states"])
print("NFA final states:", nfa["final_states"])

# Testing
test_string = input("Enter a string to test: ")
result_states = simulate_NFA(test_string, nfa["start_states"], nfa["transition_function"])
if any(state in nfa["final_states"] for state in result_states):
    print("String matches the regular expression.")
else:
    print("String does not match the regular expression.")
