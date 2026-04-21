import os
import subprocess

def create_structure():
    # Directories to create
    directories = [
        ".github/workflows",
        "docs",
        "backend/apps/authentication",
        "backend/apps/users",
        "backend/apps/inventory",
        "backend/apps/audit",
        "backend/apps/reports",
        "backend/scripts"
    ]

    # Apps following the CSR pattern
    csr_apps = ["equipment", "work_orders"]
    for app in csr_apps:
        directories.extend([
            f"backend/apps/{app}/controllers",
            f"backend/apps/{app}/services",
            f"backend/apps/{app}/repositories",
            f"backend/apps/{app}/tests",
        ])

    for d in directories:
        os.makedirs(d, exist_ok=True)

    # Empty files to touch
    files = [
        "README.md",
        "CLAUDE.md",
        "docker-compose.yml",
        ".github/workflows/backend-ci.yml",
        ".github/workflows/frontend-ci.yml",
        "docs/REQUISITOS_GMAO.pdf",
        "docs/GMAO_Arquitectura_Calidad.pdf",
        "backend/requirements.txt",
        "backend/requirements-dev.txt",
        "backend/.env.example"
    ]

    for app in csr_apps:
        files.extend([
            f"backend/apps/{app}/__init__.py",
            f"backend/apps/{app}/apps.py",
            f"backend/apps/{app}/models.py",
            f"backend/apps/{app}/serializers.py",
            f"backend/apps/{app}/urls.py",
            f"backend/apps/{app}/exceptions.py",
            f"backend/apps/{app}/controllers/__init__.py",
            f"backend/apps/{app}/controllers/{app}_controller.py",
            f"backend/apps/{app}/services/__init__.py",
            f"backend/apps/{app}/services/{app}_service.py",
            f"backend/apps/{app}/repositories/__init__.py",
            f"backend/apps/{app}/repositories/{app}_repository.py",
            f"backend/apps/{app}/tests/test_services.py",
            f"backend/apps/{app}/tests/test_controllers.py",
            f"backend/apps/{app}/tests/test_repositories.py",
        ])

    for f in files:
        with open(f, 'w') as file:
            pass

if __name__ == '__main__':
    create_structure()
    print("Folder and file structure generated.")
