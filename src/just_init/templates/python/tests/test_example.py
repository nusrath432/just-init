import my_project


def test_package_is_importable() -> None:
    assert my_project.__doc__ == "My Project package."
