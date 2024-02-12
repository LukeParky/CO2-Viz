## Getting Started

### Requirements

#### Required Software
* [Docker](https://www.docker.com/)

#### Required Credentials
Create API keys for each of these services. You may need to create an account and log in
* [Stats NZ API Key](https://datafinder.stats.govt.nz/my/api/) (For fetching SA1 data)
* [Cesium access token](https://cesium.com/ion/tokens) (API token to retrieve map data from Cesium)

## Starting the services
1. Clone this repository to your local machine.
   
1. Create a file called `.env` in the project root, copy the contents of `.env.template` and fill in all blank fields unless a comment says you can leave it blank.
Blank fields to fill in include things like the `POSTGRES_PASSWORD` variable and `CESIUM_ACCESS_TOKEN`. You may configure other variables as needed.

1. Add the data file as `initialise_db/data/revised_BRANZ_SA1_emissions.xlsx`

1. From project root, run the command `docker-compose up --build -d` to run the database, webservers, and initialisation script.  
   
1. You may inspect the logs of the initialisation script using `docker-compose logs -f initialise_db`

1. Visit http://localhost:{WWW_PORT} to view the site. (values from .env, defaults to 8080)
