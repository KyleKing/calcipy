# TODO: Replace MockLogger with more Generic Intercept Logger

- [ ] [Create new `dev/log_intercept.py` file](https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/)
- [ ] [See loguru-specific notes](https://github.com/Delgan/loguru/issues/59)

## OTHER

```sh
Might be useful?
poetry run symilar --ignore-comments --ignore-docstrings --ignore-imports ...files..
```

```sh
https://pylint.pycqa.org/en/latest/
poetry run pylint calcipy (lots of false positives for line length, but some useful capitalization checks)
```

```sh
poetry run wily --help
poetry run wily build calcipy
poetry run wily report calcipy
poetry run wily graph calcipy
```

## Readability

[textstat](https://pypi.org/project/textstat)

```py
import texstat
import pandas as pd

records = []
for path_md in DG.doc.paths_md:
    text = path_md.read_text()
    records.append(
        'path': path_md.as_posix(),
        'flesch_reading_ease': textstat.flesch_reading_ease(text),  # 0-122 with higher being easier
        'smog_index': textstat.smog_index(text),  # Grade level - requires at least 30 sentences
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),  # Grade level
        'coleman_liau_index': textstat.coleman_liau_index(text),  # Grade level
        'automated_readability_index': textstat.automated_readability_index(text),  # Grade level
        'dale_chall_readability_score': textstat.dale_chall_readability_score(text),  # lookup for 3K most common words
        'difficult_words': textstat.difficult_words(text),  # Verbose?
        'linsear_write_formula': textstat.linsear_write_formula(text),  # Grade level
        'gunning_fog': textstat.gunning_fog(text),  # Grade level
        'text_standard': textstat.text_standard(text, float_output=True),  # Summary statistic?
    )
df_text = pd.DataFrame(records)
breakpoint()
```
