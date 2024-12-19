<!-- 
### Explanation:

- **Headings (`#` for large titles, `##` for smaller headings):** Markdown headings provide a clear structure.
- **Code blocks (````bash`):** Used for commands that the user should run, such as installing dependencies and running the app.
- **Lists (`-` or `*`):** Used to describe features, prerequisites, installation steps, etc.
- **Links (`[text](url)`):** For referencing external documents or resources, such as a License file or repository.
- **Bold Text (`**text**`):** Used for important terms or labels.

This format follows the common structure of a README file and should be easy to modify for your specific project details. -->

# Care Connect Backend

## Description 

Care Connect is a web app that opens doors for persons with disability.(PWD) We are in a mission to connect PWD's to the best in class resources and assistance. We provide a platform to access donations across the board to make life a litle more easier.

### Technology Stack

- Python
- FastAPI
- Uvicorn Server
- SQLAlchemy

### How To setup

* Fork and clone the project to yout local machine.

* Open the project directory.

* Run the following command to install pipenv to manage your virtual environment.

````pipenv install````

* Run the following command to activate the virtual environment

````pipenv shell````

* Run the following commands to install dependencies

````pipenv fastapi[standard] ````
````pipenv install sqlalchemy````
````pipenv install cors```

Open the project in any IDE of your choice.

### How to run the web app

To be able to run the web app in development you need to run the following command in you terminal.

- Ensure to avtivate your virtual environment first for this command to succeed.

````fastapi dev````

This will open your app in a localhost and access the app using the provided address.
The endpoint that will be provide is the one you will use to make request from the frontend.

 To run the prolect in production run.

 ````fastapi run````

This will open your app in your the production environment.

### Deployement

You can use any cloud platform to deploy the project in this instance the project has been deployed in **Render.com** at [CareConnectBackend](https://phase-3-project-backend.onrender.com/)
