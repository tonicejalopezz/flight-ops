# flight-ops

An end-to-end data pipeline designed to ingest and transform open-source data into structured, business-ready data models for analytics and AI application.

## Overview

Flight-Ops is currently in the early stages of development. The goal of the project is to provide insights into the current state and historical performance of flight operations across the United States.

## Configuration 
This project requires API credentials to request external data sources. Credentials should be added to the .env file in the project root. Refer to .env.example for the required environment variables. 

### [OpenSky Network API](https://opensky-network.org/data/api)
```bash
OPENSKY_CLIENT_ID=your_client_id
OPENSKY_CLIENT_SECRET=your_client_secret
```
