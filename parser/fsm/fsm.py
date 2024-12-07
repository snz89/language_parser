class FSM:
    """
    Конечный автомат с возможностью переходов между состояниями на основе входных токенов.
    """

    def __init__(self, states, transitions, initial_state, final_states):
        """
        :param states: множество состояний
        :param transitions: словарь переходов {(state_from, token): state_to}
        :param initial_state: начальное состояние
        :param final_states: множество конечных состояний
        """
        self.states = states
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.current_state = initial_state

    def transition(self, input_token):
        if (self.current_state, input_token) in self.transitions:
            self.current_state = self.transitions[(
                self.current_state, input_token)]
        else:
            self.current_state = None

    def is_accepted(self):
        return self.current_state in self.final_states

    def process_sequence(self, input_sequence):
        """Обрабатывает последовательность и возвращает результат принятия."""
        for element in input_sequence:
            self.transition(element)
        return self.is_accepted()

    def reset(self):
        """Сбрасывает текущее состояние к начальному."""
        self.current_state = self.initial_state
