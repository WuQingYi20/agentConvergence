# Agent Decision-Making Pseudocode with Gradually Decaying Exploration

# 全局探索参数
initial_exploration_rate = 0.5      // 初始探索率
decay_factor = 0.99                 // 每个迭代步长的衰减因子
min_exploration_rate = 0         // 探索率下限，保证永远有一定的随机性

# 计算当前探索率（梯度衰减）
Function get_exploration_rate(iteration):
    exploration_rate = initial_exploration_rate * (decay_factor ^ iteration)
    If exploration_rate < min_exploration_rate:
         exploration_rate = min_exploration_rate
    Return exploration_rate


## Signal Decision
Function decide_signal(history, isFirstMove, iteration):
    exploration_rate = get_exploration_rate(iteration)
    
    // 初始移动或处于探索阶段时，随机选择信号
    If isFirstMove OR random() < exploration_rate:
        If random() < 0.5:
            signal = Blue
        Else:
            signal = Red
    Else:
        // 利用历史数据，根据信号获得奖励的近期成功率决策
        blue_success_rate = history.getBlueSuccessRate()  // Blue信号近期奖励比例
        If random() < blue_success_rate:
            signal = Blue
        Else:
            signal = Red
    Return signal


Function decide_side(opponent_signal, own_signal, history, iteration):
    exploration_rate = get_exploration_rate(iteration)
    
    If opponent_signal == own_signal:
        side = own_signal  // 信号一致时直接采用该信号
    Else:
        // 信号不一致时，先判断是否进入探索阶段
        If random() < exploration_rate:
            // 探索：随机选择自己的信号或对方信号
            If random() < 0.5:
                side = own_signal
            Else:
                side = opponent_signal
        Else:
            // 利用：根据信号冲突时坚持自己决策的近期成功率判断
            stick_probability = history.getStickProbability()  // 坚持自己获得奖励的比例
            If random() < stick_probability:
                side = own_signal
            Else:
                side = opponent_signal
    Return side


// 更新历史数据，根据交互结果调整未来决策倾向
Function update_history(history, own_signal, chosen_side, interaction_success):
    // interaction_success为True表示双方方向一致（奖励），为False表示不一致（惩罚）
    learning_rate = 0.1  // 学习率，控制加权移动平均更新速度

    // 更新信号成功率：根据信号使用后的奖励反馈更新近期成功率
    If own_signal == Blue:
        history.updateBlueSuccess(interaction_success, learning_rate)
    Else:
        history.updateRedSuccess(interaction_success, learning_rate)
    
    // 更新冲突下坚持自己信号的成功率
    If chosen_side == own_signal:
        history.updateStickProbability(interaction_success, learning_rate)
    Else:
        history.updateStickProbability( not interaction_success, learning_rate)
