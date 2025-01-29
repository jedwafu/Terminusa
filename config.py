import os

class TerminusaConfig:
    def __init__(self):
        self.TAC_MAX = 10**10
        self.KOII_RATE = 100
        self.INITIAL_TAC = 100
        self.NODE_ENDPOINT = os.getenv('KOII_NODE', 'https://node.koii.network')