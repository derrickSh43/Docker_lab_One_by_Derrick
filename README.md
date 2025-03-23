# Derrick’s DevOps Lab: Build and Deploy Guide

Welcome to Derrick’s DevOps Lab! This guide walks you through building the project from scratch, setting up your environment, creating a Docker container, testing it locally, and uploading the image to Docker Hub. Follow each step carefully, and don’t rush—take your time to understand what’s happening!

---
![lab1image](https://github.com/user-attachments/assets/03f6e946-f8f4-4db0-8971-dd37a57a56d0)

## Prerequisites

Before you begin, make sure you have these tools installed on your computer:

1. **Docker**  
   - **Windows**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/). Install it, then launch it (look for the Docker icon in your system tray).
   - - **Note**: If you’re on Windows 10 or earlier, you’ll need to install [WSL2 (Windows Subsystem for Linux 2)](https://learn.microsoft.com/en-us/windows/wsl/install) first to run Docker effectively. Follow Microsoft’s official guide for setup.
   - **Mac**: Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/). Install and launch it (check the top menu bar for the Docker icon).  
   - **Linux**: Install Docker using your package manager. For Ubuntu, run:  
     ```bash
     sudo apt install docker.io
     ```

2. **Git**  
   - **Windows**: Download [Git for Windows](https://git-scm.com/download/win). Install it, then use **Git Bash** (a terminal app) for Git commands.  
   - **Mac**: Install Git with Homebrew: `brew install git` (if not already installed).  
   - **Linux**: Install with: `sudo apt install git` (if not already installed).  

3. **Docker Hub Account**  
   - Sign up at [Docker Hub](https://hub.docker.com/signup) to store and share your Docker images later.

---

## Steps to Set Up and Deploy the Lab

### 1. Clone the Repository or Set Up the Files

First, you need the project files on your computer.

1. Open **Git Bash** (Windows) or **Terminal** (Mac/Linux).  
2. Clone the repository using this command (replace `[repo-link]` with the actual GitHub URL):  
   ```bash
   git clone [repo-link]
   ```
3. Move into the project folder:  
   ```bash
   cd my-devops-lab
   ```

Your folder should look like this:  
```
my-devops-lab/
├── Dockerfile
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── static/
│       ├── app.js
│       ├── index.html
│       └── labs.html
├── labs/
│   └── Lab 1/
│       ├── lab1.txt
│       └── validate.sh
```
![image](https://github.com/user-attachments/assets/1bed5e6d-0542-403e-bd83-80470a9fc7b3)

---

### 2. Set Up Your Development Environment

Next, prepare your system to run the project.

1. **Create a Python virtual environment**:  
   - **Windows (Git Bash or CMD)**:  
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```  
   - **Mac/Linux (Terminal)**:  
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```  
   (You’ll see `(venv)` in your terminal when it’s active.)  

2. **Install Python dependencies**:  
   Run this command while in the virtual environment:  
   ```bash
   pip install -r backend/requirements.txt
   ```

---

### 3. Create the Dockerfile

The **Dockerfile** tells Docker how to build your project into a container. Create a file named `Dockerfile` in the `my-devops-lab` folder and add this content:

```dockerfile
# Use slim Python image
FROM python:3.11-slim

# Avoid prompts & install docker client + basic tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl docker.io iputils-ping vim sudo && \
    pip install --no-cache-dir fastapi uvicorn[standard] docker && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/main.py /app/main.py
COPY backend/requirements.txt /app/requirements.txt

# Copy frontend static files
COPY frontend/static /app/static

# Copy labs directory
COPY labs /app/labs

# Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 4. Build the Docker Image

Now, build the Docker image from your project files. In the terminal (inside `my-devops-lab`), run:  
```bash
docker build -t yourusername/lab1-app .
```
Replace `yourusername` with your Docker Hub username.

---

### 5. Run the Docker Container Locally

Test your container on your machine:  

- **Windows(powershell)**:  
  ```bash
  docker run -d -p 8000:8000 -v \\.\pipe\docker_engine:/var/run/docker.sock yourusername/lab1-app
  ```  
- **Mac/Linux(also gitbash)**:  
  ```bash
  docker run -d -p 8000:8000 -v /var/run/docker.sock:/var/run/docker.sock yourusername/lab1-app
  ```

This starts the app on port 8000 in the background (`-d` means detached mode).

---

### 6. Access the Lab in the Browser

Open your browser and go to:  
```
http://localhost:8000/labs.html
```

You’ll see a list of labs (e.g., “Lab 1: Linux Command Line Basics for DevOps”). Click **“Start Lab”** to begin.

---

### 7. Push the Docker Image to Docker Hub

Share your image with the world!

1. **Log into Docker Hub**:  
   ```bash
   docker login
   ```  
   Enter your Docker Hub username and password.  

2. **Tag the image**:  
   ```bash
   docker tag yourusername/lab1-app yourusername/lab1-app:latest
   ```  

3. **Push the image**:  
   ```bash
   docker push yourusername/lab1-app:latest
   ```  

Once uploaded, others can pull your image from Docker Hub.

---

### 8. Troubleshooting

If something goes wrong, try these fixes:

1. **Container Not Running**:  
   Check all containers:  
   ```bash
   docker ps -a
   ```  
   If it says `Exited`, view the logs:  
   ```bash
   docker logs [container-id]
   ```

2. **Port Conflict**:  
   If port 8000 is busy, use a different port (e.g., 8080):  
   ```bash
   docker run -d -p 8080:8000 -v /var/run/docker.sock:/var/run/docker.sock yourusername/lab1-app
   ```  
   Then visit `http://localhost:8080/labs.html`.

3. **Docker Socket Error**:  
   - **Windows**: Ensure Docker Desktop is running.  
   - **Linux**: Add your user to the Docker group:  
     ```bash
     sudo usermod -aG docker $USER
     ```  
     Log out and back in.
