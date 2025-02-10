import random
import matplotlib.pyplot as plt

# ============================
# 全局参数
# ============================
INITIAL_EXPLORATION_RATE = 0.5      # 初始探索率
DECAY_FACTOR = 0.98                 # 探索率衰减因子（加快衰减）
MIN_EXPLORATION_RATE = 0         # 探索率下限
LEARNING_RATE = 0.3                 # 学习率（增大以加快收敛）

def get_exploration_rate(iteration):
    """根据当前迭代次数计算探索率（梯度衰减）"""
    exploration_rate = INITIAL_EXPLORATION_RATE * (DECAY_FACTOR ** iteration)
    if exploration_rate < MIN_EXPLORATION_RATE:
        exploration_rate = MIN_EXPLORATION_RATE
    return exploration_rate

# ============================
# Agent 类
# ============================
class Agent:
    def __init__(self, name):
        self.name = name
        self.total_interactions = 0
        # 信号决策成功率估计，初始为 0.5
        self.blue_success_rate = 0.5  
        self.red_success_rate = 0.5
        # 在信号冲突时，决定是否坚持自己信号的成功率估计
        self.stick_probability = 0.5  
        # 记录历史数据，便于可视化
        self.history_signal_prob = []      # 当前选择 Blue 的概率估计
        self.history_stick_probability = [] # 坚持自己决策的概率估计
        self.history_success = []           # 每轮是否获得奖励（1 成功；0 失败）
    
    def decide_signal(self, is_first_move, iteration):
        """
        信号决策：
          - 如果是初次移动或处于探索阶段，则随机选择；
          - 否则根据信号成功率更新估计选择 Blue 的概率。
        """
        exploration_rate = get_exploration_rate(iteration)
        if is_first_move or random.random() < exploration_rate:
            signal = "Blue" if random.random() < 0.5 else "Red"
        else:
            total = self.blue_success_rate + self.red_success_rate
            p_blue = self.blue_success_rate / total if total > 0 else 0.5
            signal = "Blue" if random.random() < p_blue else "Red"
        return signal

    def decide_side(self, opponent_signal, own_signal, iteration):
        """
        方向决策：
          - 如果双方信号一致，则直接选择该信号；
          - 如果不一致，则先按当前探索率判断是否随机选择，
            否则根据信号冲突时坚持自己成功率做决策。
        """
        exploration_rate = get_exploration_rate(iteration)
        if opponent_signal == own_signal:
            side = own_signal
        else:
            if random.random() < exploration_rate:
                side = own_signal if random.random() < 0.5 else opponent_signal
            else:
                side = own_signal if random.random() < self.stick_probability else opponent_signal
        return side

    def update_history(self, own_signal, chosen_side, interaction_success, learning_rate=LEARNING_RATE):
        """
        根据交互结果更新 agent 状态：
          - 如果 agent 的信号为 Blue，则更新 blue_success_rate，否则更新 red_success_rate；
          - 如果在冲突时坚持自己的（chosen_side == own_signal），更新 stick_probability 向奖励 1 靠拢，
            否则向 0 靠拢（或反之）。
        同时记录历史数据。
        """
        self.total_interactions += 1
        reward = 1 if interaction_success else 0
        
        # 更新信号成功率：new = old + learning_rate*(reward - old)
        if own_signal == "Blue":
            self.blue_success_rate += learning_rate * (reward - self.blue_success_rate)
        else:
            self.red_success_rate += learning_rate * (reward - self.red_success_rate)
        
        # 更新坚持自己决策的成功率
        if chosen_side == own_signal:
            self.stick_probability += learning_rate * (reward - self.stick_probability)
        else:
            # 若没有坚持，更新为 (1 - reward) 趋向对方策略（也可看作对“不坚持”给予负面反馈）
            self.stick_probability += learning_rate * ((1 - reward) - self.stick_probability)
        
        # 记录当前估计（计算选择 Blue 的整体概率）
        total_signal = self.blue_success_rate + self.red_success_rate
        p_blue = self.blue_success_rate / total_signal if total_signal > 0 else 0.5
        self.history_signal_prob.append(p_blue)
        self.history_stick_probability.append(self.stick_probability)
        self.history_success.append(reward)

