from pathlib import Path

from pydantic import BaseModel


class Doc(BaseModel):
    doc_sub_dir: Path = Path('docs/docs')
    auto_doc_path: Path = Path('docs/docs').parent / 'modules'

    # FIXME: Read the mkdocs_config (move to file_helpers)
    # > mkdocs_config = read_yaml_file(self.path_project / MKDOCS_CONFIG)
    # > path_out: Path = Path(mkdocs_config.get('site_dir', 'releases/site'))
    path_out: Path = Path('releases/site')

    # TODO: Make sure that releases/ and docs/ are consistently referenced


class DG(BaseModel):
    doc: Doc = Doc()


dg = DG()
