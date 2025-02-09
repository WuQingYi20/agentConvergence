import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Agent:
    """
    Improved Agent for a pure coordination game with dynamic (reinforcement-like) updating.
    
    Internal parameters:
      - p_signal: probability of choosing "Blue" in the signal phase.
      - p_choice: probability of choosing "Blue" in the direction (choice) phase.
      
    Both parameters are updated after each round based on the coordination outcome.
    """
    def __init__(self, name, lr=0.1):
        self.name = name
        self.lr = lr  # learning rate for updating probabilities
        self.p_signal = 0.5  # initial probability for Blue signal
        self.p_choice = 0.5  # initial probability for Blue direction choice
        
        # For plotting evolution:
        self.history_signal_bias = []
        self.history_choice_bias = []

    def decide_signal(self):
        """Decide which signal to send based on current p_signal."""
        return "Blue" if random.random() < self.p_signal else "Red"

    def decide_side(self, own_signal, opponent_signal):
        """
        Decide which side to choose.
        
        If both signals are the same, choose that common signal.
        Otherwise, decide based on current p_choice.
        """
        if own_signal == opponent_signal:
            # Coordination enforced when signals agree.
            return own_signal
        else:
            return "Blue" if random.random() < self.p_choice else "Red"

    def update_biases(self, chosen_signal, chosen_side, outcome):
        """
        Update internal probabilities based on the round outcome.
        
        outcome: 1 if coordinated (win), 0 if not (lost).
        
        Update rule:
          If outcome == 1:
              - Reinforce the chosen action by moving the corresponding probability toward 1 (if Blue)
                or toward 0 (if Red).
          If outcome == 0:
              - Punish the chosen action by moving the corresponding probability toward 0.5.
        
        Both p_signal and p_choice are updated accordingly.
        """
        # --- Update p_signal ---
        if outcome == 1:
            if chosen_signal == "Blue":
                self.p_signal += self.lr * (1 - self.p_signal)
            else:
                self.p_signal -= self.lr * self.p_signal
        else:
            # If lost, move p_signal toward 0.5 to encourage exploration.
            if chosen_signal == "Blue":
                self.p_signal -= self.lr * (self.p_signal - 0.5)
            else:
                self.p_signal += self.lr * (0.5 - self.p_signal)
        
        # --- Update p_choice ---
        if outcome == 1:
            if chosen_side == "Blue":
                self.p_choice += self.lr * (1 - self.p_choice)
            else:
                self.p_choice -= self.lr * self.p_choice
        else:
            # If lost, move p_choice toward 0.5.
            if chosen_side == "Blue":
                self.p_choice -= self.lr * (self.p_choice - 0.5)
            else:
                self.p_choice += self.lr * (0.5 - self.p_choice)
        
        # Record current biases for plotting.
        self.history_signal_bias.append(self.p_signal)
        self.history_choice_bias.append(self.p_choice)

def run_simulation(num_rounds=100):
    """
    Run a simulation of num_rounds rounds between two agents in a pure coordination game.
    
    Each round:
      1. Both agents decide their signal based on p_signal.
      2. Signals are revealed.
      3. Both agents decide their final side:
           - If signals match, side = common signal.
           - Else, decide based on p_choice.
      4. Outcome is determined: if both sides match, coordination is successful (reward=1); otherwise 0.
      5. Each agent updates its p_signal and p_choice based on the outcome.
    """
    agent_A = Agent("Agent A", lr=0.1)
    agent_B = Agent("Agent B", lr=0.1)
    
    rounds = []
    A_signal_history = []
    A_choice_history = []
    B_signal_history = []
    B_choice_history = []
    
    for round_number in range(1, num_rounds+1):
        # Phase 1: Signal decision.
        signal_A = agent_A.decide_signal()
        signal_B = agent_B.decide_signal()
        
        # Phase 2: Side (direction) decision.
        side_A = agent_A.decide_side(signal_A, signal_B)
        side_B = agent_B.decide_side(signal_B, signal_A)
        
        # Determine outcome: coordination successful if both sides match.
        outcome = 1 if side_A == side_B else 0
        
        # Print round information in English.
        print(f"Round {round_number}:")
        print(f"  Agent A: Signal = {signal_A}, Side = {side_A}")
        print(f"  Agent B: Signal = {signal_B}, Side = {side_B}")
        print(f"  Outcome: {'Coordinated' if outcome==1 else 'Not Coordinated'}\n")
        
        # Update internal probabilities based on outcome.
        agent_A.update_biases(signal_A, side_A, outcome)
        agent_B.update_biases(signal_B, side_B, outcome)
        
        # Record biases for plotting.
        rounds.append(round_number)
        A_signal_history.append(agent_A.history_signal_bias[-1])
        A_choice_history.append(agent_A.history_choice_bias[-1])
        B_signal_history.append(agent_B.history_signal_bias[-1])
        B_choice_history.append(agent_B.history_choice_bias[-1])
    
    return (rounds, A_signal_history, A_choice_history,
            B_signal_history, B_choice_history, agent_A, agent_B)

def animate_simulation(rounds, A_signal_hist, A_choice_hist, B_signal_hist, B_choice_hist):
    """
    Animate the evolution of p_signal and p_choice for both agents.
    
    Two subplots:
      - Upper: p_signal (Blue bias in the signal phase).
      - Lower: p_choice (Blue bias in the choice phase).
    """
    fig, axs = plt.subplots(2, 1, figsize=(9, 8))
    fig.suptitle("Evolution of Agent Biases in Pure Coordination Game", fontsize=14)
    
    # Subplot 1: Signal bias evolution.
    axs[0].set_title("Signal Bias (p_signal)")
    axs[0].set_xlabel("Round")
    axs[0].set_ylabel("Probability of Blue")
    axs[0].set_xlim(0, rounds[-1])
    axs[0].set_ylim(0, 1)
    line_A_signal, = axs[0].plot([], [], 'b-', lw=2, label="Agent A")
    line_B_signal, = axs[0].plot([], [], 'r-', lw=2, label="Agent B")
    axs[0].legend(loc="upper left")
    
    # Subplot 2: Choice bias evolution.
    axs[1].set_title("Choice Bias (p_choice)")
    axs[1].set_xlabel("Round")
    axs[1].set_ylabel("Probability of Blue")
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
        line_A_signal.set_data(x, A_signal_hist[:frame + 1])
        line_B_signal.set_data(x, B_signal_hist[:frame + 1])
        line_A_choice.set_data(x, A_choice_hist[:frame + 1])
        line_B_choice.set_data(x, B_choice_hist[:frame + 1])
        return line_A_signal, line_B_signal, line_A_choice, line_B_choice
    
    ani = FuncAnimation(fig, update, frames=len(rounds),
                        init_func=init, blit=True, interval=200, repeat=False)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def main():
    num_rounds = 100  # You can modify the number of rounds as needed.
    (rounds, A_signal_hist, A_choice_hist,
     B_signal_hist, B_choice_hist, agent_A, agent_B) = run_simulation(num_rounds)
    animate_simulation(rounds, A_signal_hist, A_choice_hist,
                       B_signal_hist, B_choice_hist)

if __name__ == '__main__':
    main()
