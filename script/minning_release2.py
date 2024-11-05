import os
import subprocess
from git import Repo
import glob  # Import para encontrar arquivos com padrões

# Configurações
repo_url = 'https://github.com/mockito/mockito'  # URL do repositório
local_path = r'C:\minning'  # Caminho onde o repositório será clonado
jars_dir = os.path.join(local_path, 'JARS')  # Caminho para salvar os arquivos JAR
gradle_path = r"C:\Gradle\gradle-8.10.2\bin\gradle.bat"  # Ajuste o caminho conforme necessário

# Criar diretório de saída para JARs, se não existir
os.makedirs(jars_dir, exist_ok=True)

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

    # Caminho esperado para os JARs gerados em build/libs
    jar_output_path = os.path.join(jars_dir, f'{tag.name}.jar')

    # Verifica se o arquivo JAR já existe no diretório JARS
    if os.path.exists(jar_output_path):
        print(f"Arquivo JAR encontrado: {jar_output_path}. Pulando a compilação.")
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

            # Procura qualquer arquivo JAR no diretório build/libs
            jar_files = glob.glob(os.path.join(local_path, 'build', 'libs', '*.jar'))
            if jar_files:
                # Usa o primeiro arquivo JAR encontrado (ou adapte conforme necessário)
                generated_jar_file = jar_files[0]
                os.rename(generated_jar_file, jar_output_path)
                print(f"JAR movido para {jar_output_path}")
            else:
                print(f"Nenhum arquivo JAR encontrado em build/libs para a release: {tag}")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao gerar JAR para a release {tag}: {e}")
            continue

print("Compilação e armazenamento dos arquivos JAR concluídos para as 20 releases.")
