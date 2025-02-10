import random
import matplotlib.pyplot as plt

# 这里设置伪计数（初始历史值）：每个计数都初始化为1
PSEUDO_COUNT = 2

class Agent:
    def __init__(self, name):
        self.name = name
        # 为防止第一次决策“写死”，我们对信号和选择分别设置初始伪计数
        self.signal_total = 2 * PSEUDO_COUNT  # 初始认为总次数=2（1 Blue + 1 Red）
        self.blue_signal = PSEUDO_COUNT       # 初始 Blue 计数为 1
        self.choice_total = 2 * PSEUDO_COUNT    # 同理
        self.blue_choice = PSEUDO_COUNT
        # 记录历史决策（用于调试和观察演变）
        self.history_signal = []  # 每次决策记录信号
        self.history_choice = []  # 每次决策记录最终选择

    def get_signal_blue_ratio(self):
        return self.blue_signal / self.signal_total

    def get_choice_blue_ratio(self):
        return self.blue_choice / self.choice_total

    def decide_signal(self):
        # 如果还没有实际交互，则视为第一次决策（用初始伪计数给出的 0.5 概率）
        if not self.history_signal:
            signal = "Blue" if random.random() < 0.5 else "Red"
        else:
            ratio = self.get_signal_blue_ratio()
            signal = "Blue" if random.random() < ratio else "Red"
        self.history_signal.append(signal)
        return signal

    def decide_side(self, opponent_signal, own_signal):
        # 如果双方信号一致，则直接采用该信号
        if opponent_signal == own_signal:
            side = own_signal
        else:
            ratio = self.get_choice_blue_ratio()
            side = "Blue" if random.random() < ratio else "Red"
        self.history_choice.append(side)
        return side

    def update_history(self, own_signal, chosen_side):
        # 更新信号历史记录
        self.signal_total += 1
        if own_signal == "Blue":
            self.blue_signal += 1
        # 更新选择历史
        self.choice_total += 1
        if chosen_side == "Blue":
            self.blue_choice += 1

def run_simulation_convergence(num_agents, max_rounds=100000):
    """
    创建 num_agents 个 agent，进行随机两两配对交互：
      - 每轮：随机选取一对 agent，各自依靠自身历史作出信号决策，
        再根据对方信号和自身历史作出最终选择（方向）。
      - 若一对 agent 的最终选择一致，则视为一次“成功”交互。
      - 每轮结束后，双方更新各自的历史（记录决策）。
      - 当所有 agent 最近一次的最终选择均相同时，认为全局收敛。
    返回达到收敛所需的轮次及 agent 列表。
    """
    agents = [Agent(f"Agent {i+1}") for i in range(num_agents)]
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        # 随机抽取一对 agent进行交互（若奇数则有agent未参与，本轮不更新其历史）
        pair = random.sample(agents, 2)
        s1 = pair[0].decide_signal()
        s2 = pair[1].decide_signal()
        side1 = pair[0].decide_side(s2, s1)
        side2 = pair[1].decide_side(s1, s2)
        # 这里可以根据交互结果决定“奖励”与“惩罚”，但本实现统一更新历史
        pair[0].update_history(s1, side1)
        pair[1].update_history(s2, side2)

        # 每隔 10 轮检查一次全局收敛条件：所有 agent 最近一次最终选择是否一致
        if rounds % 10 == 0:
            last_choices = [agent.history_choice[-1] for agent in agents if agent.history_choice]
            if len(last_choices) == num_agents and all(choice == last_choices[0] for choice in last_choices):
                break
    return rounds, agents

def simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000):
    """
    对于给定的一系列 agent 数量，重复 runs_per_size 次模拟，
    返回字典 {agent_size: avg_rounds_to_convergence}，
    并打印每组最终平均各 agent 的信号和选择偏好（即 p(Blue)）。
    """
    results = {}
    for size in agent_sizes:
        round_counts = []
        # 为观察最终状态，也收集每次模拟后各agent的 p_blue 值（信号与选择分别）
        final_signal_ratios = []
        final_choice_ratios = []
        for _ in range(runs_per_size):
            rounds, agents = run_simulation_convergence(size, max_rounds=max_rounds)
            round_counts.append(rounds)
            # 收集每个 agent的当前信号与选择蓝色比例
            final_signal_ratios.extend([agent.get_signal_blue_ratio() for agent in agents])
            final_choice_ratios.extend([agent.get_choice_blue_ratio() for agent in agents])
        avg_rounds = sum(round_counts) / len(round_counts)
        results[size] = avg_rounds
        avg_signal_ratio = sum(final_signal_ratios) / len(final_signal_ratios)
        avg_choice_ratio = sum(final_choice_ratios) / len(final_choice_ratios)
        print(f"Agent Size: {size}, Avg Rounds to Convergence: {avg_rounds:.1f}, "
              f"Avg Signal p(Blue): {avg_signal_ratio:.2f}, Avg Choice p(Blue): {avg_choice_ratio:.2f}")
    return results

def plot_results(results):
    sizes = sorted(results.keys())
    rounds_list = [results[size] for size in sizes]
    plt.figure(figsize=(8,6))
    plt.plot(sizes, rounds_list, marker='o')
    plt.xlabel("Number of Agents")
    plt.ylabel("Average Rounds to Convergence")
    plt.title("Convergence Rounds vs. Agent Population Size")
    plt.grid(True)
    plt.show()

def main():    
    # 对不同 agent 数量进行多次模拟
    agent_sizes = [2, 4, 6, 8, 10, 16, 20, 50, 100, 200]
    results = simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000)
    plot_results(results)


if __name__ == '__main__':
    main()
