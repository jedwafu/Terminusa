import sqlite3
import random
import hashlib
import json
import traceback
from contextlib import contextmanager
import bcrypt
from getpass import getpass
from datetime import datetime

DATABASE_NAME = "terminusa.db"

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect(DATABASE_NAME)
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        with self.transaction() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    tac_balance INTEGER DEFAULT 100,
                    health INTEGER DEFAULT 100
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    player_id TEXT REFERENCES players(username),
                    item_name TEXT,
                    quantity INTEGER,
                    PRIMARY KEY (player_id, item_name)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS marketplace (
                    listing_id INTEGER PRIMARY KEY,
                    seller TEXT REFERENCES players(username),
                    item_name TEXT,
                    price INTEGER,
                    quantity INTEGER,
                    listed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    description TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_achievements (
                    player_id TEXT REFERENCES players(username),
                    achievement_id INTEGER REFERENCES achievements(achievement_id),
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (player_id, achievement_id)
                )
            ''')
            cursor.execute('''
                INSERT OR IGNORE INTO achievements VALUES
                (1, 'First Core', 'Mine your first TAC'),
                (2, 'Corruption Purge', 'Defeat your first TAC Goblin'),
                (3, 'Quantum Trade', 'Complete your first marketplace transaction')
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON players(username)')

    @contextmanager
    def transaction(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_player(self, username):
        with self.transaction() as cursor:
            cursor.execute('SELECT * FROM players WHERE username = ?', (username,))
            return cursor.fetchone()

    def save_player(self, player):
        with self.transaction() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO players 
                (username, password_hash, level, tac_balance, health)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                player.username,
                player.password_hash,
                player.level,
                player.tac_balance,
                player.health
            ))

class Player:
    def __init__(self, username, password=None):
        self.db = DatabaseManager()
        self.username = username
        self.password_hash = self._hash_password(password) if password else ''
        self.level = 1
        self.tac_balance = 100
        self.health = 100
        self.inventory = self._load_inventory()

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode(), self.password_hash.encode())
        except ValueError:
            return False

    def _load_inventory(self):
        with self.db.transaction() as cursor:
            cursor.execute('SELECT item_name, quantity FROM inventory WHERE player_id = ?', 
                         (self.username,))
            return {row[0]: row[1] for row in cursor.fetchall()}

    def save_inventory(self):
        with self.db.transaction() as cursor:
            cursor.execute('DELETE FROM inventory WHERE player_id = ?', (self.username,))
            for item, quantity in self.inventory.items():
                cursor.execute('''
                    INSERT INTO inventory (player_id, item_name, quantity)
                    VALUES (?, ?, ?)
                ''', (self.username, item, quantity))

    def add_item(self, item_name, quantity=1):
        self.inventory[item_name] = self.inventory.get(item_name, 0) + quantity
        self.save_inventory()

    def remove_item(self, item_name, quantity=1):
        if self.inventory.get(item_name, 0) >= quantity:
            self.inventory[item_name] -= quantity
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            self.save_inventory()
            return True
        return False

    def save(self):
        try:
            self.db.save_player(self)
            self.save_inventory()
        except Exception as e:
            print(f"Neural sync error: {str(e)}")
            traceback.print_exc()

    @classmethod
    def load(cls, username):
        try:
            db = DatabaseManager()
            player_data = db.get_player(username)
            if player_data:
                new_player = cls(username)
                new_player.password_hash = player_data[1]
                new_player.level = player_data[2]
                new_player.tac_balance = player_data[3]
                new_player.health = player_data[4]
                return new_player
            return None
        except Exception as e:
            print(f"Neural load error: {str(e)}")
            return None

