import os
import subprocess


def create_diff():
    diff_command = ["git", "diff", "tags/6.4.0"]
    diff_output = subprocess.run(
        diff_command,
        capture_output=True,
        text=True,
        cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), "fhir.resources"),
    )
    diff_result = diff_output.stdout

    patch_file_path = "fhir.resources.patch"
    with open(patch_file_path, "w") as patch_file:
        patch_file.write(diff_result)
    return diff_result


if __name__ == "__main__":
    create_diff()
