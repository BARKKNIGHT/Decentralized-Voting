'''
Write a initialization file to:
1.Create users.db and blockchain.db
'''
import os
import subprocess
from Blockchain import init_db as blockchain_db
from User import init_db as user_db
import time

def init_databases():
    print("🔄 Initializing databases...")

    # Create and initialize users and blockchain databases
    user_db.init_db("users.db")
    blockchain_db.init_db("blockchain.db")

    time.sleep(1)
    print("✅ Databases initialized successfully!\n")

def display_welcome_message():
    print("=" * 50)
    print("🎉 WELCOME TO THE DECENTRALIZED VOTING SYSTEM 🎉")
    print("=" * 50)
    print("Your secure and transparent voting platform.\n")
    time.sleep(1)

def display_menu():
    print("Please select an option to proceed:")
    print("1. Initialize databases")
    print("2. Start the voting system (run app.py and app_blockchain.py)")
    print("3. Exit\n")

def start_voting_system():
    print("\n🚀 Starting the voting system...")
    # Run app.py and app_blockchain.py in background
    try:
        app_process = subprocess.Popen(['python', 'app.py'])
        app_blockchain_process = subprocess.Popen(['python', 'app_blockchain.py'])
        
        print("📢 Voting system components are running.")
        print("🔴 Press Ctrl+C to stop both processes.")

        # Wait for processes to finish (Ctrl+C to terminate them)
        app_process.wait()
        app_blockchain_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down the voting system...")
        app_process.terminate()
        app_blockchain_process.terminate()
        print("✅ Voting system shut down successfully.")

def main():
    os.system("clear" if os.name == "posix" else "cls")
    display_welcome_message()
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            init_databases()
        elif choice == '2':
            start_voting_system()
        elif choice == '3':
            print("\nThank you for using the Decentralized Voting System. Goodbye! 👋")
            break
        else:
            print("❗ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()

