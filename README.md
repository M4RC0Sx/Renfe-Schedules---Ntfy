# Renfe-Schedules---Ntfy
Set up Renfe schedules notifications on your Ntfy topic.

## Installation and usage:
1. Clone the repository:
    ```bash
    git clone https://github.com/M4RC0Sx/Renfe-Schedules---Ntfy.git
    ```
2. On the root of the project, build the Docker image:
    ```bash
    cd Renfe-Schedules---Ntfy
    docker build -t rsn:1.0.0 .
    ```
3. Create a **.env file** following the exmaple.
4. Create a **config/notifications.json** following the example.
5. Run the Docker image. You can use the **docker-compose.yml** file as an example.
    ```bash
    docker compose up -d
    ```