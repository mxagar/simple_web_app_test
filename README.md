# Simple Web App

This repository contains a simple web app with a SQLite databse used to test cloud deployment functionalities.

:warning: The app is **for test puposes only**. You should not deploy an app in a container with the database inside, due to many reasons:

- The database is not scalable.
- The changes in the container are ephemeral, i.e., they disappear when the container is removed.
- etc.

However, I use this simple example for deployment tests; i.e., CICD functionalities are run on the repository to deploy it to different cloud providers using different approaches (e.g., as service, container image, etc.).

The app has two functionalities; when run locally, we can access them as follows:

- Web UI: `http://127.0.0.1:5000/`: we can enter text strings to a local database; additionally, the last 5 inserted text strings are shown with their insertion id.
- REST endpoint: `127.0.0.1:5000/text/<id>`: we can get the inserted text string with the passed id.

Note that neither exception handling nor logging are implemented &mdash; on purpose.

![Simple Web App: Insert entries to a DB](./assets/simple_web_app_db.jpg)

![Simple Web App: REAST API call](./assets/simple_web_app_rest.jpg)

## Table of Contents

- [Simple Web App](#simple-web-app)
  - [Table of Contents](#table-of-contents)
  - [App Structure](#app-structure)
  - [Setup and Local Running](#setup-and-local-running)
  - [Cloud Deployments](#cloud-deployments)
    - [Azure Deployment: Web App Service with Github Integration](#azure-deployment-web-app-service-with-github-integration)
      - [Step 0: Create an Azure Account](#step-0-create-an-azure-account)
      - [Step 1: Prepare Your Application](#step-1-prepare-your-application)
      - [Step 2: Create an Azure App Service](#step-2-create-an-azure-app-service)
      - [Step 3: Configure Deployment from GitHub](#step-3-configure-deployment-from-github)
      - [Step 4: Verify Deployment](#step-4-verify-deployment)
      - [Step 5: Tune the Deployment: Adding Tests](#step-5-tune-the-deployment-adding-tests)
      - [Step 6: Handle Deployment](#step-6-handle-deployment)


## App Structure

The application is implemented in [`app.py`](./app.py) and [`models.py`](./models.py); this is the overview of all files:

```
├───assets/                # Pics
├───templates/
│   └───index.html         # Flask web UI
├───Dockerfile
├───app.py                 # Flask app
├───models.py              # SQLAlchemy table
├───requirements.txt       # Dependencies: dev, prod
├───Procfile               # Command to launch the web app
├───README.md
└───test_app.py            # Tests for app.py using pytest
```

## Setup and Local Running

I prepared this simple app to test different cloud deployment and monitoring methods. However, you can/should run it locally, too.

**Option 1: Local run with flask**

```bash
# Environment
python -m venv venv
source venv/bin/activate # venv\Scripts\activate
pip install -r requirements.txt

# Run
flask run

# App
http://127.0.0.1:5000/
# Fill in table with texts

# REST API
127.0.0.1:5000/text/<id> # e.g., 3
# Check that the correct text is returned
```

**Option 2: Docker packaging and running:**

```bash
# Simple build
docker build -t flask-text-app .
# If we have a proxy; note that the --build_arg is optional
docker build --build-arg HTTPS_PROXY=$env:HTTPS_PROXY -t flask-text-app .

# Run
docker run -p 5000:5000 flask-text-app
# If we want to override the value of the HTTP_PROXY, first set the environment variable, then:
docker run -e HTTPS_PROXY=$env:HTTPS_PROXY -p 5000:5000 flask-text-app
# If we want to create a volume instance locally mounted in the contained; that's where the DB is saved by default
docker run -v instance:/app/instance -p 5000:5000 flask-text-app

# Stop
docker ps
docker stop <id_or_name>
```

## Cloud Deployments

### Azure Deployment: Web App Service with Github Integration

This method is equivalent to a PaaS Heroku deployment.

Deploying a web application to Azure App Service directly from a GitHub repository is a convenient method to automate deployments. This approach is ideal for scenarios where your application doesn't require a containerized environment.

Note that Azure App Service's file system is ephemeral. Changes to the SQLite database will be lost whenever the app is restarted or redeployed.

#### Step 0: Create an Azure Account

Account creation: [Build in the cloud with an Azure free account ](https://azure.microsoft.com/en-us/free/search/); maybe we need to add credit card in order to be able to deploy stuff, even though we have no costs.

Also, install the Azure CLI tool, even though it is not necessary for the deployment: [How to install the Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).

#### Step 1: Prepare Your Application

We need a Prepare the [`Procfile`](./Procfile). Procfiles are native to [Heroku](https://www.heroku.com/), however, they can be used by other platforms.

Any [`Procfile`](./Procfile) needs to be set with the correct `app:app` parameter, being `app:app == module_name:flask_app_instance`, e.g.:

```bash
web: gunicorn -w 4 -k gevent -b 0.0.0.0:8000 app:app
```

#### Step 2: Create an Azure App Service

1. **Log into the Azure Portal**: Visit [Azure Portal](https://portal.azure.com/).
2. **Create a Web App**:

   - Go to "Create a resource" > "Web" > "Web App".
   - Fill in the details:
     - **Subscription**: Choose your Azure subscription; e.g., `Azure subscription 1`
     - **Resource Group**: Select an existing resource group or create a new one, e.g., `rg-simple-web-app`.
     - **Name**: Enter a unique name for your web app; e.g., `simple-web-app-db`.
     - **Publish**: Select "Code".
     - **Runtime stack**: Choose the appropriate runtime for your Flask app, e.g., Python 3.9.
     - **Region**: Choose a region near you or your users.
     - **Linux Plan (App Service plan)**: Select an existing plan or create a new one.
     - **Pricing plan**: select one; e.g. `Free F1: 60 minutes/day`
   - Click "Review and create" > "Create".

#### Step 3: Configure Deployment from GitHub

1. **Open your Web App resource** in the Azure Portal.
2. **Go to Deployment Center**:
   - Navigate to the "Deployment Center" in the sidebar.
   - Choose "GitHub" as the source.
3. **Authorize Azure to Access GitHub**:
   - You'll be prompted to authenticate with GitHub and authorize Azure to access your repositories.
4. **Configure the Build Provider and Repository**:
   - For the build provider, select "App Service build service".
   - Choose your GitHub organization (or username), repository, and branch you wish to deploy.
5. **Finish the Setup**:
   - Complete the configuration and click "Save".
   - Azure will start the deployment process, pulling the latest commit from the specified branch.
   - The first deployment might fail because the app service is not created yet, but the next ones should work.

#### Step 4: Verify Deployment

- Once the deployment process is complete, you can navigate to your web app's URL (found in the "Overview" section of your Web App resource in the Azure Portal) to see your running Flask application.
  - Example: [https://simple-web-app-db.azurewebsites.net/](https://simple-web-app-db.azurewebsites.net/).
- **Continuous Deployment: Future pushes to your selected GitHub branch will trigger automatic deployments to your Azure Web App!**

Now, we can open the app from anywhere and use it!

The **Continuous Deployment** is achieved by *Github Actions*; a workflow is automatically generated in [`.github/workflows/main_simple-web-app-db.yml`](.github/workflows/main_simple-web-app-db.yml). That workflow has 2 jobs:

- `build`: it sets a python environment and installs the dependencies; then, all the files are packaged into a ZIP artifact.
- `deploy`: it uncompresses the ZIP artifact and uploads it to Azure after loging in. The login in happens via 3 secrets: **Client ID, Tenant ID and Subscription ID**. **Those secret values are automatically found and set in Github by Azure.**

In the workflow YAML, the secrets are referenced as follows

```yaml
client-id: ${{ secrets.AZUREAPPSERVICE_CLIENTID_XXX }}
tenant-id: ${{ secrets.AZUREAPPSERVICE_TENANTID_XXX }}
subscription-id: ${{ secrets.AZUREAPPSERVICE_SUBSCRIPTIONID_XXX }}
```

The endings `XXX` are automatically set by Azure and they are not related to the values.

Note that the secrets can be accessed via Repository > Settings > Secrets and variables > Actions. **However, they are not visible once set, we can only update them!**.

To check the values of the **Client ID, Tenant ID and Subscription ID**, we can search for them in the Azure Portal:

- Subscriptions > ...
- Tenant ID: Microsoft Entra ID > ...
- Client ID: Microsoft Entra ID > Users > ...

#### Step 5: Tune the Deployment: Adding Tests

We can use the file [`test_app.py`](./test_app.py) to test our app; those tests should be run (with pytest) either during the `build` job or after it and before the `deploy` job.

**Option 1**: We add an additional command to the `build` job:

```yaml
      # ...
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: |
          source venv/bin/activate
          pytest
        # Add this step to run your tests. Make sure 'pytest' is listed in your 'requirements.txt'

      - name: Zip artifact for deployment
        run: zip release.zip ./* -r
        # This step will only be reached if the tests pass
      # ...
```

**Option 2**: We add an additional job after the `build` job and before the `deploy` job:

```yaml
   # ...
   build:
   # ...
   test:
    needs: build
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python version
        uses: actions/setup-python@v1
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt

      - name: Run pytest
        run: |
          source venv/bin/activate
          pytest
   # ...
   deploy:
   #...
```

Note: in orther to push changes in a workflow, the Github Personal Access Token (PAT) needs to have this permission: Account Settings > Developer Settings > Personal access tokens > Select token > check Workflow.

#### Step 6: Handle Deployment

We can Start/Stop/Restart the app in the Azure portal: `rg-simple-web-app` > `simple-web-app-db`: Stop/Restart.

We can also use the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/), after [installing it](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).

A summary of useful commands:

```bash
# Log in
az logout
az login
# Browser is prompted for logging in
# Id info is output: tenantId, etc.

# Get list or resource groups
az group list --output table

# Get list of resources in the resource group rg-simple-web-app
az resource list --resource-group rg-simple-web-app --output table

# Stop the resource simple-web-app-db from resource group rg-simple-web-app
az webapp stop --name simple-web-app-db --resource-group rg-simple-web-app

# Start again the resource simple-web-app-db from resource group rg-simple-web-app
az webapp start --name simple-web-app-db --resource-group rg-simple-web-app
```
