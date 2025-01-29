class AssistedMode:
    HELP = {
        'mine': "Solve quantum puzzles to earn TAC",
        'koii': "Trade TAC for KOII to participate in governance"
    }

    def show_help(self, topic):
        print(f"\n💡 {self.HELP.get(topic, 'Help not available')}")

class LowSpecAdapter:
    def __init__(self):
        self.performance_mode = False
        
    def toggle_mode(self):
        self.performance_mode = not self.performance_mode
        print(f"Performance mode {'enabled' if self.performance_mode else 'disabled'}")