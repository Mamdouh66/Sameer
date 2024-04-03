# Understanding project structure

```
root-dir/
├── data/
│   └── files.csv
├── Sameer/
│   └── files.py
├── notebooks/
│   └── notebooks.ipynb
├── tets/
│   └── tests.py
├── .gitignore
├── Dockerfile
├── docker-compose.yaml
├── .pre-commit-config.yaml
├── poetry.lock
└── pyproject.toml
```

for the `data` you should download The Movies Dataset from [kaggle](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset/data?select=movies_metadata.csv) and put the files there.
They will not be sent to github because of their size.
the `filmora` directory is the main entry for the package and it will hold the final main logic for the project.
the `notebooks` directory will hold visualization, experiments, what ever we need with notebooks.
the `tests` directory as the name suggests.
the `Dockerfile` has a docker image so you don't say its works on my machine.
the `docker-compose.yaml` its an easier way to deal with docker builds in development
the `.pre-commit-config.yaml` file is important for making sure your commit is not dog water.
the `pyproject.toml` is Poetry `requirements.txt` but better.

## Running the project (local machine)

Firstly create a virtual environment, I use conda for making virtual environments and poetry for packaging and monitoring dependinces. You can do all of that in poetry watch [this](https://www.youtube.com/watch?v=0f3moPe_bhk)

Install poetry

```bash
pip install poetry
```

Install the dependencies

```bash
poetry install
```

## Running the project (Docker image)
Build the docker image

```bash
docker-compose up --build
```
