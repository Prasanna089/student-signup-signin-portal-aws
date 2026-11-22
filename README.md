# Student Signup and Signin Portal on AWS

A learning project demonstrating a serverless student signup/signin workflow using Amazon S3, Amazon API Gateway (HTTP API), AWS Lambda (Python), Amazon DynamoDB, IAM and CloudWatch Logs.

## Architecture

Browser → Amazon S3 static website → API Gateway HTTP API → Lambda (`StudentAuthFunction`) → DynamoDB (`Students`)

## AWS configuration used

- Region: `ap-south-2` (Asia Pacific – Hyderabad)
- Lambda function: `StudentAuthFunction`
- Runtime: Python 3.14
- Lambda environment variable: `TABLE_NAME=Students`
- DynamoDB table: `Students`
- Partition key: `email` (String)
- API: `StudentAPI` (HTTP API)
- Routes: `POST /signup` and `POST /signin`
- Stage: `$default` (if configured with auto-deploy)
- API base URL: `https://8nemkn0y0h.execute-api.ap-south-2.amazonaws.com`

## Repository contents

- `backend/lambda_function.py` – Lambda handler for signup and signin.
- `frontend/index.html` – single-file frontend with HTML, CSS and JavaScript.
- `iam/StudentsTableAccess-policy-template.json` – least-privilege DynamoDB policy template.
- `test-events/` – sample Lambda test events.
- `documentation/screenshots/` – place your own redacted AWS screenshots here.

## Deployment outline

1. Create DynamoDB table `Students` with partition key `email` (String).
2. Create Lambda function `StudentAuthFunction` using Python 3.14.
3. Upload the code in `backend/lambda_function.py` to Lambda.
4. Set Lambda environment variable `TABLE_NAME` to `Students`.
5. Set Lambda timeout to at least 15 seconds.
6. Attach `AWSLambdaBasicExecutionRole` and a scoped DynamoDB policy based on the template in `iam/`.
7. Create API Gateway HTTP API `StudentAPI`, integrate the Lambda, and add `POST /signup` and `POST /signin`.
8. Configure API Gateway CORS for your actual website origin; allow `POST` and `OPTIONS`, and `content-type`.
9. Confirm the API invoke URL matches `API_URL` in `frontend/index.html`. Update it if your deployed URL changes.
10. Upload `frontend/index.html` to your S3 bucket and enable static website hosting with `index.html` as the index document.
11. Test signup, signin, duplicate signup and incorrect password handling.

## Lambda test events

Use the JSON files in `test-events/`. Signup should return HTTP 201 for a new email. Signin should return HTTP 200 for the same email/password. Reusing an email should return HTTP 409; incorrect credentials should return HTTP 401.

## Security notes

- Passwords are stored as salted PBKDF2-SHA256 hashes (200,000 rounds), not plain text.
- Never commit AWS access keys, secret keys, passwords, real student information or private environment files.
- Replace `YOUR_12_DIGIT_ACCOUNT_ID` in the IAM policy template only when applying it in your AWS account. Do not publish your account-specific policy if you prefer to keep the account ID private.
- Configure CORS to allow only your actual website origin when possible.
- This is an educational demo, not production authentication. It does not issue signed session tokens. Do not use it to protect real student data.
- S3 static website endpoints use HTTP. For HTTPS, use CloudFront and an appropriate domain.

## Screenshots

Add your own screenshots to `documentation/screenshots/` and link them here after capturing:
- Lambda function overview
- API Gateway routes and stage
- DynamoDB table configuration (no personal data)
- S3 static website hosting
- Signup success
- Signin success

## Author

Prasanna Venkatesh
