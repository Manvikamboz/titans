"""DFA (Deterministic Finite Automaton) engine. No graphics, so it is easy to test."""
from itertools import product


class DFA:
    def __init__(self, name, description, states, alphabet, start, accepting, transitions):
        self.name, self.description = name, description
        self.states, self.alphabet = list(states), list(alphabet)
        self.start, self.accepting = start, set(accepting)
        self.transitions = dict(transitions)   # (state, symbol) -> state
        self._validate()

    def _validate(self):
        if self.start not in self.states:
            raise ValueError("start state is not in the state list")
        if not self.accepting <= set(self.states):
            raise ValueError("an accepting state is not in the state list")
        for s in self.states:
            for a in self.alphabet:
                if (s, a) not in self.transitions:       # 'deterministic' = exactly one move
                    raise ValueError(f"missing transition for state {s} on symbol {a}")
                if self.transitions[(s, a)] not in self.states:
                    raise ValueError(f"transition from {s} on {a} goes to an unknown state")

    def run(self, text):
        """Returns (accepted, trace). trace = list of (from_state, symbol, to_state)."""
        state, trace = self.start, []
        for ch in text:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet {self.alphabet}")
            nxt = self.transitions[(state, ch)]
            trace.append((state, ch, nxt))
            state = nxt
        return state in self.accepting, trace

    def accepts(self, text):
        return self.run(text)[0]

    def reachable_states(self):
        """DFS over the DFA graph. A state that is never reached is useless."""
        seen, stack = set(), [self.start]
        while stack:
            s = stack.pop()
            if s in seen:
                continue
            seen.add(s)
            stack.extend(self.transitions[(s, a)] for a in self.alphabet)
        return seen

    def unreachable_states(self):
        return [s for s in self.states if s not in self.reachable_states()]


def divisible_by_3():
    """Binary number divisible by 3. State = remainder so far."""
    states = ["r0", "r1", "r2"]
    t = {(f"r{r}", b): f"r{(2 * r + int(b)) % 3}" for r in range(3) for b in "01"}
    return DFA("Binary divisible by 3", "Accepts binary numbers that are multiples of 3",
               states, "01", "r0", ["r0"], t)


def ends_with_01():
    t = {("q0", "0"): "q1", ("q0", "1"): "q0",
         ("q1", "0"): "q1", ("q1", "1"): "q2",
         ("q2", "0"): "q1", ("q2", "1"): "q0"}
    return DFA("Ends with 01", "Accepts strings whose last two symbols are 0 then 1",
               ["q0", "q1", "q2"], "01", "q0", ["q2"], t)


def no_two_ones():
    t = {("ok", "0"): "ok", ("ok", "1"): "one",
         ("one", "0"): "ok", ("one", "1"): "dead",
         ("dead", "0"): "dead", ("dead", "1"): "dead"}
    return DFA("No two 1s in a row", "Rejects any string containing 11 (dead = trap state)",
               ["ok", "one", "dead"], "01", "ok", ["ok", "one"], t)


EXAMPLES = [divisible_by_3, ends_with_01, no_two_ones]


def all_strings(alphabet, max_len):
    for n in range(max_len + 1):
        for combo in product(alphabet, repeat=n):
            yield "".join(combo)
