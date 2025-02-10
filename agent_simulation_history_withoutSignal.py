import random
import matplotlib.pyplot as plt

# 伪计数：初始认为 Blue 与 Red 各有 1 次“假交互”
PSEUDO_COUNT = 1.0

class Agent:
    def __init__(self, name):
        self.name = name
        # 初始计数：总次数为2（Blue+Red各1），Blue计数为1
        self.total = 2 * PSEUDO_COUNT
        self.blue_count = PSEUDO_COUNT
        # 记录每次决策的方向（仅用于调试和观察演变）
        self.history = []
    
    def get_blue_ratio(self):
        return self.blue_count / self.total
    
    def decide_direction(self):
        # 第一次决策时根据初始伪计数给出的 0.5 概率
        if not self.history:
            direction = "Blue" if random.random() < 0.5 else "Red"
        else:
            ratio = self.get_blue_ratio()
            direction = "Blue" if random.random() < ratio else "Red"
        self.history.append(direction)
        return direction
    
    def update_history(self, chosen_direction):
        # 每次决策后更新统计数据
        self.total += 1
        if chosen_direction == "Blue":
            self.blue_count += 1

def run_simulation_convergence(num_agents, max_rounds=100000):
    """
    创建 num_agents 个 agent，进行随机两两配对交互：
      - 每轮随机抽取一对 agent，各自依靠自己的历史作出方向决策；
      - 决策后，双方都更新自己的历史统计；
      - 当所有 agent 最近一次决策均相同时，认为全局收敛。
    返回达到收敛所需的轮次以及 agent 列表。
    """
    agents = [Agent(f"Agent {i+1}") for i in range(num_agents)]
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        # 随机抽取一对 agent进行交互（若 agent 数量为奇数，则有 agent 本轮不参与）
        pair = random.sample(agents, 2)
        d1 = pair[0].decide_direction()
        d2 = pair[1].decide_direction()
        # 更新两 agent 的历史
        pair[0].update_history(d1)
        pair[1].update_history(d2)
        # 每隔 10 轮检查一次全局收敛条件：所有 agent 最近一次决策均相同
        if rounds % 10 == 0:
            last_choices = [agent.history[-1] for agent in agents if agent.history]
            if len(last_choices) == num_agents and all(choice == last_choices[0] for choice in last_choices):
                break
    return rounds, agents

def simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000):
    """
    对于给定的一系列 agent 数量，重复 runs_per_size 次模拟，
    返回字典 {agent_size: avg_rounds_to_convergence}，
    同时输出每组的平均 Blue 选择概率（即 p(Blue)）。
    """
    results = {}
    for size in agent_sizes:
        round_counts = []
        final_blue_ratios = []
        for _ in range(runs_per_size):
            rounds, agents = run_simulation_convergence(size, max_rounds=max_rounds)
            round_counts.append(rounds)
            # 收集每个 agent 当前 p(Blue)
            final_blue_ratios.extend([agent.get_blue_ratio() for agent in agents])
        avg_rounds = sum(round_counts) / len(round_counts)
        results[size] = avg_rounds
        avg_blue_ratio = sum(final_blue_ratios) / len(final_blue_ratios)
        print(f"Agent Size: {size}, Avg Rounds to Convergence: {avg_rounds:.1f}, "
              f"Avg p(Blue): {avg_blue_ratio:.2f}")
    return results

def plot_results(results):
    sizes = sorted(results.keys())
    rounds_list = [results[size] for size in sizes]
    plt.figure(figsize=(8,6))
    plt.plot(sizes, rounds_list, marker='o')
    plt.xlabel("Number of Agents")
    plt.ylabel("Average Rounds to Convergence")
    plt.title("Convergence Rounds vs. Agent Population Size (Only Direction)")
    plt.grid(True)
    plt.show()

def main():
    # 对不同 agent 数量进行多次模拟
    agent_sizes = [2, 4, 6, 8, 10, 16, 20, 50, 100, 200]
    results = simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000)
    plot_results(results)


if __name__ == '__main__':
    main()
