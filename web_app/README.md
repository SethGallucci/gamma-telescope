# Streamlit Set-Up

## 1. Databricks Invocations URL
The `DATABRICKS_URL` is the REST API path used to send data to your model.

1. Log in to your **Databricks Workspace**.
2. In the left-hand sidebar, click on **Serving**.
3. Click the **Name** of the specific endpoint you have already deployed.
4. Near the top of the endpoint details page, look for the **URL** field.
5. **Critical Formatting:** Ensure the URL provided in the UI has `/invocations` at the end.
    * **Base URL (from UI):** `https://<workspace-id>.cloud.databricks.com/serving-endpoints/endpoint-name`
    * **Your .env URL:** `https://<workspace-id>.cloud.databricks.com/serving-endpoints/endpoint-name/invocations`

## 2. Databricks Token
The `DATABRICKS_TOKEN` (Personal Access Token) is required to authenticate your Streamlit app's requests.

1. Click your **Username/Email** in the corner of your Databricks workspace.
2. Select **Settings**.
3. Navigate to the **Developer** section in the sidebar.
4. Next to **Access tokens**, click **Manage**.
5. Click **Generate new token**.
6. Enter a comment (e.g., "Streamlit-App-Access") and set an expiration date.
7. In API scope(s), check model-serving.
8. **Copy the token immediately.** It will only be displayed once.

## 3. Environment Configuration
Copy a `.env` file in your Streamlit project root:

Copy the example file to create your local `.env` file:
```bash
cp .env.example .env
```

Fill in your credentials as follows:

```env
DATABRICKS_URL="https://dbc-02468ace-1357.cloud.databricks.com/serving-endpoints/endpoint-name/invocations"
DATABRICKS_TOKEN="dapi0123456789abcdef0123456789abcdef"
```

## 4. Run Streamlit Locally

Using Streamlit run the main file of the web app.

```bash
uv run streamlit run main.py
```

Open the link displayed in your terminal with a web browser to view the app.