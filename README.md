# DevOps Practical 4: Docker Basics

**LYCS DevOps Sem 7, Q4: Docker Basics (30 marks)**

Repository: https://github.com/show-star/aa45

📘 **Viva questions and easy explanations for all 6 practicals:** [VIVA.md](VIVA.md)

| Page | Practical |
| --- | --- |
| This page | **Practical 4:** Docker basics (nginx, `my-web-app:v1`) |
| [p5](p5/README.md) | **Practical 5:** Docker Compose multi-container app (Flask + MySQL) |

## Aim

Pull the `nginx` image from Docker Hub and run it on port 8080, create a simple web page that says "Hello Docker", write a Dockerfile for it using `nginx:alpine`, build the image `my-web-app:v1`, run it on port 8081, and use the basic Docker commands `docker ps`, `docker images`, `docker logs`, `docker stop` and `docker rm`.

## What this practical is about

- **Docker** packages an application together with everything it needs, so it runs the same way on every computer.
- An **image** is a ready-made package, like a template. `nginx` is an image of the nginx web server.
- A **container** is a running copy of an image. One image can run as many containers.
- A **Dockerfile** is a text file with instructions for building your own image.
- **Docker Hub** is the public online store of images. `docker pull` downloads from it.
- **Port mapping** (`-p 8081:80`) connects a port on Windows (8081) to a port inside the container (80), so the browser can reach the web server.

## What's in this repo

```
├── index.html    The web page ("Hello Docker")
├── Dockerfile    Builds the image my-web-app:v1 from nginx:alpine
└── README.md     These steps
```

**index.html**

```html
<!DOCTYPE html>
<html>
<head><title>My Web App</title></head>
<body style="font-family:Arial;text-align:center;margin-top:100px;">
  <h1>Hello Docker</h1>
  <p>Your Name - Your Roll Number</p>
</body>
</html>
```

**Dockerfile**

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
```

| Line | Meaning |
| --- | --- |
| `FROM nginx:alpine` | Start from the small, Alpine Linux based nginx image |
| `COPY index.html /usr/share/nginx/html/index.html` | Put our page in the folder nginx serves web pages from |
| `EXPOSE 80` | The container listens on port 80 |

---

## Before you start

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop (keep **Use WSL 2** ticked), then restart the PC.
2. **Open Docker Desktop:** press the Windows key, type *Docker Desktop* and press Enter. Wait until the bottom left says **Engine running** in green. Keep it open for the whole practical.
3. **Open PowerShell:** press the Windows key, type *PowerShell* and press Enter. The prompt looks like `PS C:\Users\YourName>`.
4. **Check Docker works:**
   ```powershell
   docker --version
   ```
   If you get **'docker' is not recognized**, see [Error 1](#error-1-docker-is-not-recognized) below.

**Where to do this:** all commands run in **PowerShell**. Use **Chrome** to check `http://localhost:8080` and `http://localhost:8081`. Step 1 also needs **PowerShell as Administrator** to stop Jenkins.

---

## Step 1: Pull nginx and run it on port 8080 (6 marks)

Jenkins also uses port 8080, so stop Jenkins first. Open **PowerShell as Administrator** (Windows key, type *PowerShell*, click **Run as administrator**, then **Yes**) and run:

```powershell
net stop jenkins
```

If Jenkins isn't installed, skip that line. Then run:

```powershell
docker pull nginx
docker run -d --name nginx-test -p 8080:80 nginx
```

Open **http://localhost:8080** in Chrome. The **Welcome to nginx!** page appears.

📸 **Screenshot:** `docker pull nginx` output and the nginx welcome page.

Then free port 8080 and start Jenkins again:

```powershell
docker stop nginx-test
net start jenkins
```

---

## Step 2: Create the web app (5 marks)

In a normal **PowerShell** window:

```powershell
cd $HOME\Desktop
mkdir my-web-app
cd my-web-app

@'
<!DOCTYPE html>
<html>
<head><title>My Web App</title></head>
<body style="font-family:Arial;text-align:center;margin-top:100px;">
  <h1>Hello Docker</h1>
  <p>Your Name - Your Roll Number</p>
</body>
</html>
'@ | Set-Content -Encoding ascii index.html
```

You can also download `index.html` from this repo into the `my-web-app` folder instead.

The block starting with `@'` and ending with `'@ | Set-Content ...` creates the file. Paste the whole block at once and press **Enter**. It only works in PowerShell, not Command Prompt.

---

## Step 3: Write the Dockerfile (8 marks)

Stay in the `my-web-app` folder:

```powershell
@'
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
'@ | Set-Content -Encoding ascii Dockerfile

dir
type Dockerfile
```

`dir` should show **Dockerfile** and **index.html**. The name must be exactly `Dockerfile`: capital D, no `.txt`.

📸 **Screenshot:** `type Dockerfile`.

---

## Step 4: Build my-web-app:v1 and run it on port 8081 (6 marks)

```powershell
docker build -t my-web-app:v1 .
```

**Don't forget the dot `.` at the end.** It means "build from this folder".

The build ends with a line like `naming to docker.io/library/my-web-app:v1`.

```powershell
docker run -d --name my-web-container -p 8081:80 my-web-app:v1
docker ps
```

`docker ps` shows `my-web-container` with `0.0.0.0:8081->80/tcp`.

Open **http://localhost:8081** in Chrome. It shows **Hello Docker**.

📸 **Screenshots:** the build output, `docker ps`, and the page at localhost:8081 with the address bar visible.

---

## Step 5: Container management commands (5 marks)

Refresh http://localhost:8081 once (so the log has a line), then run these one by one:

