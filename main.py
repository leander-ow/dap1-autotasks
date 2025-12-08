import sys
import os
import re
import subprocess
from markdownify import markdownify as md
from dotenv import load_dotenv
from moodle import *
from getpass import getpass
from bs4 import BeautifulSoup, Comment

# Helper functions

def extract_text(html):
    """
    Converts HTML content into Markdown.
    """
    soup = BeautifulSoup(html, "html.parser")

    for div in soup.find_all(id=re.compile(r"^assign_files_tree")):
        div.decompose()

    markdown = md(str(soup)).strip()

    return markdown

def extract_code_frame(html):
    """
    Extracts the C++ code frame from <pre><code>.
    Returns None if none exists.
    """
    soup = BeautifulSoup(html, "html.parser")
    code = soup.find("pre")
    if code:
        return code.get_text()
    return None

def git_pull(repo_path="."):
    """Executes git pull"""
    subprocess.run(["git", "-C", repo_path, "pull"], check=True)

def git_add(repo_path="."):
    """Executes git add ."""
    subprocess.run(["git", "-C", repo_path, "add", "."], check=True)

def git_commit(repo_path=".", message="Update"):
    """Executes git commit -m <message>"""
    subprocess.run(["git", "-C", repo_path, "commit", "-m", message], check=True)

def git_push(repo_path=".", branch="main"):
    """Executes git push origin <branch>"""
    subprocess.run(["git", "-C", repo_path, "push", "origin", branch], check=True)

os.chdir(os.path.dirname(__file__))

load_dotenv()
user = os.getenv("SSO_USER") or input("Username: ")
password = os.getenv("SSO_PASS") or getpass("Password: ")
course_id = os.getenv("COURSE_ID") or "54815"
repo = os.getenv("REPO") or "dap1"
base = os.getenv("BASE") or "Programmieraufgaben"
base_path = repo + "/" + base
no_git = os.getenv("NO_GIT") or False

m = Moodle()

# moodle login
print("Logging in...")
m.login(user, password)
print("Done")

# show courses
if 'courses' in sys.argv:
    courses = m.load_courses(course_limit=10)
    for course in courses:
        print(f"Course: {course['fullname']}")
        print(f"ID: {course['id']}")
    print("Logging out...")
    m.close()
    print("Done")
    sys.exit(1)

# git pull
if not no_git: git_pull(repo)

assignment_links = m.extract_assignment_links(course_id)

for assignment_link in assignment_links:
    title = assignment_link["title"]

    # Extract task X.Y
    match = re.search(r'Programmieraufgabe\s+(\d+)\.(\d+)', title)
    if not match:
        print("Could not extract task:", title)
        continue

    week, number = match.groups()
    week = f"{int(week):02d}"
    week_folder = os.path.join(base_path, week)
    os.makedirs(week_folder, exist_ok=True)

    cpp_path = os.path.join(week_folder, f"{number}.cpp")
    md_path  = os.path.join(week_folder, f"{number}.md")

    cpp_exists = os.path.exists(cpp_path)
    md_exists  = os.path.exists(md_path)

    subdir = os.path.join(week_folder, number)
    subdir_exists = os.path.isdir(subdir)

    if (cpp_exists and md_exists) or subdir_exists:
        print(f"✓ {week}.{number}: exists")
        continue

    # get html
    html, code_files = m.extract_assignment_content(assignment_link["url"])
    text = extract_text(html)
    code_frame = extract_code_frame(html)

    if code_files:
        # Case A: Code from files
        subdir = os.path.join(week_folder, number)
        os.makedirs(subdir, exist_ok=True)

        print(f"→ write files for {week}.{number} into subfolder {subdir}")

        # markdown
        md_target = os.path.join(subdir, f"Aufgabenstellung.md")
        if not os.path.exists(md_target):
            print("   write:", md_target)
            with open(md_target, "w", encoding="utf-8") as f:
                f.write(text)

        # cpp / hpp
        for filename, content in code_files.items():
            clean_filename = filename.split("?")[0]
            file_path = os.path.join(subdir, clean_filename)
            print("   write:", file_path)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    else:
        # Case B: Code from html
        print(f"→ write files for {week}.{number} ...")

        # markdown
        if not md_exists:
            print("   write:", md_path)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(text)

        # cpp
        if not cpp_exists:
            print("   write:", cpp_path)
            with open(cpp_path, "w", encoding="utf-8") as f:
                if code_frame:
                    f.write(code_frame)
                else:
                    f.write("// TODO\n")
            
    # git workflow
    try:
        commit_msg = f"Programmieraufgabe {week}.{number}: init"
        if not no_git:
            git_add(repo)
            git_commit(repo, commit_msg)
            git_push(repo)
            print(f"✓ pushed {week}.{number} to GitHub")
        else:
            print(f"[SKIP GIT] Would have committed {commit_msg}")
    except subprocess.CalledProcessError as e:
        print("Git operation failed:", e)
        break

print("Logging out...")
m.close()
print("Done")
