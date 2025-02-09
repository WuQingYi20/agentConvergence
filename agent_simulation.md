# Agent Decision-Making Pseudocode

## Signal Decision
```pseudo
Function decide_signal(history, isFirstMove):
    If isFirstMove:
        If random() < 0.5:
            signal = Blue
        Else:
            signal = Red
    Else:
        // Calculate Blue bias from history:
        blue_ratio = history.getBlueRatio()  // (# of Blue interactions) / (total interactions)
        If random() < blue_ratio:
            signal = Blue
        Else:
            signal = Red
    Return signal


Function decide_side(opponent_signal, own_signal, history):
    If (opponent_signal == Blue AND own_signal == Blue) OR (opponent_signal == Red AND own_signal == Red):
        side = own_signal  // Align with the signal
    Else:
        // Calculate Blue bias for choices:
        blue_choice_ratio = history.getBlueChoiceRatio()  // (# of Blue choices) / (total interactions)
        If random() < blue_choice_ratio:
            side = Blue
        Else:
            side = Red
    Return side
