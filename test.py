import unittest
from unittest.mock import patch, MagicMock
from main import clone_repo, get_commit_history, get_commit_files, build_dependency_graph
from graphviz import Digraph


class TestGitFunctions(unittest.TestCase):

    @patch("subprocess.run")
    def test_clone_repo(self, mock_run):
        # Проверяем вызов subprocess.run для команды клонирования
        mock_run.return_value = MagicMock(returncode=0)
        clone_repo("https://example.com/repo.git", "/tmp/repo")
        mock_run.assert_called_once_with(
            ["git", "clone", "https://example.com/repo.git", "/tmp/repo"], check=True
        )

    @patch("subprocess.run")
    def test_get_commit_history(self, mock_run):
        # Мокируем вывод команды 'git log'
        mock_result = MagicMock(stdout="hash1 Commit 1\nhash2 Commit 2\n", returncode=0)
        mock_run.return_value = mock_result

        repo_path = "/tmp/repo"
        commit_history = get_commit_history(repo_path)

        mock_run.assert_called_once_with(
            ["git", "log", "--pretty=format:%H %s"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(commit_history, ["hash1 Commit 1", "hash2 Commit 2"])

    @patch("subprocess.run")
    def test_get_commit_files(self, mock_run):
        # Мокируем вывод команды 'git show'
        mock_result = MagicMock(stdout="file1.py\nfile2.py\n", returncode=0)
        mock_run.return_value = mock_result

        repo_path = "/tmp/repo"
        commit_hash = "hash1"
        files = get_commit_files(repo_path, commit_hash)

        mock_run.assert_called_once_with(
            ["git", "show", "--name-only", "--pretty=format:", commit_hash],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            text=True
        )
        self.assertEqual(files, ["file1.py", "file2.py"])

    def test_build_dependency_graph(self):
        # Создаем фиктивные данные для коммитов
        commits = [
            "hash1 Commit 1",
            "hash2 Commit 2"
        ]
        repo_path = "/tmp/repo"

        # Мокируем `get_commit_files`
        with patch("main.get_commit_files", side_effect=[["file1.py"], ["file2.py"]]):
            graph = build_dependency_graph(commits, repo_path)

            # Проверяем структуру графа
            self.assertIsInstance(graph, Digraph)
            self.assertEqual(len(graph.body), 5)  # 2 узла + 1 связь + аттрибуты графа
            self.assertIn('hash1', graph.source)
            self.assertIn('hash2', graph.source)
            self.assertIn('file1.py', graph.source)
            self.assertIn('file2.py', graph.source)


if __name__ == "__main__":
    unittest.main()
