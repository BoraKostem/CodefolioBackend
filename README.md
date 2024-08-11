# Codefolio Backend API Documentation

## Get Users (Public Endpoint)
This endpoint retrieves the given user profile.

- **GET endpoint**: `<ip>/api/profile/public` (Not Secured)
- **Input**: 
  - Get Param `id`: 
    - Example: `<ip>/api/profile/public?id=1`

## Search Users (Public Endpoint)
This endpoint retrieves users based on the given query.

- **GET endpoint**: `<ip>/api/search` (Not Secured)
- **Input**: (Query Parameters)
  - `q` (string): The search query. Defaults to an empty string if not provided.
  - `page` (integer): The page number for pagination. Defaults to 1 if not provided.
  - `offset` (integer): The number of items to return per page. Defaults to 10 if not provided.

## Register User
This endpoint creates a new user account with a unique email.

- **POST endpoint**: `<ip>/api/register`
- **JSON Input**:
  ```json
  {
    "email": "user@example.com",  
    "password": "your_secure_password",   
    "name": "John Doe",   
    "location": "City, Country",  
    "phone": "1234567890",  
    "github_url": "https://github.com/username",  
    "linkedin_url": "https://www.linkedin.com/in/username"
  }
  ```
  *Note: Adding GitHub during registration does not automatically pull repositories. It is recommended to leave the GitHub field null at registration and use the GitHub endpoint to configure the user's GitHub profile.*

## Login
This endpoint logs in the user and returns a Bearer access token for authentication.

- **POST endpoint**: `<ip>/api/login`
- **JSON Input**:
  ```json
  {
    "email": "user@example.com",  
    "password": "your_secure_password"
  }
  ```

## Add GitHub Profile Link
This endpoint saves the given GitHub URL to the user's data and fetches all public repositories of the user.

- **Warning**: Calling this endpoint will remove all previous GitHub information of the user.
- **POST endpoint**: `<ip>/api/profile/github` (Secured)
- **JSON Input**:
  ```json
  {
    "github_url": "https://github.com/username"
  }
  ```

## Get User's GitHub Projects
This endpoint retrieves the saved GitHub projects of the user.

- **GET endpoint**: `<ip>/api/profile/github` (Secured)
- **Input**: –

## Delete User's GitHub Projects
This endpoint accepts a single or list of GitHub project IDs of the user and deletes them from the database.

- **DELETE endpoint**: `<ip>/api/profile/github` (Secured)
- **JSON Input**: (This can be a single ID or a list of IDs in the `project_ids` field)
  ```json
  {
    "project_ids": "44"
  }
  ```

## Change Description of a GitHub Project
This endpoint changes the description of the specified project (normally fetched from the README file of the GitHub project).

- **PATCH endpoint**: `<ip>/api/profile/github` (Secured)
- **JSON Input**:
  ```json
  {
    "project_id": "1",
    "description": "Hello World"
  }
  ```

## Add CV to Profile
This endpoint uploads a CV in PDF format and parses it for the user's skills, about me, projects, languages, education, and experiences, and saves it to the database.

- **Warning**: Calling this endpoint will remove all previous CV information of the user.
- **POST endpoint**: `<ip>/api/profile/cv/upload` (Secured)
- **multipart/form-data Input**:
  - Key: `cv`
  - Value: PDF file

## Change Description of a CV Project or Add a New Language
This endpoint changes the description of the specified project or adds a new language to the project (normally fetched from the CV).

- **PATCH endpoint**: `<ip>/api/profile/cv/project/edit` (Secured)
- **JSON Input**:
  ```json
  {
    "project_id": 13,
    "description": "Hello World",
    "languages": ["Java", "C++"]  // Or a single string
  }
  ```

## Get User's CV Info
This endpoint retrieves the saved CV information of the user.

- **GET endpoint**: `<ip>/api/profile/cv` (Secured)
- **Input**: –

