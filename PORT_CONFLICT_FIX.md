# Port Conflict Fix for CI/CD Pipeline

## Problem Description

The GitHub CI/CD pipeline was failing with the error:
```
Error: http://localhost:8081 is already used, make sure that nothing is running on the port/url or set reuseExistingServer:true in config.webServer.
```

This occurred because:
1. The CI workflow manually starts the frontend server on port 8081 using `npm run web &`
2. Playwright was also trying to start its own web server on the same port 8081
3. This created a port conflict, causing the tests to fail

## Solution Implemented

### 1. Updated Playwright Configuration (`frontend/playwright.config.ts`)

- **Port Coordination**:
  - CI environment: Uses port 8081 (reuses existing server)
  - Local development: Uses port 8082 (avoids conflicts)
- **Server Reuse**: Set `reuseExistingServer: true` to always reuse existing servers
- **Conditional Commands**: CI environment uses a no-op command since server is already running

### 2. Added New Package Script (`frontend/package.json`)

- Added `web:test` script: `expo start --web --port 8082`
- This allows local testing on port 8082 without conflicts

### 3. Updated CI/CD Workflow (`.github/workflows/ci-cd.yml`)

- Added explicit `export CI=true` to ensure Playwright knows it's in CI mode
- Added clarifying comments about port usage strategy
- Maintained the existing server startup on port 8081

## How It Works Now

### CI Environment
1. CI workflow starts frontend server on port 8081
2. Playwright detects CI environment and reuses the existing server
3. No port conflicts occur

### Local Development
1. Developers can use `npm run web:test` for testing on port 8082
2. Playwright starts its own server on port 8082
3. No conflicts with other development servers

## Benefits

- ✅ **CI Pipeline Fixed**: No more port conflicts in automated testing
- ✅ **Local Development**: Clean separation of ports for different use cases
- ✅ **Maintainable**: Clear configuration that's easy to understand and modify
- ✅ **Flexible**: Supports both CI and local development scenarios

## Testing

To verify the fix works:

1. **Local Testing**: `npm run web:test` (port 8082)
2. **Playwright Tests**: `npx playwright test` (uses port 8082)
3. **CI Pipeline**: Should now pass without port conflicts

## Files Modified

- `frontend/playwright.config.ts` - Main configuration changes
- `frontend/package.json` - Added new script
- `.github/workflows/ci-cd.yml` - CI workflow improvements
- `PORT_CONFLICT_FIX.md` - This documentation file
