## Table of Contents
1. [Requirements](#requirements)
1. [Quick setup](#quick-setup)
2. [Running tests](#running-tests)
3. [Running the project locally](#running-the-project-locally)

# 1 Requirements
-Docker >27 \
-Python 3.12.4 \
-Pip 22.0 \
-Redis 7.4.0

# 2 Quick setup
build the whole project using docker compose:
```
docker compose -p thumbify -f "compose.api.yaml" up -d --build
docker-compose logs -f
```

get a shell on redis
```
docker compose -f "compose.api.yaml" exec redis redis-cli -h redis -a secret -n 0
```

API documentation available at
```
http://localhost/docs
```

remove build
```
docker compose -p thumbify -f "compose.api.yaml" down
```

# 3 Running tests
### 2.1 create a virtual environment
```
python -m venv .venv
```

### 2.2 activate the virtual environment
```
source .venv/Scripts/activate
```

### 2.3 install dependencies
```
pip install -r requirements.txt
```

### 2.4 run the test suit
```
python -m pytest src/
```


# 4  Running the project locally
add .env file following .env.example

### Check your python version
```
python --version
```

### Create a virtual environment:
```
python -m venv .venv
```

### Get a shell in the created environment:
```
.venv\Scripts\activate
```

### For Windows users using Git Bash terminal:
```
source .venv/Scripts/activate
```

### Install packages:
```
pip install -r requirements.txt
```

### Run the API:
```
python src/main.py
```

### Run the Worker:
```
python worker/main.py
```