## Delete User's CV Projects
This endpoint deletes the given CV project if just `project_id` is provided. If a `languages` variable is provided with either a string or a list of strings, it will delete the language(s) of the specified project if they exist.

- **DELETE endpoint**: `<ip>/api/profile/cv/project/delete` (Secured)
- **JSON Input**:
  ```json
  {
    "project_id": 16
  }
  ```
  or
  ```json
  {
    "project_id": 16,
    "languages": ["Java", "C++"]
  }
  ```

## Add CV Project
This endpoint adds a new project with the given information.

- **POST endpoint**: `<ip>/api/profile/cv/project/add` (Secured)
- **JSON Input**:
  ```json
  {
    "project_name": "Project Title",
    "description": "Project Description",
    "languages": ["Technology1", "Technology2"]
  }
  ```

## Add or Delete CV Skill
This endpoint allows a user to add or delete a skill in their CV.

- **POST endpoint**: `/api/profile/cv/skill` (Secured)
- **JSON Input**:
  ```json
  {
    "skill": "Skill Name"
  }
  ```

### Responses:
- **200 OK**: Skill added successfully.
- **400 Bad Request**: The 'skill' field is required.
- **401 Unauthorized**: User is not authenticated.
- **500 Internal Server Error**: An error occurred on the server.

- **DELETE endpoint**: `/api/profile/cv/skill` (Secured)
- **JSON Input**:
  ```json
  {
    "skill": "Skill Name"
  }
  ```

### Responses:
- **200 OK**: Skill deleted successfully.
- **400 Bad Request**: The 'skill' field is required.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: Skill not found.
- **500 Internal Server Error**: An error occurred on the server.

## Add or Delete CV Certification
This endpoint allows a user to add or delete a certification in their CV.

- **POST endpoint**: `/api/profile/cv/certification` (Secured)
- **JSON Input**:
  ```json
  {
    "certification_name": "Certification Title",
    "description": "Certification Description",
    "url": "Certification URL",
    "date": "MM/YYYY"
  }
  ```

### Responses:
- **200 OK**: Certification added successfully.
- **400 Bad Request**: The 'certification_name', 'description', 'url', and 'date' fields are required.
- **401 Unauthorized**: User is not authenticated.
- **500 Internal Server Error**: An error occurred on the server.

- **DELETE endpoint**: `/api/profile/cv/certification` (Secured)
- **JSON Input**:
  ```json
  {
    "certification_id": "Certification ID"
  }
  ```

### Responses:
- **200 OK**: Certification deleted successfully.
- **400 Bad Request**: The 'certification_id' field is required.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: Certification not found.
- **500 Internal Server Error**: An error occurred on the server.

## Add or Delete CV Education
This endpoint allows a user to add or delete an education entry in their CV.

- **POST endpoint**: `/api/profile/cv/education` (Secured)
- **JSON Input**:
  ```json
  {
    "degree": "Degree Title",
    "school": "School Name",
    "location": "Location",
    "start_date": "MM/YYYY",
    "end_date": "MM/YYYY"  // Optional
  }
  ```

### Responses:
- **200 OK**: Education added successfully.
- **400 Bad Request**: The 'degree', 'school', 'location', and 'start_date' fields are required. 'end_date' is optional.
- **401 Unauthorized**: User is not authenticated.
- **500 Internal Server Error**: An error occurred on the server.

- **DELETE endpoint**: `/api/profile/cv/education` (Secured)
- **JSON Input**:
  ```json
  {
    "education_id": "Education ID"
  }
  ```

### Responses:
- **200 OK**: Education deleted successfully.
- **400 Bad Request**: The 'education_id' field is required.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: Education not found.
- **500 Internal Server Error**: An error occurred on the server.

## Add or Delete CV Experience
This endpoint allows a user to add or delete an experience entry in their CV.

