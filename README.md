## Cabinet Nominations Repo

This is a repository for code related to corpus analysis of nomination hearings for 
US cabinet members. 

To support this research, I've begun building my own wrapper for the Congress API (v3)
to expedite the process of ingesting and processing the queried data.

## Getting Started 

Register for an API key through their [official portal](https://api.congress.gov/sign-up/). You will
need this to run the API client.


### uv
To run this project in your own local environment, `uv` is required. This is easily done:

```bash
pip install uv
```

### Installing Dependencies

Once `uv` is installed, these commands will set it up in the working directory of your choice

```bash
cd my_fun_dir
git clone https://github.com/jer164/nom-research.git ### initalize repo
uv sync ### sets up the venv 
```

## Using the Congress API

To start using the Congress API, instatiate a client:

```python
### initalize with your API key
client = CongressV3Client(api_key=api_key)

### call one of the packaged endpoints

noms = client.hearing.get_hearings_by_congress(117, limit=10) # returns a list of Nominations
noms[0].citation
>>> 'PN1204'
```