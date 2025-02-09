Function decide_signal(p_signal):
    // p_signal：agent 在信号阶段选择 “Blue” 的内部概率
    If random() < p_signal:
        return Blue
    Else:
        return Red

Function decide_side(own_signal, opponent_signal, p_choice):
    If own_signal == opponent_signal:
        // 当双方信号一致时，直接选择该共同信号
        return own_signal
    Else:
        // 当双方信号不一致时，根据 p_choice 随机决策
        If random() < p_choice:
            return Blue
        Else:
            return Red

Function update_biases(chosen_signal, chosen_side, outcome, lr, p_signal, p_choice):
    // outcome: 如果协调成功（双方选择一致）则为1，否则为0
    // lr: 学习率，用于控制更新的步长
    
    // 更新信号偏好（p_signal）
    If outcome == 1:
        // 协调成功：强化当前选择
        If chosen_signal == Blue:
            p_signal = p_signal + lr * (1 - p_signal)
        Else:  // chosen_signal == Red
            p_signal = p_signal - lr * p_signal
    Else:
        // 协调失败：将 p_signal 调整回中性（0.5）
        If chosen_signal == Blue:
            p_signal = p_signal - lr * (p_signal - 0.5)
        Else:  // chosen_signal == Red
            p_signal = p_signal + lr * (0.5 - p_signal)
    
    // 同样更新选择偏好（p_choice）
    If outcome == 1:
        If chosen_side == Blue:
            p_choice = p_choice + lr * (1 - p_choice)
        Else:  // chosen_side == Red
            p_choice = p_choice - lr * p_choice
    Else:
        If chosen_side == Blue:
            p_choice = p_choice - lr * (p_choice - 0.5)
        Else:  // chosen_side == Red
            p_choice = p_choice + lr * (0.5 - p_choice)
    
    Return p_signal, p_choice
