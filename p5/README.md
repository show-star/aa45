# DevOps Practical 5: Docker Compose Multi-Container App (Flask + MySQL)

**LYCS DevOps Sem 7, Q5: Docker Compose, multi-container application (30 marks)**

Page: https://github.com/show-star/aa45/tree/main/p5

## Aim

Create a project with a Python (Flask) web app and a MySQL database, write a `docker-compose.yml` with two services (`web` and `db`), run them with `docker compose up -d`, check that the web app connects to the database and displays its data, and show how to scale, view logs and bring everything down with volumes (`docker compose down -v`).

## What this practical is about

- **Docker Compose** starts several containers together from one YAML file, `docker-compose.yml`, with one command.
- A **service** is one part of the app. Here there are two: `web` (Flask) and `db` (MySQL).
- Compose puts both containers on one **network**, so the web app reaches the database just by its service name, `db`.
- A **volume** stores the database's data outside the container, so it survives when the container is removed.
- **depends_on** with a **healthcheck** makes `web` wait until MySQL is ready.

## Files in this folder

```
p5/
├── app.py               Flask web app: reads the students table and shows it
├── requirements.txt     Python libraries: flask, mysql-connector-python
├── Dockerfile           Builds the web image from python:3.12-slim
├── init.sql             Creates the students table and 3 sample rows
├── docker-compose.yml   The two services: web and db
└── README.md            These steps
```

---

## Before you start

