#!/usr/bin/env python3
"""
PigSpy GitHub Push Script
This script helps push the cleaned PigSpy project to GitHub.
"""

import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors."""
    try:
        print(f"Running: {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    print("PigSpy GitHub Push Helper")
    print("=" * 30)

    # Check if git repo is initialized
    if not run_command("git status", "Checking git status"):
        print("Git repository not initialized. Run cleanup_for_github.py first.")
        return

    # Get GitHub repo URL from user
    repo_url = input("Enter your GitHub repository URL (e.g., https://github.com/username/pigspy.git): ").strip()
    if not repo_url:
        print("No URL provided. Exiting.")
        return

    # Add remote
    if not run_command(f"git remote add origin {repo_url}", f"Adding remote origin: {repo_url}"):
        print("Failed to add remote. It might already exist. Trying to set-url...")
        run_command(f"git remote set-url origin {repo_url}", f"Setting remote origin: {repo_url}")

    # Push to GitHub
    if run_command("git push -u origin master", "Pushing to GitHub"):
        print("\nSuccess! Your PigSpy project is now on GitHub.")
        print(f"Repository URL: {repo_url}")
    else:
        print("\nPush failed. You may need to:")
        print("1. Create the repository on GitHub first")
        print("2. Make sure you have push permissions")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()