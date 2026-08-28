import os
import random
import shutil
import subprocess

directory = "generations"

def play_match(file1, file2):
    """Plays a match between two files and returns the winner."""
    shutil.copy(file1, "a.txt")
    shutil.copy(file2, "b.txt")
    
    subprocess.run(["python", "main1.py", "--player1", "ghadim_agent1", "--player2", "ghadim_agent2"], capture_output=True)
    
    with open("result.txt", "r") as f:
        result = f.read().strip()
    
    if "Player 1 wins" in result:
        return file1
    else:
        return file2

def elimination_tournament():
    """Runs a knockout tournament until only one file remains."""
    while True:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]
        
        if len(files) == 1:
            print(f"Winner: {files[0]}")
            break
        
        random.shuffle(files)
        for i in range(0, len(files) - 1, 2):
            file1, file2 = files[i], files[i+1]
            winner = play_match(file1, file2)
            os.remove(file1 if winner == file2 else file2)

def main():
    elimination_tournament()

if __name__ == "__main__":
    main()
