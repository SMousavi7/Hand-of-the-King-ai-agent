import os
import random
import shutil
import subprocess

# Define directory for generations
GEN_DIR = "generations"
INITIAL_POPULATION = 40
PARAMS = [
    "Stark", "Greyjoy", "Lannister", "Targaryen", "Baratheon", "Tyrell", "Tully", "Half", "Companion", "Combo"
]
gen_number = 0
# Ensure directory exists
os.makedirs(GEN_DIR, exist_ok=True)

def generate_initial_population():
    """Generates 40 random configuration files."""
    for i in range(INITIAL_POPULATION - 20):
        file_path = os.path.join(GEN_DIR, f"gen_{i}.txt")
        with open(file_path, "w") as f:
            for param in PARAMS:
                if(param == "Half"):
                    value = random.randint(-10, 0)  # Restrict initial values
                    f.write(f"{param} {value}\n")    
                else:
                    value = random.randint(5, 15)
                    f.write(f"{param} {value}\n")
                

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

def tournament_selection():
    """Runs a tournament selection and keeps only winners."""
    files = os.listdir(GEN_DIR)
    if len(files) < 2:
        return
    
    winners = []
    random.shuffle(files)
    for i in range(0, len(files), 2):
        if i+1 >= len(files):
            winners.append(files[i])
            continue
        file1, file2 = os.path.join(GEN_DIR, files[i]), os.path.join(GEN_DIR, files[i+1])
        winner = play_match(file1, file2)
        winners.append(winner)
        os.remove(file1 if winner == file2 else file2)
    return winners

def crossover_and_mutation(winners):
    """Generates new children from winners."""
    random.shuffle(winners)
    new_population = winners[:]
    
    for i in range(0, len(winners), 2):
        if i+1 >= len(winners):
            continue
        parent1, parent2 = winners[i], winners[i+1]
        
        with open(parent1, "r") as f1, open(parent2, "r") as f2:
            p1_data = [line.strip().split() for line in f1.readlines()]
            p2_data = [line.strip().split() for line in f2.readlines()]
        
        child1_data, child2_data = [], []
        for (k1, v1), (k2, v2) in zip(p1_data, p2_data):
            v1, v2 = int(v1), int(v2)
            if random.random() < 0.5:
                child1_data.append(f"{k1} {v1}")
                child2_data.append(f"{k2} {v2}")
            else:
                child1_data.append(f"{k1} {v2}")
                child2_data.append(f"{k2} {v1}")
            
            # Mutation
            if random.random() < 0.1:
                child1_data[-1] = f"{k1} {v1 + random.randint(-2, 2)}"
            if random.random() < 0.1:
                child2_data[-1] = f"{k2} {v2 + random.randint(-2, 2)}"
        
        child1_path = os.path.join(GEN_DIR, f"child_{i}_{gen_number}.txt")
        child2_path = os.path.join(GEN_DIR, f"child_{i+1}_{gen_number}.txt")
        
        with open(child1_path, "w") as f1, open(child2_path, "w") as f2:
            f1.write("\n".join(child1_data))
            f2.write("\n".join(child2_data))
        
        new_population.append(child1_path)
        new_population.append(child2_path)
    
    return new_population

# Run GA
if __name__ == "__main__":
    generate_initial_population()
    for gen in range(10):  # Run for 10 generations
        print(f"Generation {gen}:")
        winners = tournament_selection()
        if len(winners) <= 1:
            break  # End if only one file remains
        new_population = crossover_and_mutation(winners)
        gen_number += 1
        print(f"Remaining Population: {len(new_population)}")
