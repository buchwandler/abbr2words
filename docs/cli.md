# Command line interface

The package provides both `python -m abbr2words` and the installed `abbr2words`
command.

Pass text as the optional positional argument:

```console
abbr2words --lang de "Prof. Klein kommt ggf."
```

If positional text is omitted, the command reads all input from standard input:

```console
printf 'Prof. Klein kommt ggf.' | abbr2words --lang de
```

Options:

- `--lang CODE` selects a language or locale; the default is `en`.
- `--no-context` disables contextual disambiguation.
- `--languages` prints every supported canonical base and explicit locale key and exits.

Invalid language or input values are reported as parser errors and return a
nonzero exit status. Successful expansion prints one line to standard output.
