import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from packaging import version  # Importa o módulo de versionamento

# Configurações
output_dir = r'C:\minning\spotbugs_results'  # Caminho para os resultados XML

# Inicializa um dicionário para armazenar contagens de bugs por release
bug_counter_by_release = defaultdict(Counter)

# Percorre todos os arquivos XML no diretório de resultados
for xml_file in os.listdir(output_dir):
    if xml_file.endswith('.xml'):
        file_path = os.path.join(output_dir, xml_file)
        release_name = os.path.splitext(xml_file)[0]  # Nome da release sem a extensão
        print(f"Lendo arquivo: {file_path} (Release: {release_name})")

        # Lê o arquivo XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Verifica se há BugInstances e conta os tipos
        for bug_instance in root.findall('BugInstance'):
            bug_type = bug_instance.get('type')  # Tipo do bug
            if bug_type:  # Verifica se o tipo do bug existe
                bug_counter_by_release[release_name][bug_type] += 1
                print(f"Encontrado bug: {bug_type} na release {release_name}")

# Ordena as releases usando a função de comparação do módulo 'packaging.version'
sorted_releases = sorted(bug_counter_by_release.keys(), key=version.parse)

# Gráfico de barras para cada release
for release in sorted_releases:
    bugs = bug_counter_by_release[release]
    bug_types = list(bugs.keys())
    bug_counts = list(bugs.values())

    plt.figure(figsize=(10, 6))
    plt.barh(bug_types, bug_counts, color='lightcoral')
    plt.xlabel('Número de Ocorrências')
    plt.ylabel('Tipo de Bug')
    plt.title(f'Bugs Encontrados pelo SpotBugs na Release: {release}')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Gráfico de linhas para o número total de bugs por release
total_bugs_per_release = {release: sum(bugs.values()) for release, bugs in bug_counter_by_release.items()}

# Ordena os bugs por release para garantir a sequência correta
sorted_bug_counts = [total_bugs_per_release[release] for release in sorted_releases]

plt.figure(figsize=(12, 6))
plt.plot(sorted_releases, sorted_bug_counts, marker='o', linestyle='-', color='b')
plt.xlabel('Release')
plt.ylabel('Número Total de Bugs')
plt.title('Evolução do Número Total de Bugs por Release')
plt.xticks(rotation=45)  # Rotaciona os rótulos das releases para melhor legibilidade
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
