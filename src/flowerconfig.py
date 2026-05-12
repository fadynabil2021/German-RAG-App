import os

# Flower configuration
port = 5555
max_tasks = 10000
auto_refresh = True

# Authentication
flower_user = os.environ.get("FLOWER_USER", "admin")
flower_password = os.environ.get("FLOWER_PASSWORD")

if flower_password:
    basic_auth = [f"{flower_user}:{flower_password}"]
else:
    # If no password is set, we might want to warn or fail, but per PRD we should read from env.
    # In production, this should be mandatory.
    pass
