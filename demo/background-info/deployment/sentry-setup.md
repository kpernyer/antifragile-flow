# Sentry Crash Reporting Setup with GlitchTip

This guide explains how to set up Sentry crash reporting for both the mobile app and web app, configured to work with your self-hosted GlitchTip instance.

## 🚀 Quick Setup

### 1. Environment Variables

#### Mobile App (Flutter)
Create `apps/mobile/.env` with:
```bash
# Sentry Configuration for GlitchTip
SENTRY_DSN=https://your-glitchtip-instance.com/1
SENTRY_ENVIRONMENT=development
```

#### Web App (React)
Create `apps/admin_web/.env` with:
```bash
# Sentry Configuration for GlitchTip
VITE_SENTRY_DSN=https://your-glitchtip-instance.com/1
VITE_SENTRY_ENVIRONMENT=development
VITE_SENTRY_RELEASE=react-admin@1.0.0
```

### 2. GlitchTip Instance Setup

1. **Deploy GlitchTip** using Docker:
   ```bash
   docker run -d \
     --name glitchtip \
     -p 3000:3000 \
     -e SECRET_KEY=your-secret-key \
     -e DATABASE_URL=postgresql://user:pass@host:5432/glitchtip \
     glitchtip/glitchtip:latest
   ```

2. **Create a project** in GlitchTip UI (http://localhost:3000)

3. **Get the DSN** from your project settings and update the environment variables

## 📱 Mobile App (Flutter)

### Features Implemented

- ✅ **Automatic crash reporting** - Catches all unhandled exceptions
- ✅ **Performance monitoring** - Tracks app performance metrics
- ✅ **User context** - Associates errors with specific users
- ✅ **Organization context** - Tags errors with organization ID
- ✅ **Sensitive data filtering** - Removes passwords, tokens, etc.
- ✅ **Breadcrumbs** - Tracks user actions leading to errors
- ✅ **Custom error capture** - Manual error reporting capabilities

### Usage Examples

```dart
import 'package:flutter_twin/core/error/sentry_config.dart';

// Set user context when user logs in
SentryConfig.setUser(
  id: user.id,
  email: user.email,
  username: user.displayName,
);

// Set organization context
SentryConfig.setOrganization(organization.id);

// Add breadcrumbs for debugging
SentryConfig.addBreadcrumb(
  message: 'User tapped login button',
  category: 'user_action',
);

// Manually capture errors
try {
  await apiCall();
} catch (e, stackTrace) {
  await SentryConfig.captureException(
    e,
    stackTrace: stackTrace,
    extras: {'api_endpoint': '/users'},
    tags: {'feature': 'authentication'},
  );
}

// Capture informational messages
await SentryConfig.captureMessage(
  'User completed onboarding',
  level: SentryLevel.info,
);
```

## 🌐 Web App (React)

### Features Implemented

- ✅ **Error boundaries** - Catches React component errors
- ✅ **Performance monitoring** - Tracks page load times and interactions
- ✅ **User context** - Associates errors with specific users
- ✅ **Organization context** - Tags errors with organization ID
- ✅ **Sensitive data filtering** - Removes passwords, tokens, etc.
- ✅ **Breadcrumbs** - Tracks user actions leading to errors
- ✅ **Custom error capture** - Manual error reporting capabilities

### Usage Examples

```typescript
import {
  setUser,
  setOrganization,
  addBreadcrumb,
  captureException,
  captureMessage
} from '../core/error/sentry';

// Set user context when user logs in
setUser({
  id: user.id,
  email: user.email,
  username: user.displayName,
  organization: user.organization,
});

// Set organization context
setOrganization(organization.id);

// Add breadcrumbs for debugging
addBreadcrumb({
  message: 'User clicked submit button',
  category: 'user_action',
  data: { form: 'login' },
});

// Manually capture errors
try {
  await apiCall();
} catch (error) {
  captureException(error, {
    extras: { api_endpoint: '/users' },
    tags: { feature: 'authentication' },
  });
}

// Capture informational messages
captureMessage('User completed onboarding', 'info');
```

## 🔧 Configuration Options

### Mobile App Configuration

The mobile app Sentry configuration is in `apps/mobile/lib/core/error/sentry_config.dart`:

- **DSN**: Configured via environment variable
- **Environment**: Set to development/staging/production
- **Release**: Set to app version
- **Performance monitoring**: Enabled with 100% sampling
- **Debug mode**: Only enabled in debug builds
- **Sensitive data filtering**: Automatically removes passwords, tokens, etc.

### Web App Configuration

The web app Sentry configuration is in `apps/admin_web/src/core/error/sentry.ts`:

- **DSN**: Configured via environment variable
- **Environment**: Set to development/staging/production
- **Release**: Set to app version
- **Performance monitoring**: Enabled with BrowserTracing
- **Debug mode**: Only enabled in development
- **Sensitive data filtering**: Automatically removes passwords, tokens, etc.

## 🛡️ Security Features

### Data Privacy

Both apps automatically filter out sensitive information:

- **Passwords** - Never sent to Sentry
- **API Keys** - Automatically removed
- **Tokens** - Filtered out from all events
- **Personal Data** - Sanitized before sending

### Environment-Specific Behavior

- **Development**: Limited error reporting to avoid noise
- **Staging**: Full error reporting for testing
- **Production**: Complete error tracking with performance monitoring

## 📊 Monitoring Dashboard

Once configured, you can monitor your apps in GlitchTip:

1. **Error Tracking**: View all crashes and errors
2. **Performance**: Monitor app performance metrics
3. **User Sessions**: Track user journeys and actions
4. **Releases**: Monitor specific app versions
5. **Alerts**: Set up notifications for critical errors

## 🚨 Alerting Setup

Configure alerts in GlitchTip for:

- **High error rates** (>5% error rate)
- **Performance degradation** (>2s page load times)
- **Critical errors** (authentication failures, payment errors)
- **New error types** (unexpected errors)

## 🔄 CI/CD Integration

### Mobile App Build

For production builds, set the environment variables:

```bash
flutter build apk --dart-define=SENTRY_DSN=https://your-glitchtip-instance.com/1 --dart-define=SENTRY_ENVIRONMENT=production
```

### Web App Build

For production builds, set the environment variables:

```bash
VITE_SENTRY_DSN=https://your-glitchtip-instance.com/1 VITE_SENTRY_ENVIRONMENT=production npm run build
```

## 🐛 Troubleshooting

### Common Issues

1. **DSN not found**: Check environment variables are set correctly
2. **No events in GlitchTip**: Verify network connectivity and DSN
3. **Performance issues**: Check sampling rates are appropriate
4. **Missing context**: Ensure user/organization context is set

### Debug Mode

Enable debug mode to see Sentry logs:

- **Mobile**: Set `debug: true` in SentryConfig
- **Web**: Set `debug: true` in Sentry.init()

## 📈 Best Practices

1. **Set user context** immediately after authentication
2. **Add breadcrumbs** for important user actions
3. **Use custom tags** to categorize errors by feature
4. **Monitor performance** regularly
5. **Set up alerts** for critical issues
6. **Review error patterns** weekly
7. **Update release versions** with each deployment

## 🔗 Resources

- [GlitchTip Documentation](https://glitchtip.com/docs/)
- [Sentry Flutter SDK](https://docs.sentry.io/platforms/flutter/)
- [Sentry React SDK](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
