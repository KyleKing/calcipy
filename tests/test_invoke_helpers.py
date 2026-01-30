
from calcipy.invoke_helpers import get_doc_subdir


def test_get_doc_subdir_no_copier_answers(tmp_path):
    sub_dir = tmp_path / 'project'
    sub_dir.mkdir()
    (sub_dir / '.git').mkdir()

    result = get_doc_subdir(sub_dir)

    assert result == sub_dir / 'docs' / 'docs'


def test_get_doc_subdir_copier_at_repo_root(tmp_path):
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    (repo_dir / '.git').mkdir()
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: documentation')

    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    result = get_doc_subdir(sub_dir)

    assert result == sub_dir / 'documentation' / 'docs'
