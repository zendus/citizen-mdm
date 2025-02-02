# Citizen MDM Service

A Master Data Management (MDM) service that merges and serves citizen data from the Ministry of Health and Ministry of Education. This service provides a unified view of citizen records by combining data from multiple government agencies.

## Features

- Data ingestion from multiple sources (Health and Education ministries)
- Automated conflict resolution for matching records
- RESTful API endpoints for accessing merged data
- Comprehensive logging of data conflicts and resolutions
- In-memory data storage for fast access
- Health check endpoint for monitoring

## Technical Stack

- Python 3.8+
- FastAPI framework
- Pydantic for data validation
- Built-in logging module
- JSON for data storage

## Project Structure

```
citizen-mdm/
├── main.py           # FastAPI application and business logic
├── health.json       # Sample health ministry data
├── education.json    # Sample education ministry data
├── requirements.txt  # Project dependencies
├── mdm.log          # Application logs
└── README.md        # This file
```

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/zendus/citizen-mdm.git
   cd citizen-mdm
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

The server will start at `http://localhost:8000`

## API Documentation

### Endpoints

1. Get Citizen by ID

   ```
   GET /citizens/{citizen_id}
   ```

   Returns merged record for a specific citizen.

   Example Response:

   ```json
   {
     "citizen_id": "A1234",
     "name": "Johnmicheal Uzendu",
     "dob": "1990-05-15",
     "gender": "M",
     "health_status": "Healthy",
     "school_name": "Enugu State University of Science and Technology"
   }
   ```

2. List All Citizens

   ```
   GET /citizens
   ```

   Returns a list of all merged citizen records.

3. Health Check
   ```
   GET /health
   ```
   Returns service health status and timestamp.

### Error Responses

- 404 Not Found: When requesting a non-existent citizen
- 500 Internal Server Error: For server-side errors

## Data Merging Logic

1. Records are matched by `citizen_id`
2. For conflicting fields (name, dob, gender):
   - The most frequent value is chosen
   - Conflicts are logged for auditing
3. For missing values:
   - non-null values are chosen if existing
   - if not, `None` is returned
4. Non-conflicting fields (health_status, school_name) are combined

## Logging

The application logs important events to `mdm.log`, including:

- Data loading events
- Conflict resolutions
- Error conditions

## Testing

Access the interactive API documentation at `http://localhost:8000/docs` to test endpoints.

Example curl commands:

```bash
# Get specific citizen
curl http://localhost:8000/citizens/A1234

# List all citizens
curl http://localhost:8000/citizens

# Health check
curl http://localhost:8000/health
```

## Requirements File

Create a `requirements.txt` with:

```
fastapi>=0.68.0,<0.69.0
uvicorn>=0.15.0,<0.16.0
pydantic>=1.8.0,<2.0.0
```

## Limitations & Future Improvements

1. Current Implementation:

   - In-memory storage (data is lost on service restart)
   - Basic conflict resolution using frequency-based approach
   - Limited to two data sources

2. Potential Enhancements:
   - Persistent storage (database integration)
   - More sophisticated matching algorithms
   - Data validation and cleansing
   - Authentication and authorization
   - Bulk import/export functionality
   - Real-time data updates
   - API rate limiting
   - Caching layer

## Support

For issues and questions, please open a GitHub issue or contact the developer.

## License

MIT License - feel free to use and modify as needed.