# ============================
# 多 agent 模拟及 Agent1 数据跟踪
# ============================
def run_simulation(num_rounds=1000, num_agents=20):
    """
    模拟多 agent 随机交互：
      - 创建 num_agents 个 agent；
      - 每轮随机选取一对 agent 进行交互；
      - 交互规则：各自根据信号决策和方向决策确定最终选择，
        如果双方最终选择一致，则均视为成功（reward=1）；否则 reward=0；
      - 同时跟踪 Agent 1 的数据（状态参数和对手信息）。
    """
    agents = [Agent(f"Agent {i+1}") for i in range(num_agents)]
    
    # 用于记录 Agent 1 参与交互时的数据
    agent1_rounds = []              # Agent 1 参与交互的轮次
    agent1_signal_prob_history = [] # Agent 1 当前选择 Blue 的概率估计
    agent1_stick_history = []       # Agent 1 坚持自己决策的概率
    agent1_success_history = []     # Agent 1 本轮交互是否成功
    agent1_opponent_info = []       # 对手信息：(对手名称, 对手 p(Blue), 对手 stick_probability)
    
    for round_number in range(1, num_rounds + 1):
        # 随机匹配两个不同 agent
        pair = random.sample(agents, 2)
        
        # 判断是否有 Agent 1 参与
        agent1_in_pair = None
        agent2_in_pair = None
        for agent in pair:
            if agent.name == "Agent 1":
                agent1_in_pair = agent
            else:
                agent2_in_pair = agent
        
        # 每个 agent 决策信号
        signal_dict = {}
        for agent in pair:
            is_first_move = (agent.total_interactions == 0)
            signal_dict[agent] = agent.decide_signal(is_first_move, round_number)
        
        # 每个 agent 决策方向（利用对方信号）
        side_dict = {}
        for agent in pair:
            opponent = pair[0] if pair[1] == agent else pair[1]
            side_dict[agent] = agent.decide_side(opponent_signal=signal_dict[opponent],
                                                 own_signal=signal_dict[agent],
                                                 iteration=round_number)
        
        # 交互成功：双方最终选择一致
        interaction_success = (list(side_dict.values())[0] == list(side_dict.values())[1])
        
        # 更新双方历史
        for agent in pair:
            agent.update_history(own_signal=signal_dict[agent],
                                 chosen_side=side_dict[agent],
                                 interaction_success=interaction_success)
        
        # 若 Agent 1 参与，记录其数据
        if agent1_in_pair is not None:
            agent1_rounds.append(round_number)
            total_signal = agent1_in_pair.blue_success_rate + agent1_in_pair.red_success_rate
            p_blue = agent1_in_pair.blue_success_rate / total_signal if total_signal > 0 else 0.5
            agent1_signal_prob_history.append(p_blue)
            agent1_stick_history.append(agent1_in_pair.stick_probability)
            agent1_success_history.append(1 if interaction_success else 0)
            
            # 记录对手信息
            opp_total = agent2_in_pair.blue_success_rate + agent2_in_pair.red_success_rate
            opp_p_blue = agent2_in_pair.blue_success_rate / opp_total if opp_total > 0 else 0.5
            agent1_opponent_info.append((agent2_in_pair.name, opp_p_blue, agent2_in_pair.stick_probability))
    
    return (agent1_rounds, agent1_signal_prob_history, agent1_stick_history,
            agent1_success_history, agent1_opponent_info, agents)

# ============================
# 数据可视化
# ============================
def plot_agent1_data(rounds, signal_probs, stick_probs, success_history):
    """
    绘制 Agent 1 的演变情况：
      - 上图显示 Agent 1 信号决策参数（选择 Blue 的概率）与坚持自己决策的概率；
      - 下图显示 Agent 1 的交互成功率（移动平均平滑）。
    """
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    # 子图1：参数演变
    axs[0].plot(rounds, signal_probs, label="Agent 1 Signal p(Blue)", color="blue")
    axs[0].plot(rounds, stick_probs, label="Agent 1 Stick Probability", color="green")
    axs[0].set_xlabel("Round")
    axs[0].set_ylabel("Probability")
    axs[0].set_title("Evolution of Agent 1 Decision Parameters")
    axs[0].legend()
    
    # 子图2：交互成功率（移动平均）
    window = 10
    moving_avg = [sum(success_history[max(0, i-window):i+1]) / (i - max(0, i-window) + 1) for i in range(len(success_history))]
    axs[1].plot(rounds, moving_avg, label="Agent 1 Moving Avg Success Rate", color="red")
    axs[1].set_xlabel("Round")
    axs[1].set_ylabel("Success Rate")
    axs[1].set_title("Agent 1 Interaction Success Rate (Moving Average)")
    axs[1].legend()
    
    plt.tight_layout()
    plt.show()

# ============================
# 主函数
# ============================
def main():
    num_rounds = 100000   # 模拟 10000 轮
    num_agents = 20
    (agent1_rounds, agent1_signal_probs, agent1_stick_probs,
     agent1_success_history, agent1_opponent_info, agents) = run_simulation(num_rounds, num_agents)
    
    # 输出 Agent 1 最近 10 次交互的信息
    print("Agent 1 Interaction Data (last 10 interactions):")
    for i in range(-10, 0):
        if abs(i) <= len(agent1_rounds):
            round_num = agent1_rounds[i]
            opp_name, opp_p_blue, opp_stick = agent1_opponent_info[i]
            success = agent1_success_history[i]
            print(f"Round {round_num}: Opponent = {opp_name}, Opponent p(Blue) = {opp_p_blue:.2f}, Opponent Stick = {opp_stick:.2f}, Success = {success}")
    
    # 可视化 Agent 1 的数据
    plot_agent1_data(agent1_rounds, agent1_signal_probs, agent1_stick_probs, agent1_success_history)

if __name__ == '__main__':
    main()
