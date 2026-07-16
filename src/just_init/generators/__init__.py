"""Language-specific project generators."""

from just_init.generators.python import PythonProjectGenerator

GENERATORS = {
    PythonProjectGenerator.language: PythonProjectGenerator(),
}
