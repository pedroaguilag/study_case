Scripts to process json files containing log requests

This application uses poetry for dependency managenement
`pip install poetry`

Local development:

From the project local folder study_case execute `poetry install` to install all dependencies and create a virtual environment

The application uses a config.yml file to configure the following parameters:

dev:
  requests_file_path: 'path/to/folder/local'
prod:
  requests_file_path: '/app/requests'

Vizualization parameters:

viz:
  start_date: '2020-05-01'
  end_date: '2020-05-20'

Data export parameters:
export:
  start_date: '2020-06-01'
  end_date: '2020-10-01'
  export_file_name: 'requests.csv'


Dockerfile is provide to build an image and deploy and run it on a server


