import random
import matplotlib.pyplot as plt

# 学习率参数（可根据需要调整）
ALPHA = 0.5   # 成功时的更新步长
BETA  = 0.4   # 失败时的更新步长

class Agent:
    def __init__(self, name):
        self.name = name
        self.x = 0.5  # 初始偏好，0.5 表示 Blue 与 Red 各半
        self.history = []  # 记录每轮决策后的 x 值

    def choose_direction(self):
        # 以当前 x 作为选择 Blue 的概率
        direction = "Blue" if random.random() < self.x else "Red"
        return direction

    def update(self, chosen_direction, success):
        if success:
            if chosen_direction == "Blue":
                # 协调成功，强化 Blue 倾向
                self.x = self.x + ALPHA * (1 - self.x)
            else:  # chosen_direction == "Red"
                self.x = self.x - ALPHA * self.x
        else:
            if chosen_direction == "Blue":
                # 协调失败，减少 Blue 倾向
                self.x = self.x - BETA * self.x
            else:  # chosen_direction == "Red"
                self.x = self.x + BETA * (1 - self.x)
        # 限制 x 在 [0,1]
        self.x = max(0.0, min(1.0, self.x))
        self.history.append(self.x)

def run_simulation_convergence(num_agents, max_rounds=100000):
    """
    创建 num_agents 个 agent，每轮随机配对交互，
    更新各自的偏好 x。
    收敛条件：所有 agent 的 x 均 ≥ 0.99 或均 ≤ 0.01。
    返回达到收敛所需的轮次和 agent 列表。
    """
    agents = [Agent(f"Agent {i+1}") for i in range(num_agents)]
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        pair = random.sample(agents, 2)
        d1 = pair[0].choose_direction()
        d2 = pair[1].choose_direction()
        success = (d1 == d2)
        # 更新每个 agent，根据自己本次的选择和交互结果更新 x
        pair[0].update(d1, success)
        pair[1].update(d2, success)
        
        # 每隔 10 轮检查一次收敛：所有 agent 的 x 都非常接近 0 或 1
        if rounds % 10 == 0:
            xs = [agent.x for agent in agents]
            if all(x >= 0.99 for x in xs) or all(x <= 0.01 for x in xs):
                break
    return rounds, agents

def simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000):
    """
    对于给定 agent 数量列表，重复 runs_per_size 次模拟，
    返回字典 {agent_size: avg_rounds_to_convergence} 并打印每组的
    平均最终偏好（即平均 x 值）。
    """
    results = {}
    for size in agent_sizes:
        round_counts = []
        final_xs = []
        for _ in range(runs_per_size):
            rounds, agents = run_simulation_convergence(size, max_rounds=max_rounds)
            round_counts.append(rounds)
            final_xs.extend([agent.x for agent in agents])
        avg_rounds = sum(round_counts) / len(round_counts)
        avg_x = sum(final_xs) / len(final_xs)
        results[size] = avg_rounds
        print(f"Agent Size: {size}, Avg Rounds to Convergence: {avg_rounds:.1f}, "
              f"Avg x: {avg_x:.2f}")
    return results

def plot_results(results):
    sizes = sorted(results.keys())
    rounds_list = [results[size] for size in sizes]
    plt.figure(figsize=(8,6))
    plt.plot(sizes, rounds_list, marker='o')
    plt.xlabel("Number of Agents")
    plt.ylabel("Average Rounds to Convergence")
    plt.title("Convergence Rounds vs. Agent Population Size (Direct Direction Choice)")
    plt.grid(True)
    plt.show()

def main():    
    # 对不同 agent 数量进行模拟
    agent_sizes = [2, 4, 6, 8, 10, 16, 20, 50, 100, 200]
    results = simulate_for_agent_sizes(agent_sizes, runs_per_size=20, max_rounds=100000)
    plot_results(results)

if __name__ == '__main__':
    main()