- **POST endpoint**: `/api/profile/cv/experience` (Secured)
- **JSON Input**:
  ```json
  {
    "company_name": "Company Name",
    "description": "Job Description",
    "position": "

Position",
    "location": "Location",
    "start_date": "MM/YYYY",
    "end_date": "MM/YYYY"  // Optional
  }
  ```

### Responses:
- **200 OK**: Experience added successfully.
- **400 Bad Request**: The 'company_name', 'description', 'position', 'location', and 'start_date' fields are required. 'end_date' is optional.
- **401 Unauthorized**: User is not authenticated.
- **500 Internal Server Error**: An error occurred on the server.

- **DELETE endpoint**: `/api/profile/cv/experience` (Secured)
- **JSON Input**:
  ```json
  {
    "experience_id": "Experience ID"
  }
  ```

### Responses:
- **200 OK**: Experience deleted successfully.
- **400 Bad Request**: The 'experience_id' field is required.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: Experience not found.
- **500 Internal Server Error**: An error occurred on the server.

## Add or Delete CV Language
This endpoint allows a user to add or delete a language in their CV.

- **POST endpoint**: `/api/profile/cv/language` (Secured)
- **JSON Input**:
  ```json
  {
    "language": "Language Name"
  }
  ```

### Responses:
- **200 OK**: Language added successfully.
- **400 Bad Request**: The 'language' field is required.
- **401 Unauthorized**: User is not authenticated.
- **500 Internal Server Error**: An error occurred on the server.

- **DELETE endpoint**: `/api/profile/cv/language` (Secured)
- **JSON Input**:
  ```json
  {
    "language": "Language Name"
  }
  ```

### Responses:
- **200 OK**: Language deleted successfully.
- **400 Bad Request**: The 'language' field is required.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: Language not found.
- **500 Internal Server Error**: An error occurred on the server.

## Get User CV
This endpoint retrieves all data from the user's CV category.

- **GET endpoint**: `/api/profile/cv` (Secured)
- **Input**: –

## Update Profile Photos
This endpoint updates the user's profile photo and/or background photo.

- **POST endpoint**: `<ip>/api/profile/photo` (Secured)
- **Form-data Input**:
  - `profile_photo`: (File) The new profile photo to upload. Must be at least 200x200 pixels.
  - `background_photo`: (File) The new background photo to upload. Must be at least 1920x1080 pixels.
  
  *Note: At least one of `profile_photo` or `background_photo` must be provided. The uploaded photo URL will be accessible from the user's information via `/api/whoami`.*

---

# Chat API Documentation

This API allows users to interact with a chat service by creating or retrieving chat sessions based on a unique identifier (UUID).

## Create or Continue Chat Session (Public Endpoint)
This endpoint creates a new chat session or continues an existing one. If a UUID is not provided, a new chat session is created. If a UUID is provided, the existing chat session is used.

- **POST endpoint**: `/api/chat`
- **JSON Input**:
  ```json
  {
    "uuid": "existing-uuid",  // Optional if creating a new chat
    "user_id": "user-id",     // Required if uuid is not provided
    "input": "User's message" // Required
  }
  ```

### Responses:
- **200 OK**: Chat message processed successfully.
  ```json
  {
    "response": "Chatbot's response",
    "uuid": "chat-uuid"
  }
  ```
- **400 Bad Request**: The `user_id` or `uuid` is required when creating a new chat session. The `input` field is required.
- **404 Not Found**: The chat session with the provided UUID was not found.
- **500 Internal Server Error**: An error occurred on the server.

## Get Chat History (Public Endpoint)
This endpoint retrieves the chat history for a session identified by the UUID.

- **GET endpoint**: `/api/chat`
- **Query Parameters**:
  - `uuid` (required): The UUID of the chat session to retrieve.

### Responses:
- **200 OK**: Chat history retrieved successfully.
  ```json
  {
    "chat": [/* array of chat messages */],
    "uuid": "chat-uuid"
  }
  ```
```