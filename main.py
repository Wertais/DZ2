import os
import sys
import subprocess
import tempfile
from graphviz import Digraph


def clone_repo(repo_url, temp_dir):
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)

def get_commit_history(repo_path):
    result = subprocess.run(["git", "log", "--pretty=format:%H %s"], cwd=repo_path, stdout=subprocess.PIPE, text=True)
    return result.stdout.splitlines()

def get_commit_files(repo_path, commit_hash):
    result = subprocess.run(["git", "show", "--name-only", "--pretty=format:", commit_hash], cwd=repo_path, stdout=subprocess.PIPE, text=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def build_dependency_graph(commits, repo_path):
    graph = Digraph(format="png")
    graph.attr(rankdir="LR")

    for i, commit in enumerate(commits):
        commit_hash, commit_msg = commit.split(maxsplit=1)
        files = get_commit_files(repo_path, commit_hash)
        node_label = f"{commit_hash[:7]}\n{commit_msg}\nFiles:\n" + "\n".join(files)
        graph.node(commit_hash, label=node_label, shape="box")

        if i > 0:
            prev_commit_hash = commits[i - 1].split(maxsplit=1)[0]
            graph.edge(prev_commit_hash, commit_hash)

    return graph

def main():
    if len(sys.argv) != 2:
        print("Ввод в консоль: python main.py <git-repo-url>")
        sys.exit(1)

    repo_url = sys.argv[1]

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            print("Клонирование репозитория...")
            clone_repo(repo_url, temp_dir)

            print("Fetching истории коммистов")
            commits = get_commit_history(temp_dir)

            print("Билд графа")
            graph = build_dependency_graph(commits, temp_dir)

            output_file = "Граф зависимостей.png"
            graph.render(output_file, cleanup=True)

            print(f"Граф сохранен {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()