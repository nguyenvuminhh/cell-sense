# Design choices

## Project Structure

I considered two main approaches for structuring the project:

**Option 1: Separated by Responsibility**

```
server/
├── routers/
│   ├── chat_router.py
│   ├── user_router.py
│   └── ...
│
├── services/
│   ├── chat_service.py
│   ├── user_service.py
│   └── ...
│
├── models/
│   ├── chat_model.py
│   ├── user_model.py
│   └── ...
│
└── main.py
```

**Option 2: Separated by Module**

```
server/
├── chat_module/
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── config.py
│
├── user_module/
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── config.py
│
└── main.py
```

I chose Option 2 for the following reasons:
- **Modularity**: Each module is self-contained, making it easier to manage and understand.
- **Scalability**: New modules can be added without affecting existing ones.

However, I believe that for a small project like this, Option 1 would work better since there is no need for scalability. Regardless, I opted for Option 2 because I have not personally used it before and wanted to try it out.

## Add-ons Solution: Google Apps Script vs HTTP Endpoint

Details about the comparison can be found in [this video](https://youtu.be/M8bUbcuteio?si=yb8ZvqYZhYEVt1tA).

**Google Apps Script**:
- **Pros**:
  - Seamless integration with Google Sheets.
  - No need for an external server.
  - Easy to deploy and manage within the Google ecosystem.
  - Google handles authoriazation.
- **Cons**:
	- Limited by Google Apps Script quotas and limitations.
	- Debugging can be more challenging.
	- Less flexibility in terms of libraries and tools available.
	- Have to use 3rd party services to edit the script locally and to do version control.
	
**HTTP Endpoint**:
- **Pros**:
  - Full control over the server environment.
  - Can use any language, libraries, or tools needed.
  - Easier to implement complex logic and integrations.
  - Easier to debug and test locally.
- **Cons**:
  - Requires setting up and maintaining a server.
  - More complex integration with Google Sheets.
  - Need to handle authentication and authorization.

## Hosting Platform: Azure vs Google Cloud Platform (GCP)
I am more familiar with Azure, but I chose GCP for the following reasons:
- **Integration with Google Services**: Since the add-on is for Google Sheets, the documentations are written in a way that is more friendly to GCP users.
- **Free Credits**: GCP offers $300 in free credits in 90 days for new users, while Azure offers $200 in free credits in 30 days.