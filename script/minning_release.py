import os
import subprocess
from git import Repo
import glob

# Configurações
repo_url = 'https://github.com/mockito/mockito'  # URL do repositório
local_path = r'C:\minning'  # Caminho onde o repositório será clonado
output_dir = r'C:\minning\spotbugs_results'  # Caminho para salvar os resultados XML
gradle_path = r"C:\Gradle\gradle-8.10.2\bin\gradle.bat"  # ajuste o caminho conforme necessário

# Criar diretório de saída para resultados XML, se não existir
os.makedirs(output_dir, exist_ok=True)

# Clonar o repositório (somente se ainda não existir)
if not os.path.exists(local_path):
    Repo.clone_from(repo_url, local_path)
    print(f"Repositório clonado em {local_path}")
else:
    print("Repositório já clonado.")

# Acessa o repositório com GitPython
repo = Repo(local_path)
assert not repo.bare  # Verifica se o repositório foi clonado corretamente

# Obtém todas as tags e inverte a ordem
tags = list(repo.tags)[::-1]  # Inverte a lista de tags para pegar da mais recente para a mais antiga

# Itera por todas as tags (limite de 20) e faz o checkout de cada uma
for index, tag in enumerate(tags[:20]):  # Limita a análise para as 20 últimas tags
    # Tenta stash as alterações antes do checkout
    try:
        repo.git.stash("save")  # Stash as alterações não comitadas
    except Exception as e:
        print(f"Erro ao fazer stash das alterações: {e}")

    # Realiza o checkout para a release atual
    try:
        repo.git.checkout(tag)
        print(f"\nCheckout realizado para release: {tag}")
    except Exception as e:
        print(f"Erro ao fazer checkout da tag {tag}: {e}")
        continue

    # Verifica se o arquivo build.gradle existe
    build_gradle_path = os.path.join(local_path, 'build.gradle')
    if not os.path.exists(build_gradle_path):
        print(f"Arquivo build.gradle não encontrado para a release {tag}. Pulando...")
        continue

    # Caminho do arquivo JAR
    jar_file = os.path.join(local_path, 'build', 'libs', f'{tag.name}.jar')

    # Verifica se o arquivo JAR já existe
    if os.path.exists(jar_file):
        print(f"Arquivo JAR encontrado: {jar_file}. Pulando a compilação.")
    else:
        # Compila com Java 21 para as três primeiras tags, e Java 19 para as demais
        if index < 3:
            java_version = "21"
            subprocess.run(["C:\\Program Files\\Java\\jdk-21\\bin\\javac", "-version"], check=True)
        else:
            java_version = "19"
            subprocess.run(["C:\\Program Files\\Java\\jdk-19\\bin\\javac", "-version"], check=True)

        # Executa o Gradle para gerar o JAR sem rodar os testes
        try:
            subprocess.run([gradle_path, "clean", "build", "-x", "test"], cwd=local_path, check=True)
            print(f"JAR gerado com sucesso para a release: {tag}")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao gerar JAR para a release {tag}: {e}")
            continue

    # Caminho do arquivo XML de saída para esta release
    output_file = os.path.join(output_dir, f"{tag}.xml")

    # Executa o SpotBugs com FindSecBugs no código da release atual
    try:
        subprocess.run(
            [
                r"C:\spotbugs-4.8.6\bin\spotbugs.bat", "-textui", "-effort:max", "-xml",
                "-output", output_file, jar_file  # Passa o arquivo JAR do projeto
            ],
            check=True
        )

        print(f"Análise do SpotBugs concluída para release: {tag}. Resultados salvos em {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar SpotBugs para a release {tag}: {e}")

print("Análise concluída para as 20 releases.")
