# Microsoft OAuth Setup Instructions

## Setting up Microsoft OAuth 2.0

### 1. Register your application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Fill in the details:
   - **Name**: Your app name (e.g., "Django OAuth Demo")
   - **Supported account types**: Choose based on your needs:
     - "Accounts in this organizational directory only" (Single tenant)
     - "Accounts in any organizational directory" (Multi-tenant)
     - "Accounts in any organizational directory and personal Microsoft accounts" (Multi-tenant + personal)
   - **Redirect URI**: 
     - Platform: Web
     - URI: `http://localhost:8000/auth/complete/microsoft-graph/`

### 2. Configure the application

1. After registration, note down the **Application (client) ID**
2. Go to "Certificates & secrets" > "Client secrets" > "New client secret"
3. Add a description and choose expiration
4. Copy the **Value** (this is your client secret)

### 3. Set API permissions (optional)

1. Go to "API permissions"
2. Add permissions as needed:
   - Microsoft Graph > Delegated permissions
   - Common permissions: `openid`, `email`, `profile`, `User.Read`

### 4. Update your Django settings

Update your `.env` file with the credentials:

```env
# Microsoft OAuth
MICROSOFT_KEY=your-application-client-id-from-azure
MICROSOFT_SECRET=your-client-secret-from-azure
```

### 5. For Azure AD specific setup

If you want to use Azure AD OAuth (enterprise accounts only):

```env
# Azure AD OAuth
AZUREAD_KEY=your-application-client-id-from-azure
AZUREAD_SECRET=your-client-secret-from-azure
AZURE_TENANT_ID=your-tenant-id-or-common
```

## Redirect URIs to configure in Azure:

- Microsoft Graph: `http://localhost:8000/auth/complete/microsoft-graph/`
- Azure AD OAuth2: `http://localhost:8000/auth/complete/azuread-oauth2/`

## Production URLs:

Replace `localhost:8000` with your production domain:
- `https://yourdomain.com/auth/complete/microsoft-graph/`
- `https://yourdomain.com/auth/complete/azuread-oauth2/`

## Scopes Available:

### Microsoft Graph:
- `openid` - Basic authentication
- `email` - Email address
- `profile` - Basic profile information
- `User.Read` - Read user profile

### Azure AD OAuth2:
- `openid` - Basic authentication
- `email` - Email address  
- `profile` - Basic profile information

## Testing:

1. Start your Django development server: `python manage.py runserver`
2. Go to `http://localhost:8000/login/`
3. Click "Continue with Microsoft" or "Continue with Azure AD"
4. You should be redirected to Microsoft login page
5. After successful login, you'll be redirected back to your app