1. **Open Docker Desktop** (Windows key, type *Docker Desktop*, Enter) and wait until the bottom left says **Engine running**.
2. **Open PowerShell** (Windows key, type *PowerShell*, Enter). Use PowerShell, **not Command Prompt**: the `@' ... '@` blocks below only work in PowerShell.
3. **Check Docker works:**
   ```powershell
   docker --version
   ```
   If you get **'docker' is not recognized**, see [Error 1](#error-1-docker-is-not-recognized).
4. **Free memory and ports:** stop other labs with `docker compose down` in their folders. If Practical 4's container is still running, that's fine: this practical uses port 8000.

**Where to do this:** one **PowerShell** window for every step, inside the `Desktop\compose-app` folder. **Chrome** for `http://localhost:8000`.

---

## Step 1: Create the project (5 marks)

```powershell
cd $HOME\Desktop
mkdir compose-app
cd compose-app
```

Stay in this folder for every later step. `docker compose` only works in the folder that contains `docker-compose.yml`.

Paste each block below as a whole, then press **Enter**. Each one creates one file with the exact spacing. (You can also download the files from this folder into `compose-app` instead.)

**app.py**

```powershell
@'
from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

@app.route("/")
def home():
    try:
        db = mysql.connector.connect(
            host="db",
            user="root",
            password=os.environ["MYSQL_ROOT_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"]
        )
        cursor = db.cursor()
        cursor.execute("SELECT id, name, course FROM students")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        table_rows = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>" for r in rows)
        return f"""
        <html><body style="font-family:Arial;text-align:center;margin-top:60px">
        <h1>Docker Compose: Flask + MySQL</h1>
        <p style="color:green">Connected to MySQL successfully!</p>
        <table border="1" cellpadding="8" style="margin:auto">
        <tr><th>ID</th><th>Name</th><th>Course</th></tr>
        {table_rows}
        </table>
        </body></html>
        """
    except mysql.connector.Error as e:
        return f"Database connection failed: {e}", 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
'@ | Set-Content -Encoding ascii app.py
```

**requirements.txt**

```powershell
@'
flask
mysql-connector-python
'@ | Set-Content -Encoding ascii requirements.txt
```

**Dockerfile**

```powershell
@'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 80
CMD ["python", "app.py"]
'@ | Set-Content -Encoding ascii Dockerfile
```

**init.sql** (runs automatically the first time MySQL starts)

```powershell
@'
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  course VARCHAR(50)
);
INSERT INTO students (name, course) VALUES
  ('Arvind', 'DevOps'),
  ('Priya', 'Data Science'),
  ('Rahul', 'Cloud Computing');
'@ | Set-Content -Encoding ascii init.sql
```

---

## Step 2: Write docker-compose.yml (12 marks)

```powershell
@'
services:
  web:
    build: .
    ports:
      - "8000:80"
    environment:
      MYSQL_ROOT_PASSWORD: rootpass123
      MYSQL_DATABASE: studentdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass123
      MYSQL_DATABASE: studentdb
    volumes:
      - db_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost -uroot -p$$MYSQL_ROOT_PASSWORD --silent"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

volumes:
  db_data:
'@ | Set-Content -Encoding ascii docker-compose.yml
```

**Check the files:**

```powershell
dir
type docker-compose.yml
docker compose config
```

- `dir` must list **5 files**: `app.py`, `requirements.txt`, `Dockerfile`, `init.sql`, `docker-compose.yml`. **None of them should be 0 bytes.**
- `type docker-compose.yml` must start with `services:`.
- `docker compose config` prints the full configuration with **no error**.

📸 **Screenshot:** `dir` and `type docker-compose.yml`.

### docker-compose.yml explained

| Part | Meaning |
| --- | --- |
| `services:` | The list of containers in the app |
| `web` → `build: .` | Build the web image from the Dockerfile in this folder |
| `ports: "8000:80"` | `localhost:8000` on Windows goes to port 80 inside the web container |
| `environment:` (web) | Gives the app the database password and name |
| `depends_on` → `condition: service_healthy` | Start `web` only after `db` passes its health check |
| `db` → `image: mysql:8.0` | The official MySQL 8.0 image from Docker Hub |
| `MYSQL_ROOT_PASSWORD` | The root password MySQL is created with |
| `MYSQL_DATABASE` | The database MySQL creates on first start (`studentdb`) |
| `db_data:/var/lib/mysql` | Named volume: MySQL's data is kept even if the container is removed |
| `./init.sql:/docker-entrypoint-initdb.d/init.sql` | MySQL runs this script on first start to create the table and rows |
| `healthcheck` | Every 10 s, checks MySQL is answering (`mysqladmin ping`) |
| `$$` | In Compose, `$$` means a literal `$`, so the check reads the variable inside the container |
| `volumes: db_data:` | Declares the named volume |

---

## Step 3: Run it and check both containers (5 marks)

```powershell
docker compose up -d --build
```

The first run downloads Python and MySQL, so it takes a few minutes. Wait for **Started** / **Healthy** lines.

```powershell
docker compose ps
```

Run `docker compose ps` again after about 30 seconds until:

- `db` shows **Up (healthy)**
- `web` shows **Up**, with `0.0.0.0:8000->80/tcp`

📸 **Screenshot:** `docker compose ps` with both containers running. You can also show Docker Desktop's **Containers** tab, which groups them under `compose-app`.

---

## Step 4: Check the web app reads from the database (5 marks)

1. Open **http://localhost:8000** in Chrome. You should see:
   - **Docker Compose: Flask + MySQL**
   - **Connected to MySQL successfully!** in green
   - A table with **Arvind / DevOps**, **Priya / Data Science**, **Rahul / Cloud Computing**
2. Check the same data directly inside MySQL:
   ```powershell
   docker compose exec db mysql -uroot -prootpass123 -e "SELECT * FROM studentdb.students;"
   ```
   (The warning about using a password on the command line is normal.)

📸 **Screenshots:** the page at localhost:8000 (address bar visible) and the `SELECT` output.

---

## Step 5: Scale, logs, and bring down with volumes (3 marks)

**Scale down and back up:**

```powershell
docker compose up -d --scale web=0
docker compose ps
docker compose up -d --scale web=1
docker compose ps
```

`--scale web=0` removes the web container (only `db` is left). `--scale web=1` brings it back. It can't go above 1, because only one container can use port 8000 on Windows.

**View logs:**

```powershell
docker compose logs web
docker compose logs db
```

`web` shows Flask's startup and one line per page visit. `db` shows MySQL starting and running `init.sql`.

**Bring everything down, including the volume:**

```powershell
docker compose down -v
docker compose ps
docker volume ls
```

`down -v` removes both containers, the network **and** the `db_data` volume. `docker compose ps` is now empty, and `docker volume ls` no longer lists `compose-app_db_data`.

📸 **Screenshots:** the scale commands, both logs, and `down -v` with `docker volume ls`.

---

## Errors and fixes

These are the errors that came up while doing this practical, with the exact fix for each.

### Error 1: 'docker' is not recognized

```
docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Why:** Docker Desktop is installed for one user only, so a new PowerShell window doesn't know where `docker.exe` is. A fix done with `$env:Path` in an earlier window only lasts until that window is closed, so it comes back in every new window.

**Fix for this window:**

```powershell
$env:Path += ";$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin"
docker --version
```

**Permanent fix** (run once, then open a new PowerShell window):

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin", "User")
```

If `Test-Path "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe"` says **False**, use `C:\Program Files\Docker\Docker\resources\bin` instead. If both are False, Docker Desktop isn't installed.

### Error 2: empty compose file

```
empty compose file
```

**Why:** `docker compose up` ran before anything was saved in the files. `dir` shows the files with **0** bytes.

**Fix:** run each file's `@' ... '@ | Set-Content ...` block again (Steps 1 and 2), then check with `dir` that no file is 0 bytes.

### Error 3: go-yaml ... mapping values are not allowed in this context

```
go-yaml load error in scanner at L8.C11: mapping values are not allowed in this context
```

**Why:** `docker-compose.yml` contains the wrong content or broken spacing. On this PC the Python code had been pasted into the compose file by mistake: `compose.yaml` and `app.py` were both 974 bytes, and line 8 column 11 was the `:` in `def home():`. Pasting YAML into Notepad can also break its indentation.

**Fix:**

1. Run the **Step 2** block again in PowerShell. It overwrites the file with the correct content and spacing.
2. Check it:
   ```powershell
   type docker-compose.yml
   docker compose config
   ```
   It must start with `services:` (not `from flask`), and `config` must show no error.
3. Run `type app.py` too, to make sure the Python file still has the Python code.

### Error 4: Database connection failed

```
Database connection failed: 2003 (HY000): Can't connect to MySQL server on 'db:3306'
```

**Why:** MySQL takes 20 to 40 seconds to start the first time.

**Fix:** wait 30 seconds, run `docker compose ps` until `db` shows **(healthy)**, then refresh the page.

### Error 5: Table 'studentdb.students' doesn't exist

**Why:** `init.sql` only runs when the volume is empty. An older volume from a previous run was reused, so the table was never created.

**Fix:**

```powershell
docker compose down -v
docker compose up -d --build
```

### Other errors

| Error | Fix |
| --- | --- |
| `error during connect` / `open //./pipe/docker_engine` | Docker Desktop isn't running. Open it and wait for **Engine running** |
| `no configuration file provided: not found` | You're not in the `compose-app` folder. Run `cd $HOME\Desktop\compose-app` |
| `Set-Content` / `@'` is not recognized | You're in Command Prompt. Open **PowerShell** |
| `port is already allocated` (8000) | Another container uses it. Run `docker ps`, then `docker stop <name>` |
| `Container compose-app-db-1 is unhealthy` | MySQL failed to start. Run `docker compose logs db`, then `docker compose down -v` and `docker compose up -d --build` |
| A file is named `Dockerfile.txt` or `.env.txt` | Notepad added `.txt`. Rename it: `ren Dockerfile.txt Dockerfile`, or create files with the PowerShell blocks instead of Notepad |
| `pip install` fails during build | Internet problem. Check the connection (try a phone hotspot) and run `docker compose up -d --build` again |

---

## Viva points

| Question | Answer |
| --- | --- |
| What is Docker Compose? | A tool that defines and runs multi-container apps from one YAML file with one command |
| What is a service? | One container definition in the compose file, such as `web` or `db` |
| How does `web` find `db`? | Compose puts both on one network, and the service name `db` works as a hostname |
| Why use a volume? | Container files are lost when it's removed. A volume keeps the database data |
| What does `depends_on` do? | Starts services in order. With `service_healthy`, it also waits for the health check to pass |
| What is a healthcheck? | A command Docker runs regularly to check the container is working |
| `docker compose up -d --build`? | Builds images if needed, then starts all services in the background |
| `down` vs `down -v`? | `down` removes containers and the network. `-v` also deletes the volumes |
| Why can't `web` scale above 1 here? | Only one container can use host port 8000 |
| Docker vs Docker Compose? | Docker runs one container per command. Compose runs a whole multi-container app from one file |

## Conclusion

We created a Flask web app and a MySQL 8.0 database, defined them as two services in `docker-compose.yml` with a named volume for data and a health check, and started them with `docker compose up -d`. The web app connected to MySQL and displayed the `students` table at `localhost:8000`. We then scaled the web service, viewed the logs of both services, and removed everything, including the volume, with `docker compose down -v`. This shows how Docker Compose runs and manages a multi-container application.
