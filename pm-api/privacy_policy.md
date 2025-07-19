

🛡️ Privacy Policy

Last updated: 2025-07-18

1. Overview

This Agile Project Management API is designed with privacy and transparency as core principles. It provides secure, stateless interactions except where explicitly storing user-managed project data. All operations are protected by API key authentication, and user data is never shared or used for model training.


---

2. What We Collect

We collect only project-related data that users explicitly submit. Specifically:

Stored:

Project metadata (ID, title, deadlines, fields)

Updates to projects


Not Stored:

Prompts, chat logs, or natural language inputs

Session metadata, IP addresses, or cookies




---

3. Data Access and Control

Every API request requires a secure API token (X-API-Key).

Users may retrieve, update, or delete their own projects via the documented endpoints.

All project data is stored locally in a SQLite database, accessible through:

GET /api/dataset: full SQLite file

GET /api/dataset/raw: base64 JSON blob




---

4. Data Retention

Project data is retained only until a user deletes it or resets the dataset.

There is no automatic retention of inference logs or prompt histories.

Deleted data is permanently erased from the SQLite backend and cannot be recovered.



---

5. Third-Party Sharing

No data is shared with:

Advertising platforms

Analytics services

Cloud vendors or external APIs


All computation and persistence is handled locally within the server environment.


---

6. Legal Compliance

This API meets or exceeds standards for:

GDPR (EU)

CCPA (California)

LGPD (Brazil)

PIPEDA (Canada)


User-controlled data storage, deletion rights, and zero prompt retention ensure full compliance.


---

7. Contact

Questions about your data rights or this policy?
📧 @iurbinah 

