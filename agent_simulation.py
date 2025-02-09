import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Agent:
    """
    Agent implementing the following decision rules:

    1. Signal Decision:
       - If it is the first move:
           * With probability 0.5, signal "Blue"; otherwise signal "Red".
       - Else, calculate blue bias = (# of Blue signals so far) / (total interactions so far).
           * With probability equal to blue bias, signal "Blue"; otherwise signal "Red".

    2. Side Decision:
       - If the opponent's signal equals the agent's own signal, then choose that side.
       - Else, calculate blue choice bias = (# of Blue choices so far) / (total interactions so far).
           * With probability equal to blue choice bias, choose "Blue"; otherwise choose "Red".
    """

    def __init__(self, name):
        self.name = name
        self.total_interactions = 0
        self.blue_signals = 0
        self.blue_choices = 0
        # To record evolution over rounds for visualization:
        self.history_signal_ratio = []
        self.history_choice_ratio = []

    def get_signal_bias(self):
        """Return the ratio of Blue signals in previous interactions."""
        if self.total_interactions == 0:
            return 0.5
        return self.blue_signals / self.total_interactions

    def get_choice_bias(self):
        """Return the ratio of Blue choices in previous interactions."""
        if self.total_interactions == 0:
            return 0.5
        return self.blue_choices / self.total_interactions

    def decide_signal(self, is_first_move):
        """Decide which signal to send."""
        if is_first_move:
            # For the first move, use a fair coin toss.
            if random.random() < 0.5:
                signal = "Blue"
            else:
                signal = "Red"
        else:
            blue_ratio = self.get_signal_bias()
            if random.random() < blue_ratio:
                signal = "Blue"
            else:
                signal = "Red"
        return signal

    def decide_side(self, opponent_signal, own_signal):
        """
        Decide which side to choose:
          - If opponent's signal equals own signal, then choose that side.
          - Otherwise, use the historical blue choice ratio to decide.
        """
        if (opponent_signal == "Blue" and own_signal == "Blue") or (opponent_signal == "Red" and own_signal == "Red"):
            side = own_signal  # Align with the signal if both agree.
        else:
            blue_choice_ratio = self.get_choice_bias()
            if random.random() < blue_choice_ratio:
                side = "Blue"
            else:
                side = "Red"
        return side

    def update_history(self, signal, side):
        """Update the interaction history after each round."""
        self.total_interactions += 1
        if signal == "Blue":
            self.blue_signals += 1
        if side == "Blue":
            self.blue_choices += 1

        # Record current biases for plotting.
        self.history_signal_ratio.append(self.get_signal_bias())
        self.history_choice_ratio.append(self.get_choice_bias())

def run_simulation(num_rounds=100):
    """
    Simulate num_rounds interactions between two agents.
    In each round, each agent:
      1. Decides a signal (using its past history).
      2. Receives the opponent's signal.
      3. Decides its final side based on both signals.
      4. Updates its history.
    """
    agent_A = Agent("Agent A")
    agent_B = Agent("Agent B")

    # For plotting: record the evolution of blue ratio (signal and choice) for each agent.
    rounds = []
    A_signals_history = []
    A_choices_history = []
    B_signals_history = []
    B_choices_history = []

    for round_number in range(num_rounds):
        # Determine if this is the first move for each agent.
        is_first_move_A = (agent_A.total_interactions == 0)
        is_first_move_B = (agent_B.total_interactions == 0)

        # Each agent decides its signal.
        signal_A = agent_A.decide_signal(is_first_move_A)
        signal_B = agent_B.decide_signal(is_first_move_B)

        # Each agent then decides its side.
        side_A = agent_A.decide_side(opponent_signal=signal_B, own_signal=signal_A)
        side_B = agent_B.decide_side(opponent_signal=signal_A, own_signal=signal_B)

        # Print round information in English.
        print(f"Round {round_number + 1}:")
        print(f"  Agent A: Signal = {signal_A}, Side = {side_A}")
        print(f"  Agent B: Signal = {signal_B}, Side = {side_B}\n")

        # Update each agent's history.
        agent_A.update_history(signal_A, side_A)
        agent_B.update_history(signal_B, side_B)

        # Record current bias ratios for plotting.
        rounds.append(round_number + 1)
        A_signals_history.append(agent_A.history_signal_ratio[-1])
        A_choices_history.append(agent_A.history_choice_ratio[-1])
        B_signals_history.append(agent_B.history_signal_ratio[-1])
        B_choices_history.append(agent_B.history_choice_ratio[-1])

    return (rounds, A_signals_history, A_choices_history,
            B_signals_history, B_choices_history, agent_A, agent_B)

def animate_simulation(rounds, A_signals, A_choices, B_signals, B_choices):
    """
    Create an animation showing the evolution of the Blue ratio for signals and choices.
    Two subplots are created:
      - Upper: Signal Blue Ratio over rounds.
      - Lower: Choice Blue Ratio over rounds.
    """
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))
    fig.suptitle("Agent Decision-Making Evolution", fontsize=14)

    # Subplot 1: Signal Blue Ratio
    axs[0].set_title("Signal Blue Ratio")
    axs[0].set_xlabel("Round")
    axs[0].set_ylabel("Blue Ratio")
    axs[0].set_xlim(0, rounds[-1])
    axs[0].set_ylim(0, 1)
    line_A_signal, = axs[0].plot([], [], 'b-', lw=2, label="Agent A")
    line_B_signal, = axs[0].plot([], [], 'r-', lw=2, label="Agent B")
    axs[0].legend(loc="upper left")

    # Subplot 2: Choice Blue Ratio
    axs[1].set_title("Choice Blue Ratio")
    axs[1].set_xlabel("Round")
    axs[1].set_ylabel("Blue Ratio")
    axs[1].set_xlim(0, rounds[-1])
    axs[1].set_ylim(0, 1)
    line_A_choice, = axs[1].plot([], [], 'b--', lw=2, label="Agent A")
    line_B_choice, = axs[1].plot([], [], 'r--', lw=2, label="Agent B")
    axs[1].legend(loc="upper left")

    def init():
        line_A_signal.set_data([], [])
        line_B_signal.set_data([], [])
        line_A_choice.set_data([], [])
        line_B_choice.set_data([], [])
        return line_A_signal, line_B_signal, line_A_choice, line_B_choice

    def update(frame):
        x = rounds[:frame + 1]
        line_A_signal.set_data(x, A_signals[:frame + 1])
        line_B_signal.set_data(x, B_signals[:frame + 1])
        line_A_choice.set_data(x, A_choices[:frame + 1])
        line_B_choice.set_data(x, B_choices[:frame + 1])
        return line_A_signal, line_B_signal, line_A_choice, line_B_choice

    ani = FuncAnimation(fig, update, frames=len(rounds),
                        init_func=init, blit=True, interval=200, repeat=False)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def main():
    num_rounds = 100  # You can change the number of rounds as desired.
    (rounds, A_signals, A_choices,
     B_signals, B_choices, agent_A, agent_B) = run_simulation(num_rounds)
    animate_simulation(rounds, A_signals, A_choices, B_signals, B_choices)

if __name__ == '__main__':
    main()
