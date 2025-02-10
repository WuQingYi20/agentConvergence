import random
import matplotlib.pyplot as plt

# 学习率参数，较激进以加快收敛
ALPHA = 0.8   # 成功时更新步长
BETA  = 0.8   # 失败时更新步长

class Agent:
    def __init__(self, name):
        self.name = name
        self.p_signal = 0.5  # 信号决策偏好：选择 Blue 的概率
        self.p_choice = 0.5  # 决策冲突时坚持自己信号的概率
        # 用于记录历史，便于调试观察
        self.history_signal = []  # 每轮发送的信号
        self.history_final = []   # 每轮最终选择的方向

    def decide_signal(self):
        # 以 p_signal 概率发送 Blue，否则 Red
        if random.random() < self.p_signal:
            signal = "Blue"
        else:
            signal = "Red"
        self.history_signal.append(signal)
        return signal

    def decide_final(self, opponent_signal, own_signal):
        # 如果双方信号一致，则直接采用该信号
        if opponent_signal == own_signal:
            final = own_signal
        else:
            # 如果信号不一致，则以 p_choice 决定是否坚持自己的信号
            if random.random() < self.p_choice:
                final = own_signal
            else:
                final = opponent_signal
        self.history_final.append(final)
        return final

    def update(self, own_signal, final_decision, success, signals_match):
        # 更新 p_signal：依据交互成功与否
        if success:
            if own_signal == "Blue":
                self.p_signal = self.p_signal + ALPHA * (1 - self.p_signal)
            else:  # Red
                self.p_signal = self.p_signal - ALPHA * self.p_signal
        else:
            if own_signal == "Blue":
                self.p_signal = self.p_signal - BETA * self.p_signal
            else:
                self.p_signal = self.p_signal + BETA * (1 - self.p_signal)
        self.p_signal = max(0.0, min(1.0, self.p_signal))
        
        # 更新 p_choice 仅在信号冲突情况下
        if not signals_match:
            # 若交互成功且 agent 坚持自己，则奖励 p_choice
            if success and (final_decision == own_signal):
                self.p_choice = self.p_choice + ALPHA * (1 - self.p_choice)
            # 若交互失败且 agent 坚持自己，则惩罚 p_choice
            elif (not success) and (final_decision == own_signal):
                self.p_choice = self.p_choice - BETA * self.p_choice
            # 可以对另一种情况（跟随对方时）的更新做对称处理，也可不更新
            self.p_choice = max(0.0, min(1.0, self.p_choice))

def run_simulation_convergence(num_agents, max_rounds=100000):
    """
    创建 num_agents 个 agent，进行随机配对交互：
      - 每轮，每个 agent先根据 p_signal 发送信号；
      - 然后在 pair 中，各自依据对方信号和自己的 p_choice 选择最终方向；
      - 若最终选择一致，则交互成功，否则失败；
      - 根据成功与否更新各 agent 的 p_signal（始终更新）和 p_choice（仅在信号不一致时更新）。
      - 当所有 agent 最近一次的最终选择均相同时，认为全局收敛。
    返回达到收敛所需轮次和 agent 列表。
    """
    agents = [Agent(f"Agent {i+1}") for i in range(num_agents)]
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        # 随机抽取一对 agent
        pair = random.sample(agents, 2)
        # 各 agent先决策信号
        s1 = pair[0].decide_signal()
        s2 = pair[1].decide_signal()
        # 判断信号是否一致
        signals_match = (s1 == s2)
        # 各 agent作出最终选择
        final1 = pair[0].decide_final(s2, s1)
        final2 = pair[1].decide_final(s1, s2)
        # 交互成功条件：最终选择一致
        success = (final1 == final2)
        # 更新各 agent
        pair[0].update(s1, final1, success, signals_match)
        pair[1].update(s2, final2, success, signals_match)
        
        # 每 10 轮检查全局收敛：所有 agent 最近一次的最终选择是否相同
        if rounds % 10 == 0:
            last_finals = [agent.history_final[-1] for agent in agents if agent.history_final]
            if len(last_finals) == num_agents and all(choice == last_finals[0] for choice in last_finals):
                break
    return rounds, agents

def simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000):
    """
    对不同 agent 数量进行模拟，重复 runs_per_size 次，
    返回字典 {agent_size: avg_rounds_to_convergence} 并打印每组的
    平均最终 p_signal 与 p_choice。
    """
    results = {}
    for size in agent_sizes:
        round_counts = []
        final_p_signals = []
        final_p_choices = []
        for _ in range(runs_per_size):
            rounds, agents = run_simulation_convergence(size, max_rounds=max_rounds)
            round_counts.append(rounds)
            final_p_signals.extend([agent.p_signal for agent in agents])
            final_p_choices.extend([agent.p_choice for agent in agents])
        avg_rounds = sum(round_counts) / len(round_counts)
        avg_p_signal = sum(final_p_signals) / len(final_p_signals)
        avg_p_choice = sum(final_p_choices) / len(final_p_choices)
        results[size] = avg_rounds
        print(f"Agent Size: {size}, Avg Rounds: {avg_rounds:.1f}, "
              f"Avg p_signal: {avg_p_signal:.2f}, Avg p_choice: {avg_p_choice:.2f}")
    return results

def plot_results(results):
    sizes = sorted(results.keys())
    rounds_list = [results[size] for size in sizes]
    plt.figure(figsize=(8,6))
    plt.plot(sizes, rounds_list, marker='o')
    plt.xlabel("Number of Agents")
    plt.ylabel("Avg Rounds to Convergence")
    plt.title("Convergence Rounds vs. Agent Population Size (Signal + Direction)")
    plt.grid(True)
    plt.show()

def main():
    # 对不同 agent 数量进行模拟
    agent_sizes = [2, 4, 6, 8, 10, 16, 20, 50, 100, 200]
    results = simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000)
    plot_results(results)

if __name__ == '__main__':
    main()
