import argparse
import subprocess
import sys
import re
from concurrent.futures import ThreadPoolExecutor

# Codes ANSI pour les couleurs
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'

signature = """
***********************************************************
*                                                         *
*                Script d'attaque de force brute          *
*                         by Assa                         *
*                                                         *
***********************************************************
"""

print(signature)

def try_password(file_path, password, output_file, keyword=None):
    command = f'stegsnow -C -p {password} {file_path}'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='latin-1')

    if keyword and re.search(keyword, result.stdout):
        with open(output_file, 'a') as out_file:
            out_file.write(f'Message extrait avec le mot de passe : {password}\n')
            out_file.write(result.stdout + '\n')
        print(BLUE + f"\nMot clé '{keyword}' trouvé avec le mot de passe : {password}" + ENDC)
        print(BLUE + "Message décodé:")
        lines = result.stdout.split('\n')
        for line in lines:
            if keyword in line:
                print(RED + line + ENDC)

    elif result.returncode == 0:
        with open(output_file, 'a') as out_file:
            out_file.write(f'Message extrait avec le mot de passe : {password}\n')
            out_file.write(result.stdout + '\n')
    else:
        with open(output_file, 'a') as out_file:
            out_file.write(f"Tentative avec le mot de passe '{password}' a échoué.\n")

parser = argparse.ArgumentParser(description='Script d\'attaque de force brute pour stegsnow')
parser.add_argument('--file', required=True, help='Chemin du fichier cible')
parser.add_argument('--wordlist', required=True, help='Chemin du fichier de mots de passe')
parser.add_argument('--output', required=True, help='Chemin du fichier de sortie des résultats')
parser.add_argument('--keyword', help='Mot clé à rechercher dans les résultats')
args = parser.parse_args()

file_path = args.file
password_file = args.wordlist
output_file = args.output
keyword = args.keyword

# Charger la liste des mots de passe depuis le fichier rockyou.txt
with open(password_file, 'rb') as f:
    lines = f.readlines()

num_threads = 4  # nombre de threads
total_passwords = len(lines)
start_index = int(0.00 * total_passwords)  # pourcentage d'avancement
progress = 0

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    for line in lines[start_index:]:
        try:
            password = line.decode('latin-1').strip()
        except UnicodeDecodeError:
            continue

        executor.submit(try_password, file_path, password, output_file, keyword)

        # Mise à jour de la progression et affichage du pourcentage
        progress += 1
        percentage = ((start_index + progress) / total_passwords) * 100

        # Effacer la ligne précédente et afficher le nouveau pourcentage
        sys.stdout.write("\r" + f"Progression : {percentage:.2f}%")
        sys.stdout.flush()

print("\nFin de l'attaque de force brute. Les résultats ont été enregistrés dans", output_file)