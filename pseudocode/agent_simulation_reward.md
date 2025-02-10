Initialize for each agent:
    p_signal ← 0.5   // 信号决策偏好
    p_choice ← 0.5   // 决策冲突时坚持自己的概率

For each round:
    For each agent:
         signal = "Blue" with probability p_signal, else "Red"
    For each pair (agent A, agent B) randomly配对:
         A_signal, B_signal are sent
         For each agent:
             If (A_signal == B_signal):
                  final_decision = A_signal (or B_signal)
             Else:
                  final_decision = own_signal with probability p_choice, 
                                   else opponent_signal

         Determine outcome = (A_final == B_final)  // success or failure

         For each agent in the pair:
             // Update p_signal:
             If success:
                 If agent sent Blue:
                     p_signal ← p_signal + ALPHA*(1 - p_signal)
                 Else:  // sent Red
                     p_signal ← p_signal - ALPHA*(p_signal)
             Else: // failure
                 If agent sent Blue:
                     p_signal ← p_signal - BETA*(p_signal)
                 Else:
                     p_signal ← p_signal + BETA*(1 - p_signal)

             // Update p_choice only if signals were different:
             If (agent's own signal != opponent's signal):
                 If success and agent final decision == own signal:
                     p_choice ← p_choice + ALPHA*(1 - p_choice)
                 Else if failure and agent final decision == own signal:
                     p_choice ← p_choice - BETA*(p_choice)
                 (可以对其他情况进行对称更新)