```powershell
docker ps
docker images
docker logs my-web-container
docker stop my-web-container
docker rm my-web-container
docker ps -a
```

| Command | What it does / what you'll see |
| --- | --- |
| `docker ps` | Lists running containers: `my-web-container` with `0.0.0.0:8081->80/tcp` |
| `docker images` | Lists images on the PC: `my-web-app` (tag `v1`) and `nginx` |
| `docker logs my-web-container` | Shows nginx's log, with one `GET /` line per page visit |
| `docker stop my-web-container` | Stops the container (prints its name) |
| `docker rm my-web-container` | Deletes the stopped container (prints its name) |
| `docker ps -a` | Lists all containers, including stopped ones. `my-web-container` is gone |

📸 **Screenshot:** the output of each command.

**Clean up** (optional):

```powershell
docker rm nginx-test
```

---

## Errors and fixes

These are the errors that came up while doing this practical, with the exact fix for each.

### Error 1: 'docker' is not recognized

```
docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Why:** Docker Desktop was installed for one user only, so PowerShell doesn't know where `docker.exe` is. Typing `Docker` with a capital D is not the problem.

**Fix:**

1. Make sure Docker Desktop is installed and open, showing **Engine running**.
2. Close PowerShell and open a new window, then try `docker --version` again.
3. Still not recognized? Find where Docker is:
   ```powershell
   Test-Path "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
   Test-Path "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe"
   ```
4. Whichever line says **True**, add that folder to PATH for this window:
   ```powershell
   # if the second line was True (installed for one user):
   $env:Path += ";$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin"
   # if the first line was True:
   $env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
   docker --version
   ```
5. **Permanent fix** (so every new window works):
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin", "User")
   ```
   Then close PowerShell and open a new one.
6. If both lines say **False**, Docker isn't installed. Install Docker Desktop (see Before you start).

### Error 2: docker build requires 1 argument

```
ERROR: docker: 'docker buildx build' requires 1 argument
```

**Why:** the dot `.` at the end of the build command is missing.

**Fix:**

```powershell
docker build -t my-web-app:v1 .
```

### Error 3: port is already allocated

```
Bind for 0.0.0.0:8081 failed: port is already allocated
```

**Why:** another container is already using port 8081. On this PC it was `schema-registry` from a Kafka setup (it can also be a container from an earlier Jenkins practical).

**Fix:**

1. Find what's using the port:
   ```powershell
   docker ps
   ```
   Look for the row with `0.0.0.0:8081->...` and note the name in the **NAMES** column.
2. Stop that container (stopping doesn't delete it):
   ```powershell
   docker stop schema-registry
   ```
   Use the name you found in step 1 if it's different.
3. Remove the half-created container and run again:
   ```powershell
   docker rm -f my-web-container
   docker run -d --name my-web-container -p 8081:80 my-web-app:v1
   ```
4. When you've finished the practical, start the other container again if you need it:
   ```powershell
   docker start schema-registry
   ```

For port **8080** (Step 1), the usual cause is Jenkins. Run `net stop jenkins` in PowerShell as Administrator.

### Error 4: container name is already in use

```
Conflict. The container name "/my-web-container" is already in use by container "7321e5b1...".
```

**Why:** an earlier `docker run` failed (for example because of Error 3), but Docker still created a container with that name.

**Fix:**

```powershell
docker rm -f my-web-container
docker run -d --name my-web-container -p 8081:80 my-web-app:v1
```

### Other errors

| Error | Fix |
| --- | --- |
| `error during connect` / `open //./pipe/docker_engine` | Docker Desktop isn't running. Open it and wait for **Engine running** |
| `Set-Content` / `@'` is not recognized | You're in Command Prompt. Open **PowerShell** |
| `unable to prepare context: unable to evaluate symlinks in Dockerfile path` | You're not in the `my-web-app` folder, or the file is named `Dockerfile.txt`. Run `cd $HOME\Desktop\my-web-app` and check with `dir` |
| The nginx default page shows instead of "Hello Docker" | `index.html` wasn't in the folder when you built. Check with `dir`, then build again and re-run the container |
| `pull access denied` / `TLS handshake timeout` | Internet problem. Check the connection (try a phone hotspot) and run `docker pull nginx` again |

---

## Viva points

| Question | Answer |
| --- | --- |
| What is Docker? | A platform that packages apps and their dependencies into containers, so they run the same everywhere |
| Image vs container? | An image is the template. A container is a running copy of an image |
| Container vs virtual machine? | A container shares the host's OS kernel, so it's much lighter and starts in seconds. A VM runs a full OS |
| What is a Dockerfile? | A text file with instructions to build an image |
| What is Docker Hub? | The public registry that images like `nginx` are pulled from |
| What does `-d` mean? | Detached: run the container in the background |
| What does `-p 8081:80` mean? | Windows port 8081 forwards to port 80 inside the container |
| What does `--name` do? | Gives the container a fixed name instead of a random one |
| `docker stop` vs `docker rm`? | `stop` stops a running container. `rm` deletes a stopped one |
| `docker ps` vs `docker ps -a`? | `ps` shows running containers. `-a` also shows stopped ones |
| Why `nginx:alpine`? | Alpine is a very small Linux, so the image is small and fast to download |

## Conclusion

We pulled the nginx image from Docker Hub and ran it on port 8080, created a "Hello Docker" web page, wrote a Dockerfile based on `nginx:alpine`, built the image `my-web-app:v1` and ran it on port 8081. We then used `docker ps`, `docker images`, `docker logs`, `docker stop` and `docker rm` to manage the container. This shows how Docker packages and runs applications in containers.
