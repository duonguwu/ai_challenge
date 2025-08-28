#!/usr/bin/env python3
"""
Setup script for the Video Retrieval API
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        os.system(f"cp {env_example} {env_file}")
        print("✅ .env file created. Please review and modify as needed.")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example found, creating basic .env file...")
        with open(env_file, "w") as f:
            f.write("DEBUG=true\n")
            f.write("QDRANT_HOST=localhost\n")
            f.write("QDRANT_PORT=6333\n")


def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")


def check_qdrant():
    """Check if Qdrant is running"""
    try:
        import requests
        response = requests.get("http://localhost:6333/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ Qdrant is running")
            return True
    except:
        pass
    
    print("⚠️  Qdrant is not running. Please start it with: docker-compose up -d qdrant")
    return False


def main():
    """Main setup function"""
    print("🚀 Setting up Video Retrieval API Backend...")
    
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Setup steps
    setup_environment()
    
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    check_qdrant()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Review and modify .env file if needed")
    print("2. Start Qdrant: docker-compose up -d qdrant")
    print("3. Run the API: python run.py")
    print("4. Or run with Docker: docker-compose up backend")
    print("\n📖 API Documentation will be available at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
