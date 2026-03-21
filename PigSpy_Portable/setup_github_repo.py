#!/usr/bin/env python3
"""
PigSpy GitHub Repository Setup
Automated script to create and push the project to GitHub
"""

import subprocess
import sys
import webbrowser
from pathlib import Path

def run_command(command):
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_git_installed():
    """Check if git is installed."""
    success, _ = run_command("git --version")
    return success

def check_github_cli():
    """Check if GitHub CLI is installed."""
    success, _ = run_command("gh --version")
    return success

def create_repo_with_github_cli(repo_name):
    """Create a repository using GitHub CLI."""
    print(f"\nAttempting to create repository '{repo_name}' using GitHub CLI...")
    
    success, output = run_command(
        f'gh repo create {repo_name} --public --source=. --remote=origin --push'
    )
    
    if success:
        print(f"✓ Repository created and code pushed successfully!")
        return True, output
    else:
        print("✗ Failed to create repository with GitHub CLI")
        print(output)
        return False, output

def manual_repo_creation(repo_name):
    """Guide user through manual repository creation."""
    print("\n" + "="*60)
    print("MANUAL GITHUB REPOSITORY SETUP")
    print("="*60)
    print(f"\nSince GitHub CLI is not available, follow these steps:\n")
    
    print("1. Go to https://github.com/new")
    print(f"2. Enter Repository name: {repo_name}")
    print("3. Choose 'Public'")
    print("4. Do NOT initialize with README (we have one)")
    print("5. Click 'Create repository'")
    print("\n6. Copy the HTTPS URL shown on the new repository page")
    print("   (it will look like: https://github.com/USERNAME/pigspy.git)")
    
    # Open GitHub in browser
    try:
        print("\nOpening GitHub in your browser...")
        webbrowser.open("https://github.com/new")
    except:
        pass
    
    # Get repo URL from user
    repo_url = input("\nEnter your repository URL: ").strip()
    if not repo_url:
        return False
    
    return push_to_github(repo_url)

def push_to_github(repo_url):
    """Push existing repository to GitHub."""
    print(f"\nConfiguring remote and pushing to: {repo_url}")
    
    # Check if remote already exists
    success, _ = run_command("git remote get-url origin")
    if success:
        print("Remote 'origin' already exists. Updating...")
        success, output = run_command(f"git remote set-url origin {repo_url}")
    else:
        success, output = run_command(f"git remote add origin {repo_url}")
    
    if not success:
        print(f"✗ Failed to configure remote: {output}")
        return False
    
    print("✓ Remote configured")
    
    # Push to GitHub
    print("Pushing code to GitHub (this may take a moment)...")
    success, output = run_command("git push -u origin master")
    
    if success:
        print("✓ Successfully pushed to GitHub!")
        return True
    else:
        print(f"✗ Failed to push: {output}")
        return False

def main():
    print("\n" + "="*60)
    print("PIGSPY GITHUB REPOSITORY SETUP")
    print("="*60)
    
    # Verify we're in the right directory
    if not Path(".git").exists():
        print("✗ Not in a git repository. Run cleanup_for_github.py first.")
        sys.exit(1)
    
    if not check_git_installed():
        print("✗ Git is not installed or not in PATH")
        sys.exit(1)
    
    print("✓ Git installed and repository initialized")
    
    repo_name = "pigspy"
    print(f"\nRepository name: {repo_name}")
    
    # Check for GitHub CLI
    has_github_cli = check_github_cli()
    
    if has_github_cli:
        print("✓ GitHub CLI detected")
        
        # Try to authenticate
        success, output = run_command("gh auth status")
        if success:
            print("✓ GitHub authentication successful")
            success, output = create_repo_with_github_cli(repo_name)
            if success:
                print(f"\n✓ Setup complete! Your project is now on GitHub.")
                return
        else:
            print("! GitHub CLI found but not authenticated")
            print("  You can authenticate with: gh auth login")
    
    # Fall back to manual setup
    if not manual_repo_creation(repo_name):
        print("\n✗ Setup failed. Please check your repository URL.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print(f"\nYour PigSpy project is now on GitHub as '{repo_name}'")
    print("\nNext steps:")
    print("1. Visit your repository on GitHub")
    print("2. Update the README.md with your GitHub username if needed")
    print("3. Add any additional documentation or configuration files")
    print("\nTo clone your project later:")
    print(f"  git clone https://github.com/YOUR_USERNAME/{repo_name}.git")

if __name__ == "__main__":
    main()
