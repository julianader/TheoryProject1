
import re
from copy import deepcopy, copy

def contain_each_other(str1, str2):
    count_str1_in_str2 = str2.count(str1)
    count_str2_in_str1 = str1.count(str2)
    containing = bool(count_str1_in_str2 + count_str2_in_str1)

    if not bool(count_str2_in_str1) and containing:
        str1, str2 = str2, str1

    return containing, str1, str2

def has_space(s):
    for char in s:
        if char.isspace():
            return True
    return False

def escape_re(iterable):
    for item in iterable:
        yield re.escape(item)

class RuleTreeNode:
    def __init__(self, value=None):
        self.value = value

    def children(self, pattern):
        for i in range(len(self.value)):
            if pattern.fullmatch(self.value[i][0]) and not self.value[i][1]:
                first_value = deepcopy(self.value)
                first_value[i][1] = True
                second_value = deepcopy(self.value)
                del second_value[i]
                return RuleTreeNode(first_value), RuleTreeNode(second_value)

class ContextFreeGrammar:
    def __init__(self,
                 variables=None,
                 terminals=None,
                 rules=None,
                 start_variable='S',
                 null_character='λ'):

        if variables is None:
            variables = set()
        elif hasattr(variables, '__iter__'):
            variables = {*variables}
        else:
            raise TypeError("Variables must be iterable.")

        if isinstance(rules, dict):
            variables |= {*rules}
            rules = {(var, var_rule) for var, var_rules in rules.items() for var_rule in var_rules}
        elif hasattr(rules, '__iter__'):
            rules = {*rules}
        else:
            raise TypeError("Rules must be a collection or a dictionary.")

        if isinstance(terminals, set):
            terminals = terminals
        elif hasattr(terminals, '__iter__'):
            terminals = {*terminals}
        else:
            raise TypeError("Terminals must be iterable.")

        self.variables = variables
        self.terminals = terminals
        self.start_variable = start_variable
        self.null_character = null_character
        self.accepts_null = None
        self.rules = rules
        self._is_chomsky = None
        self._cnf = None

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, new_variables):
        if type(new_variables) is not set:
            raise TypeError("Variables must be a set.")

        for variable in new_variables:
            if type(variable) is not str:
                raise TypeError("Variables must be strings.")

        for variable in new_variables:
            if has_space(variable):
                raise ValueError("Variables cannot contain white spaces.")

        new_variables_list = list(new_variables)
        for i in range(len(new_variables_list) - 1):
            for j in range(i + 1, len(new_variables_list)):
                if contain_each_other(new_variables_list[i], new_variables_list[j]):
                   raise ValueError("Terminals cannot contain each other.")

        self._variables = frozenset(new_variables)
        self._is_chomsky = None
        self._cnf = None
        self.accepts_null = None

    @property
    def terminals(self):
        return self._terminals

    @terminals.setter
    def terminals(self, new_terminals):
        if type(new_terminals) is not set:
            raise TypeError("Terminals must be a set.")

        for terminal in new_terminals:
            if type(terminal) is not str:
                raise TypeError("Terminals must be strings.")

        for terminal in new_terminals:
            if has_space(terminal):
                raise ValueError("Terminals cannot contain white spaces.")

        new_terminals_list = list(new_terminals)
        for i in range(len(new_terminals_list) - 1):
            for j in range(i + 1, len(new_terminals_list)):
                if contain_each_other(new_terminals_list[i], new_terminals_list[j]):
                   raise ValueError("Terminals cannot contain each other.")

        self._terminals = frozenset(new_terminals)
        self._is_chomsky = None
        self._cnf = None
        self.accepts_null = None

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, new_rules):
        if type(new_rules) is not set:
            raise TypeError("Rules must be a set.")

        for rule in new_rules:
            if type(rule) is not tuple:
                raise TypeError("Rules must be tuples.")
            if len(rule) != 2:
                raise TypeError("Rules must contain two elements.")
            if type(rule[0]) is not str or type(rule[1]) is not str:
                raise TypeError("Rule elements must be strings.")
            if has_space(rule[0]) or has_space(rule[1]):
                raise ValueError("Rules cannot contain white spaces.")

        # Validation and processing logic...

    @property
    def start_variable(self):
        return self._start_variable

    @start_variable.setter
    def start_variable(self, new_start_variable):
        if type(new_start_variable) is not str:
            raise TypeError("Start variable must be a string.")

        if new_start_variable not in self.variables:
            raise ValueError("Start variable must be in the variables set.")

        self._start_variable = new_start_variable
        self._is_chomsky = None
        self._cnf = None
        self.accepts_null = None

    @property
    def null_character(self):
        return self._null_character

    @null_character.setter
    def null_character(self, new_null_character):
        if type(new_null_character) is not str:
            raise TypeError("Null character must be a string.")

        if new_null_character not in self.terminals:
            raise ValueError("Null character must be in the terminals set.")

        self._null_character = new_null_character
        self._is_chomsky = None
        self._cnf = None
        self.accepts_null = None

    def remove_null_rules(self):
        """
        Removes null rules from grammar.
        """
        nullable_vars = {rule[0] for rule in self.rules if rule[1] == self.null_character}

        if not nullable_vars:
            return

        while True:
            is_nullable = re.compile('({})+'.format('|'.join(re.escape(var) for var in nullable_vars)))
            new_nullable_vars = {rule[0] for rule in self.rules if is_nullable.fullmatch(rule[1])}
            new_set = nullable_vars | new_nullable_vars
            if new_set == nullable_vars:
                break
            nullable_vars = new_set

        contains_nullable = re.compile('({})'.format('|'.join(re.escape(var) for var in nullable_vars)))

        new_rules = set()

        for rule in self.rules:
            if rule[1] == self.null_character:
                continue
            splits = contains_nullable.split(rule[1])
            if splits[0] != rule[1]:
                splits = [[x, False] for x in splits if x != '']

                def tree_search(node):
                    if not node.value:
                        return
                    children = node.children(contains_nullable)
                    if not children:
                        new_rules.add((rule[0], (''.join((val[0] for val in node.value)))))
                    else:
                        for child in children:
                            tree_search(child)

                tree_search(RuleTreeNode(splits))
            new_rules.add(rule)

        self._rules = frozenset(new_rules)

    def remove_unit_rules(self):
        """
        Removes unit rules from grammar.
        """

        def get_related_unit_rules(var, var_related_unit_rules):
            prev_related_unit_rules = copy(var_related_unit_rules)
            var_unit_rules = self._var_unit_rules(var)
            var_related_unit_rules |= var_unit_rules
            for unit_var in var_unit_rules - prev_related_unit_rules:
                get_related_unit_rules(unit_var, var_related_unit_rules)

        related_unit_rules = dict([(var, set()) for var in self.variables])

        for var in self.variables:
            get_related_unit_rules(var, related_unit_rules[var])
            related_unit_rules[var] -= {var}

        non_unit_rules = {(var, rule) for var in self.variables for rule in self._var_none_unit_rules(var)}

        for var in self.variables:
            for related_var in related_unit_rules[var]:
                non_unit_rules |= {(var, related_var_non_unit_rule) for related_var_non_unit_rule
                                   in self._var_none_unit_rules(related_var)}

        self._rules = frozenset(non_unit_rules)

    def reduct(self):
        """
        Reducts grammar's rules.
        """
        """
        Phase 1
        """
        v1 = set()
        while True:
            v1_union_t = v1 | self.terminals
            v1_union_t_pattern = re.compile('({})+'.format('|'.join(re.escape(val) for val in v1_union_t)))
            prev_v1 = deepcopy(v1)
            for var in self.variables:
                if {rule for rule in self.rules if rule[0] == var and v1_union_t_pattern.fullmatch(rule[1])}:
                    v1.add(var)
            if prev_v1 == v1:
                break
        p1 = {rule for rule in self.rules if v1_union_t_pattern.fullmatch(rule[1])}

        is_rule = re.compile('({})'.format('|'.join(re.escape(val) for val in v1)))

        """
        Phase 2
        """

        def get_related_vars(var, related_vars):
            var_related_vars = set()
            for rule in {rule[1] for rule in p1 if rule[0] == var}:
                var_related_vars |= set(is_rule.findall(rule))

            prev_related_vars = deepcopy(related_vars)
            related_vars |= var_related_vars
            for related_var in var_related_vars - prev_related_vars:
                get_related_vars(related_var, related_vars)

        S_related_vars = set()
        get_related_vars(self.start_variable, S_related_vars)
        v1 = S_related_vars
        v1.add(self.start_variable)
        is_related_rule = re.compile('|'.join(re.escape(val) for val in v1))
        p1 -= {rule for rule in p1 if not is_related_rule.fullmatch(rule[0])}

        terminals_pattern = re.compile('|'.join(re.escape(val) for val in self.terminals))
        t1 = {self.null_character}
        for rule in p1:
            t1 |= set(terminals_pattern.findall(rule[1]))

        self._variables = frozenset(v1)
        self._rules = frozenset(p1)
        self._terminals = frozenset(t1)

    def simplify(self):
        """
        Simplifies the grammar.
        """
        self.remove_null_rules()
        self.remove_unit_rules()
        self.reduct()


    @staticmethod
    def _generate_variable_names(variables, n, var_name=None):
        def next_variable():
            nonlocal var_name
            z_index = -1
            for i in range(len(var_name)):
                if var_name[i] == 'Z':
                    z_index = i
            if z_index == len(var_name) - 1:
                var_name = ['A' for _ in range(z_index + 2)]
            else:
                var_name[z_index] = chr(ord(var_name[z_index]) + 1)
            return var_name

        variable_names = []
        if not var_name:
            var_name = ['A']
        while True:
            contain_each_other = False
            var_str = ''.join(var_name)
            for var in variables:
                contain_each_other, _, _ = contain_each_other(var, var_str)
                if contain_each_other:
                    break
            if contain_each_other:
                next_variable()
            else:
                variable_names.extend([var_str + str(i) for i in range(1, 10)])
                next_variable()
                if len(variable_names) >= n:
                    break

        return variable_names[:n], var_name

    def convert_to_cnf(self):
        """
        Converts the grammar to Chomsky normal form (CNF).
        """
        last_checked_variable = None
        free_variables = []

        def new_variable():
            """
            Returns a new variable name that can be added to the grammar's variable set.
            """
            nonlocal free_variables
            nonlocal last_checked_variable

            if len(free_variables) == 0:
                free_variables, last_checked_variable = ContextFreeGrammar._generate_variable_names(
                    self.variables, 9, last_checked_variable)

            return free_variables.pop(0)

        """
        Phase 1
        """
        self.simplify()

        v1 = set(self.variables)
        p1 = set()
        p2 = set()

        is_terminal = re.compile('|'.join(map(re.escape, self.terminals)))

        terminal_rules = {}
        for var in self.variables:
            var_rules = [rule[1] for rule in self.rules if rule[0] == var]
            if len(var_rules) == 1:
                if is_terminal.fullmatch(var_rules[0]):
                    terminal_rules[var_rules[0]] = var

        for rule in self.rules:
            if is_terminal.fullmatch(rule[1]):
                p2.add(rule)
            else:
                rule_terminals = is_terminal.findall(rule[1])
                if not rule_terminals:
                    p1.add(rule)
                else:
                    old_rule = rule[1]
                    for rule_terminal in rule_terminals:
                        if not terminal_rules.get(rule_terminal, None):
                            new_var = new_variable()
                            terminal_rules[rule_terminal] = new_var
                            p2.add((new_var, rule_terminal))
                            v1.add(new_var)
                        old_rule = old_rule.replace(rule_terminal, terminal_rules[rule_terminal])

                    p1.add((rule[0], old_rule))

        """
        Phase 2
        """
        variables_pattern = re.compile('|'.join(map(re.escape, v1)))
        for rule in p1:
            rule_variables = variables_pattern.findall(rule[1])
            if len(rule_variables) == 2:
                p2.add(rule)
            else:
                new_vars = [new_variable() for _ in range(len(rule_variables) - 2)]
                p2.add((rule[0], rule_variables.pop(0) + new_vars[-1]))
                for i in range(len(new_vars) - 2):
                    p2.add((new_vars[i], new_vars.pop(0) + new_vars[i + 1]))
                a = rule_variables.pop()
                b = rule_variables.pop()
                p2.add((new_vars[-1], b + a))
                v1 |= set(new_vars)

        self.variables = frozenset(v1)
        self.rules = frozenset(p2)
        self._is_cnf = True

    def cyk_algorithm(self, string):
        """
        Checks if the grammar can generate the passed string or not using the Cocke–Younger–Kasami (CYK) algorithm.
        """
        string = string.strip()

        if not self._is_cnf:
            if not self._cnf:
                self._cnf = copy.deepcopy(self)
                self._cnf.convert_to_cnf()
            self = self._cnf

        if string == '':
            if self.null_character:
                return True
            return False

        if string == self.null_character:
            return False

        V = [[set() if i != j else {rule[0] for rule in self.rules if rule[1] == string[i]}
              for j in range(len(string))]
             for i in range(len(string))]

        variables_pattern = re.compile('|'.join(map(re.escape, self.variables)))

        def Vij(i, j):
            """
            Calculates V[i][j].
            """
            nonlocal V

            for k in range(i, j):
                for rule in self.rules:
                    rule_variables = variables_pattern.findall(rule[1])
                    if len(rule_variables) == 2:
                        if rule_variables[0] in V[i][k] and rule_variables[1] in V[k + 1][j]:
                            V[i][j].add(rule[0])

        for j in range(len(string) - 1):
            for i in range(len(string)):
                if i + 1 + j < len(string):
                    Vij(i, i + 1 + j)

        if self.start_variable in V[0][-1]:
            return True
        return False

    def stringify_rules(self, *, return_list=False, prepend='', line_splitter='\n'):
        """
        Returns a human-readable string representation of grammar's rules.
        """
        rules_var = {}
        vars = set()
        for rule in self.rules:
            if not rules_var.get(rule[0], None):
                rules_var[rule[0]] = []

            rules_var[rule[0]].append(rule[1])
            if rule[0] != self.start_variable:
                vars.add(rule[0])

        for rules in rules_var.values():
            rules.sort()

        vars = sorted(vars)
        vars.insert(0, self.start_variable)

        if self.null_character:
            if self.null_character not in rules_var[self.start_variable]:
                rules_var[self.start_variable].append(self.null_character)

        str_lines = [prepend + '{} -> {}'.format(var, ' | '.join(rules_var[var])) for var in vars]

        if return_list:
            return str_lines

        return line_splitter.join(str_lines)

    def __str__(self):
        """
        Returns a human-readable string representation of the grammar.
        """
        print_lines = []
        print_lines.append("Variables (V): {}".format(set(self.variables)))
        print_lines.append("Terminals (Σ): {}".format(set(self.terminals)))
        print_lines.append("Null character: {}".format(self.null_character))
        print_lines.append("Start variable (S): {}".format(self.start_variable))
        print_lines.append("Rules (R):")
        print_lines.extend(self.stringify_rules(return_list=True, prepend='\t'))

        return "\n".join(print_lines)