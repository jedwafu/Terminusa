import os
import asyncio
from getpass import getpass
from blockchain import QuantumBlockchain
from security import SessionManager, CryptoEngine
from accessibility import AssistedMode, LowSpecAdapter
from config import TerminusaConfig

class TerminusaCLI:
    def __init__(self):
        self.blockchain = QuantumBlockchain()
        self.sessions = SessionManager()
        self.player = None
        self.assist = AssistedMode()
        self.performance = LowSpecAdapter()

    async def main_loop(self):
        print("=== Terminusa: Quantum Frontier ===")
        print("1. Login\n2. Register\n3. Quick Start\n4. Exit")
        choice = input("> ")
        
        if choice == "1":
            await self.login()
        elif choice == "2":
            await self.register()
        elif choice == "3":
            await self.quick_start()
        else:
            exit()

    async def game_menu(self):
        while True:
            print(f"\nPlayer: {self.player['username']}")
            print(f"TAC: {self.player['tac']} | KOII: {self.player['koii']}")
            print("1. Mine\n2. Battle\n3. Market\n4. Achievements\n5. Help\n6. Quit")
            choice = input("> ")
            
            if choice == "1":
                await self.mine_interface()
            elif choice == "2":
                await self.battle_interface()
            elif choice == "6":
                await self.logout()
                break

if __name__ == "__main__":
    game = TerminusaCLI()
    asyncio.run(game.main_loop())