class Game:
    def __init__(self):
        self.current_player = None
        self.db = DatabaseManager()

    def login(self):
        try:
            username = input("Username: ").strip()
            password = getpass("Password: ").strip()
            
            if not self.validate_credentials(username, password):
                return False
                
            player = Player.load(username)
            if not player:
                print("Neural pattern not found")
                return False
                
            if not player.check_password(password):
                print("Invalid quantum signature")
                return False
                
            self.current_player = player
            print(f"Welcome back, {username}!")
            return True
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False

    def validate_credentials(self, username, password):
        if len(username) < 4:
            print("Neural handle must be at least 4 characters")
            return False
        if len(password) < 8:
            print("Quantum key must be at least 8 characters")
            return False
        return True

    def register(self):
        try:
            username = input("New neural handle: ").strip()
            password = getpass("New quantum key: ").strip()
            
            if not self.validate_credentials(username, password):
                return False
                
            if Player.load(username):
                print("Neural pattern already exists")
                return False
                
            self.current_player = Player(username, password)
            self.current_player.save()
            print("Neural imprint registered!")
            return True
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False

    def explore(self):
        try:
            print("\nAccessing quantum compute node...")
            reward = random.randint(10, 50)
            self.current_player.tac_balance += reward
            self.current_player.add_item('TAC', reward)
            print(f"Decrypted {reward} TAC from quantum matrix!")
            self.current_player.save()
            
            if reward > 0:
                self.check_achievements([1])
                
        except Exception as e:
            print(f"Quantum mining error: {str(e)}")
            traceback.print_exc()

    def battle(self):
        try:
            enemy_health = 50
            first_kill = True
            print("\nALERT: Corrupted TAC Goblin detected!")
            
            while self.current_player.health > 0 and enemy_health > 0:
                print(f"\nSystem Integrity: {self.current_player.health}")
                print(f"Enemy Core Stability: {enemy_health}")
                
                choice = input("Engage (e) or Retreat (r): ").lower().strip()
                
                if choice == "e":
                    damage = random.randint(5, 20)
                    enemy_health -= damage
                    print(f"Dealt {damage} quantum damage!")
                    
                    if enemy_health <= 0:
                        print("Threat neutralized! +50 TAC")
                        self.current_player.tac_balance += 50
                        self.current_player.add_item('TAC', 50)
                        self.current_player.save()
                        if first_kill:
                            self.check_achievements([2])
                            first_kill = False
                        break
                        
                    enemy_damage = random.randint(5, 15)
                    self.current_player.health -= enemy_damage
                    print(f"Goblin counterattack: {enemy_damage} system damage!")
                    
                    if self.current_player.health <= 0:
                        print("CRITICAL FAILURE: Neural link compromised!")
                        self.handle_defeat()
                        break
                        
                elif choice == "r":
                    print("Emergency retreat protocol engaged")
                    break
                else:
                    print("Invalid command sequence!")

        except Exception as e:
            print(f"Combat simulation error: {str(e)}")
            traceback.print_exc()

    def handle_defeat(self):
        penalty = min(50, self.current_player.tac_balance)
        self.current_player.tac_balance -= penalty
        self.current_player.health = 100
        self.current_player.save()
        print(f"System reboot complete. TAC penalty: {penalty}")

    def check_achievements(self, achievement_ids):
        with self.db.transaction() as cursor:
            for aid in achievement_ids:
                cursor.execute('''
                    INSERT OR IGNORE INTO player_achievements 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (self.current_player.username, aid))

    def marketplace_menu(self):
        while True:
            print("\n=== TAC Marketplace ===")
            print("1. Browse Listings")
            print("2. Create Listing")
            print("3. My Contracts")
            print("4. Return to Core")
            choice = input("> ").strip()
            
            if choice == "1":
                self.browse_listings()
            elif choice == "2":
                self.create_listing()
            elif choice == "3":
                self.view_my_listings()
            elif choice == "4":
                break

    def browse_listings(self):
        with self.db.transaction() as cursor:
            cursor.execute('''
                SELECT listing_id, item_name, price, quantity, seller 
                FROM marketplace
                WHERE seller != ?
            ''', (self.current_player.username,))
            listings = cursor.fetchall()
            
        if not listings:
            print("Quantum market void detected")
            return
            
        for listing in listings:
            print(f"\nContract ID: {listing[0]}")
            print(f"Resource: {listing[1]} x{listing[3]}")
            print(f"Price: {listing[2]} TAC/unit")
            print(f"Vendor: {listing[4]}")

        listing_id = input("\nEnter contract ID to acquire (or void to cancel): ").strip()
        if listing_id:
            self.purchase_listing(int(listing_id))

    def purchase_listing(self, listing_id):
        with self.db.transaction() as cursor:
            cursor.execute('''
                SELECT seller, item_name, price, quantity 
                FROM marketplace 
                WHERE listing_id = ?
            ''', (listing_id,))
            listing = cursor.fetchone()
            
            if not listing:
                print("Quantum anomaly detected: Invalid ID")
                return

            seller, item_name, price, quantity = listing
            total_cost = price * quantity
            
            if self.current_player.tac_balance < total_cost:
                print("Insufficient TAC reserves")
                return
                
            self.current_player.tac_balance -= total_cost
            cursor.execute('''
                UPDATE players 
                SET tac_balance = tac_balance + ? 
                WHERE username = ?
            ''', (total_cost, seller))
            
            self.current_player.add_item(item_name, quantity)
            cursor.execute('DELETE FROM marketplace WHERE listing_id = ?', (listing_id,))
            self.check_achievements([3])
            print("Quantum transfer complete!")

    def create_listing(self):
        print("\nNeural Inventory:")
        for item, quantity in self.current_player.inventory.items():
            print(f"- {item}: {quantity}")
            
        item_name = input("\nEnter resource to list: ").strip()
        if item_name not in self.current_player.inventory:
            print("Inventory anomaly detected")
            return
            
        available = self.current_player.inventory[item_name]
        quantity = int(input(f"Enter quantity (max {available}): "))
        if quantity > available:
            print("Resource deficit detected")
            return
            
        price = int(input("Enter TAC/unit: "))
        
        with self.db.transaction() as cursor:
            cursor.execute('''
                INSERT INTO marketplace 
                (seller, item_name, price, quantity)
                VALUES (?, ?, ?, ?)
            ''', (
                self.current_player.username,
                item_name,
                price,
                quantity
            ))
            
        self.current_player.remove_item(item_name, quantity)
        print("Quantum contract established!")

    def view_my_listings(self):
        with self.db.transaction() as cursor:
            cursor.execute('''
                SELECT listing_id, item_name, price, quantity 
                FROM marketplace 
                WHERE seller = ?
            ''', (self.current_player.username,))
            listings = cursor.fetchall()
            
        if not listings:
            print("No active contracts detected")
            return
            
        for listing in listings:
            print(f"\nContract ID: {listing[0]}")
            print(f"Resource: {listing[1]} x{listing[3]}")
            print(f"Price: {listing[2]} TAC/unit")

    def view_achievements(self):
        with self.db.transaction() as cursor:
            cursor.execute('''
                SELECT a.name, a.description, pa.unlocked_at 
                FROM player_achievements pa
                JOIN achievements a ON pa.achievement_id = a.achievement_id
                WHERE pa.player_id = ?
            ''', (self.current_player.username,))
            achievements = cursor.fetchall()
            
        if not achievements:
            print("Quantum archive empty")
            return
            
        print("\n=== Neural Achievements ===")
        for name, desc, unlocked in achievements:
            print(f"{name}: {desc} (Unlocked: {unlocked})")

    def main_menu(self):
        try:
            while True:
                print("\n=== Terminusa: Quantum Frontier ===")
                print("1. Quantum Mine")
                print("2. Combat Simulation")
                print("3. Neural Interface")
                print("4. TAC Marketplace")
                print("5. Achievements")
                print("6. Logout")
                choice = input("> ").strip()
                
                if choice == "1":
                    self.explore()
                elif choice == "2":
                    self.battle()
                elif choice == "3":
                    print(f"\nTAC Reserves: {self.current_player.tac_balance}")
                    print("Neural Inventory:")
                    for item, qty in self.current_player.inventory.items():
                        print(f"- {item}: {qty}")
                    print(f"System Integrity: {self.current_player.health}/100")
                elif choice == "4":
                    self.marketplace_menu()
                elif choice == "5":
                    self.view_achievements()
                elif choice == "6":
                    print("Stabilizing quantum link...")
                    self.current_player.save()
                    print("Neural disconnect complete")
                    break
                else:
                    print("Invalid quantum command!")
        except Exception as e:
            print(f"Quantum interface instability detected: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        game = Game()
        print("████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗██╗   ██╗███████╗ █████╗ ")
        print("╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██║   ██║██╔════╝██╔══██╗")
        print("   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║██║   ██║███████╗███████║")
        print("   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║   ██║╚════██║██╔══██║")
        print("   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝███████║██║  ██║")
        print("   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝")
        print("1. Authenticate\n2. New Imprint")
        auth_choice = input("> ").strip()
        
        if auth_choice == "1":
            if game.login():
                game.main_menu()
        elif auth_choice == "2":
            if game.register():
                game.main_menu()
        else:
            print("Invalid quantum signal")
            
    except KeyboardInterrupt:
        print("\nEmergency quantum disconnect initiated")
    finally:
        db = DatabaseManager._instance
        if db:
            db.conn.close()