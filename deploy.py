import os
import sys

def run_command(cmd):
    print(f"Running: {cmd}")
    status = os.system(cmd)
    if status != 0:
        print(f"Error executing: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting Brenve deployment tasks...")
    
    # Set environment variables for production
    os.environ['ENV'] = 'production'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'brenve_project.settings'
    
    # 1. Run database migrations
    print("\n--- 1. Running Migrations ---")
    run_command("python manage.py migrate")
    
    # 2. Collect static files
    print("\n--- 2. Collecting Static Files ---")
    run_command("python manage.py collectstatic --noinput")
    
    # 3. Seed data and create admin user
    print("\n--- 3. Seeding Database and Creating Admin User ---")
    run_command("python manage.py seed_data --admin")
    
    print("\n✅ Deployment tasks completed successfully.")
    print("Admin User: admin")
    print("Admin Password: Brenve2026#@!")
