# My First Bank App - Frontend

React Native mobile application for managing virtual bank accounts for children.

## Features

- **Authentication**: Secure login and registration for parents
- **Child Management**: View and manage child profiles
- **Account Overview**: See checking and savings account balances
- **Deposits**: Make virtual money deposits with validation
- **Transaction History**: View transaction history with infinite scroll
- **Modern UI**: Beautiful, responsive design with Material Design

## Tech Stack

- **Framework**: React Native with Expo
- **Language**: TypeScript
- **Navigation**: React Navigation v6
- **State Management**: React Context API
- **Forms**: React Hook Form with Yup validation
- **UI Components**: React Native Paper
- **HTTP Client**: Axios
- **Storage**: Expo SecureStore for JWT tokens

## Prerequisites

- Node.js 16+
- npm or yarn
- Expo CLI (`npm install -g @expo/cli`)
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

This will open the Expo development tools in your browser.

### 3. Run on Device/Simulator

- **iOS**: Press `i` in the terminal or click "Run on iOS simulator"
- **Android**: Press `a` in the terminal or click "Run on Android device/emulator"
- **Web**: Press `w` in the terminal or click "Run in web browser"

## Project Structure

```
src/
├── components/          # Reusable UI components
├── contexts/           # React Context providers
├── screens/            # Screen components
├── services/           # API and external services
├── types/              # TypeScript type definitions
└── utils/              # Utility functions
```

## Key Components

### Screens

- **LoginScreen**: Parent authentication
- **RegisterScreen**: New parent registration
- **DashboardScreen**: Overview of children and accounts
- **ChildProfileScreen**: Detailed child profile view
- **AccountScreen**: Account details and transaction history
- **DepositScreen**: Make virtual money deposits

### Contexts

- **AuthContext**: Manages authentication state and user sessions
- **ThemeContext**: Provides consistent theming across the app

### Services

- **apiService**: Handles all API communication with the backend
- **SecureStore**: Manages JWT token storage securely

## API Integration

The frontend communicates with the FastAPI backend through the `apiService`. Key endpoints:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/children/` - List children
- `POST /api/v1/children/` - Create child profile
- `POST /api/v1/accounts/{id}/deposit` - Make deposit
- `GET /api/v1/accounts/{id}/transactions` - Get transaction history

## State Management

The app uses React Context API for global state management:

- **Authentication State**: User login status, JWT tokens
- **Theme State**: Consistent styling and colors
- **Navigation State**: Screen navigation and routing

## Form Validation

All forms use React Hook Form with Yup validation schemas:

- **Login Form**: Email and password validation
- **Registration Form**: Email, password, and confirmation validation
- **Deposit Form**: Amount validation with min/max limits

## Styling

The app uses a consistent design system with:

- **Color Palette**: Primary, secondary, and semantic colors
- **Typography**: Consistent font sizes and weights
- **Spacing**: Standardized spacing scale
- **Components**: Material Design-inspired UI components

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Type checking
npm run type-check
```

## Building for Production

### Expo Build

```bash
# Build for iOS
expo build:ios

# Build for Android
expo build:android
```

### EAS Build (Recommended)

```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Configure EAS
eas build:configure

# Build for production
eas build --platform all
```

## Environment Configuration

Create a `.env` file in the frontend directory:

```env
API_BASE_URL=http://localhost:8000/api/v1
```

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `expo start -c`
2. **Dependencies conflicts**: Delete `node_modules` and reinstall
3. **iOS build issues**: Ensure Xcode is up to date
4. **Android build issues**: Check Android SDK and build tools

### Development Tips

- Use Expo Go app for quick testing on physical devices
- Enable hot reloading for faster development
- Use React Native Debugger for debugging
- Check Expo documentation for platform-specific features

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Test on both iOS and Android
4. Update documentation for new features

## License

This project is part of the My First Bank App MVP.
