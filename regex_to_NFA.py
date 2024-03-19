import sys

class Automata:

    # NFA Constructor
    def __init__(self, language = set(['0', '1'])):
        self.states = set()
        self.startstate = None
        self.finalstates = []
        self.transitions = dict()
        self.language = language

    @staticmethod
    # Get epsilon
    def epsilon():
        return "eps"

    # Set starting state (always 1)
    def setstartstate(self, state):
        self.startstate = state
        self.states.add(state)

    # Add to final states list
    def addfinalstates(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    # Add transition to transitions dictionary
    def addtransition(self, fromstate, tostate, inp):
        if isinstance(inp, str):
            inp = set([inp])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[fromstate][tostate].union(inp)
            else:
                self.transitions[fromstate][tostate] = inp
        else:
            self.transitions[fromstate] = {tostate : inp}
    
    # Call addtransition method recursively
    def addtransition_dict(self, transitions):
        for fromstate, tostates in list(transitions.items()):
            for state in tostates:
                self.addtransition(fromstate, state, tostates[state])

    # Create a transitions set and return it
    def gettransitions(self, state, key):
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

    # Get epsilon closure
    def getEClose(self, findstate):
        allstates = set()
        states = set([findstate])
        while len(states)!= 0:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if Automata.epsilon() in self.transitions[state][tns] and tns not in allstates:
                        states.add(tns)
        return allstates

    # Write NFA data to file
    # Starting state is 1 so decrement all states by 1
    def display(self):
        outputfile = open(sys.argv[2], "a")
        outputfile.write(str(len(self.states)))
        outputfile.write("\n")
        for state in self.finalstates:
            outputfile.write(str(state - 1))
        outputfile.write("\n")
        for fromstate, tostates in list(self.transitions.items()):
            doOnce = True
            for state in tostates:
                for char in tostates[state]:
                    if len(tostates) > 1 and doOnce:
                        outputfile.write(str(fromstate - 1) + " " + str(char))
                        for stateaux in tostates:
                            outputfile.write(" " + str(stateaux - 1))
                        doOnce = False
                    elif len(tostates) == 1:
                        outputfile.write(str(fromstate - 1) + " " + str(char) + " " + str(state - 1))
            outputfile.write("\n")
        outputfile.close()
    def test_string(self, input_string):
        current_states = self.getEClose(self.startstate)  # Get epsilon closure of the start state

        # Check if the start state is a final state and the input string is empty
        if input_string == "" and self.startstate in self.finalstates:
            return True

        for symbol in input_string:
            next_states = set()
            for state in current_states:
                next_states |= self.gettransitions(state, symbol)  # Union of transitions from current states
            current_states = set()
            for state in next_states:
                current_states |= self.getEClose(state)  # Get epsilon closure of next states
        # Check if any of the final states is in the current set of states
        for final_state in self.finalstates:
            if final_state in current_states:
                return True  # String is valid
        return False  # String is not valid
    # Instantiate a semi-copy Automata object and return it
    def newBuildFromNumber(self, startnum):
        translations = {}
        for i in list(self.states):
            translations[i] = startnum
            startnum += 1
        rebuild = Automata(self.language)
        rebuild.setstartstate(translations[self.startstate])
        rebuild.addfinalstates(translations[self.finalstates[0]])
        for fromstate, tostates in list(self.transitions.items()):
            for state in tostates:
                rebuild.addtransition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    # Instantiate a semi-copy Automata object using existing states and return it
    def newBuildFromEquivalentStates(self, equivalent, pos):
        rebuild = Automata(self.language)
        for fromstate, tostates in list(self.transitions.items()):
            for state in tostates:
                rebuild.addtransition(pos[fromstate], pos[state], tostates[state])
        rebuild.setstartstate(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addfinalstates(pos[s])
        return rebuild

class BuildAutomata:

    # Build basic automata part with 2 state
    @staticmethod
    def basicstruct(inp):
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setstartstate(state1)
        basic.addfinalstates(state2)
        basic.addtransition(1, 2, inp)
        return basic

    # Build automata part when input is <|>
    @staticmethod
    def unionstruct(a, b):
        [a, m1] = a.newBuildFromNumber(2)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2
        union = Automata()
        union.setstartstate(state1)
        union.addfinalstates(state2)
        union.addtransition(union.startstate, a.startstate, Automata.epsilon())
        union.addtransition(union.startstate, b.startstate, Automata.epsilon())
        union.addtransition(a.finalstates[0], union.finalstates[0], Automata.epsilon())
        union.addtransition(b.finalstates[0], union.finalstates[0], Automata.epsilon())
        union.addtransition_dict(a.transitions)
        union.addtransition_dict(b.transitions)
        return union

    # Build automata part when input is <concat> or <.>
    @staticmethod
    def dotstruct(a, b):
        [a, m1] = a.newBuildFromNumber(1)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2-1
        dot = Automata()
        dot.setstartstate(state1)
        dot.addfinalstates(state2)
        dot.addtransition(a.finalstates[0], b.startstate, Automata.epsilon())
        dot.addtransition_dict(a.transitions)
        dot.addtransition_dict(b.transitions)
        return dot

    # Build automata part with kleene star
    @staticmethod
    def starstruct(a):
        [a, m1] = a.newBuildFromNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setstartstate(state1)
        #star.addfinalstates(state1)  # Set start state as final state to allow empty string
        star.addfinalstates(state2)
        star.addtransition(star.startstate, a.startstate, Automata.epsilon())
        star.addtransition(star.startstate, star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], a.startstate, Automata.epsilon())
        star.addtransition_dict(a.transitions)
        return star

class NFAfromRegex:

    # NFA from Regex Parser constructor
    def __init__(self, regex):
        self.star = '*'
        self.positive_closure = '+'
        self.union = '|'
        self.dot = '.'
        self.openingBracket = '('
        self.closingBracket = ')'
        self.operators = [self.union, self.dot]
        self.regex = regex
        self.alphabet = [chr(i) for i in range(65,91)]
        self.alphabet.extend([chr(i) for i in range(97,123)])
        self.alphabet.extend([chr(i) for i in range(48,58)])
        self.buildNFA()

    # Return NFA object
    def getNFA(self):
        return self.nfa

    # Call main display method
    def displayNFA(self):
        self.nfa.display()

    # Main workspace for parsing and creating NFA from regex
    # Parse regex input
    # Call build methods after processing and join the automatas
    def buildNFA(self):
        language = set()
        self.stack = []
        self.automata = []
        previous = ":eps:"
        for char in self.regex:
            if char in self.alphabet:
                language.add(char)
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star, self.positive_closure]):
                    self.addOperatorToStack(self.dot)
                self.automata.append(BuildAutomata.basicstruct(char))
            elif char == self.openingBracket:
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star, self.positive_closure]):
                    self.addOperatorToStack(self.dot)
                self.stack.append(char)
            elif char == self.closingBracket:
                while(1):
                    o = self.stack.pop()
                    if o == self.openingBracket:
                        break
                    elif o in self.operators:
                        self.processOperator(o)
            elif char == self.star:
                self.processOperator(char)
            elif char == self.positive_closure:
                self.processOperator(char)
            elif char in self.operators:
                self.addOperatorToStack(char)
            previous = char

        while len(self.stack) != 0:
            op = self.stack.pop()
            self.processOperator(op)

        self.nfa = self.automata.pop()
        self.nfa.language = language

    # Add to stack and check operator
    def addOperatorToStack(self, char):
        while(1):
            if len(self.stack) == 0:
                break
            top = self.stack[len(self.stack)-1]
            if top == self.openingBracket:
                break
            if top == char or top == self.dot:
                op = self.stack.pop()
                self.processOperator(op)
            else:
                break
        self.stack.append(char)

    # Check which operator is given and build automata part for each case
    def processOperator(self, operator):
        if operator == self.star:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.starstruct(a))
        elif operator == self.positive_closure:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.dotstruct(a, BuildAutomata.starstruct(a)))
        elif operator in self.operators:
            a = self.automata.pop()
            b = self.automata.pop()
            if operator == self.union:
                self.automata.append(BuildAutomata.unionstruct(b,a))
            elif operator == self.dot:
                self.automata.append(BuildAutomata.dotstruct(b,a))
if __name__ == "__main__":
    regex = input("Enter the regex: ")
    nfa_builder = NFAfromRegex(regex)
    nfa = nfa_builder.getNFA()

    while True:
        test_string = input("Enter a string to test (or 'quit' to exit): ")
        if test_string.lower() == 'quit':
            break
        if nfa.test_string(test_string):
            print(f"'{test_string}' is valid for the regex '{regex}'.")
        else:
            print(f"'{test_string}' is not valid for the regex '{regex}'.")