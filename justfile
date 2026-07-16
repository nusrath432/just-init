# List available commands
default:
    @just --list


# Generate a project one level above the current directory by default.
init language project_name output_dir=".." author="" email="" github_username="":
    uv run just-init init {{quote(language)}} {{quote(project_name)}} --output-dir {{quote(output_dir)}} --author {{quote(author)}} --email {{quote(email)}} --github-username {{quote(github_username)}}
