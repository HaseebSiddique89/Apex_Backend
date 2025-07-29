# React Native Integration Guide for Apex Backend

This guide provides complete integration instructions for connecting your React Native frontend with the Apex Backend.

## 📱 Prerequisites

- React Native project set up
- Backend server running on `http://127.0.0.1:5000`
- All API keys configured in backend `.env`

## 🔧 Setup

### 1. Install Required Dependencies

```bash
npm install axios react-native-document-picker react-native-fs react-native-vector-icons
npm install @react-native-async-storage/async-storage
npm install react-native-3d-model-view  # For AR/3D model viewing
```

### 2. Create API Service

Create `src/services/api.js`:

```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://127.0.0.1:5000'; // Change to your backend URL

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // Authentication
  async signup(email, password) {
    try {
      const response = await this.api.post('/auth/signup', {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyEmail(email, token) {
    try {
      const response = await this.api.post('/auth/verify-email', {
        email,
        token,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(email, password) {
    try {
      const response = await this.api.post('/auth/login', {
        email,
        password,
      });
      
      // Store token
      if (response.data.token) {
        await AsyncStorage.setItem('authToken', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout() {
    await AsyncStorage.removeItem('authToken');
  }

  // Image Processing
  async uploadImage(imageUri) {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'image.jpg',
      });

      const response = await this.api.post('/image/upload-complete', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async check3DStatus(taskId) {
    try {
      const response = await this.api.post('/image/3d/status', {
        task_id: taskId,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUserImages() {
    try {
      const response = await this.api.get('/image/user/images');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      return {
        message: error.response.data.error || 'Request failed',
        status: error.response.status,
      };
    }
    return {
      message: 'Network error',
      status: 0,
    };
  }
}

export default new ApiService();
```

### 3. Create Authentication Context

Create `src/contexts/AuthContext.js`:

```javascript
import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiService from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        // You can add a verify token endpoint to check if token is still valid
        setUser({ token });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password) => {
    try {
      const response = await apiService.signup(email, password);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const verifyEmail = async (email, token) => {
    try {
      const response = await apiService.verifyEmail(email, token);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password);
      setUser({ email, token: response.token });
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signup,
        verifyEmail,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 4. Create Image Processing Service

Create `src/services/imageProcessing.js`:

```javascript
import apiService from './api';

class ImageProcessingService {
  constructor() {
    this.pollingInterval = null;
  }

  async uploadAndProcess(imageUri, onProgress) {
    try {
      onProgress?.('uploading', 'Uploading image...');
      
      const response = await apiService.uploadImage(imageUri);
      
      if (response.success) {
        onProgress?.('processing', 'Processing image...');
        
        const { model3d_task_id } = response.data;
        
        if (model3d_task_id) {
          onProgress?.('waiting', 'Waiting for 3D model...');
          return await this.poll3DModelStatus(model3d_task_id, onProgress);
        }
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  }

  async poll3DModelStatus(taskId, onProgress) {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes with 5-second intervals
      
      const poll = async () => {
        try {
          attempts++;
          
          const response = await apiService.check3DStatus(taskId);
          
          if (response.success) {
            const { status, model3d_files } = response.data;
            
            if (status === 'completed' && model3d_files) {
              onProgress?.('completed', '3D model ready!');
              clearInterval(this.pollingInterval);
              resolve(response);
              return;
            } else if (status === 'failed') {
              onProgress?.('failed', '3D model generation failed');
              clearInterval(this.pollingInterval);
              reject(new Error('3D model generation failed'));
              return;
            }
            
            onProgress?.('waiting', `Processing 3D model... (${attempts}/${maxAttempts})`);
          }
          
          if (attempts >= maxAttempts) {
            onProgress?.('timeout', '3D model generation timed out');
            clearInterval(this.pollingInterval);
            reject(new Error('3D model generation timed out'));
            return;
          }
        } catch (error) {
          onProgress?.('error', 'Error checking 3D status');
          clearInterval(this.pollingInterval);
          reject(error);
        }
      };
      
      // Start polling
      this.pollingInterval = setInterval(poll, 5000); // Poll every 5 seconds
      poll(); // Initial call
    });
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  async getUserImages() {
    try {
      const response = await apiService.getUserImages();
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new ImageProcessingService();
```

### 5. Create Main Screens

#### Login Screen (`src/screens/LoginScreen.js`):

```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      // Navigation will be handled by AuthContext
    } catch (error) {
      Alert.alert('Login Failed', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Apex AR</Text>
      <Text style={styles.subtitle}>Login to your account</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Login</Text>
        )}
      </TouchableOpacity>
      
      <TouchableOpacity
        style={styles.linkButton}
        onPress={() => navigation.navigate('Signup')}
      >
        <Text style={styles.linkText}>Don't have an account? Sign up</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  input: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    alignItems: 'center',
  },
  linkText: {
    color: '#007AFF',
    fontSize: 14,
  },
});

export default LoginScreen;
```

#### Image Upload Screen (`src/screens/UploadScreen.js`):

```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import imageProcessingService from '../services/imageProcessing';

const UploadScreen = ({ navigation }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState('');

  const pickImage = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.images],
      });
      
      setSelectedImage(result[0]);
    } catch (err) {
      if (!DocumentPicker.isCancel(err)) {
        Alert.alert('Error', 'Failed to pick image');
      }
    }
  };

  const uploadImage = async () => {
    if (!selectedImage) {
      Alert.alert('Error', 'Please select an image first');
      return;
    }

    setProcessing(true);
    setProgress('');

    try {
      const result = await imageProcessingService.uploadAndProcess(
        selectedImage.uri,
        (status, message) => {
          setProgress(message);
        }
      );

      Alert.alert(
        'Success!',
        'Image processed successfully. Check your gallery for results.',
        [
          {
            text: 'View Results',
            onPress: () => navigation.navigate('Gallery'),
          },
          {
            text: 'Upload Another',
            onPress: () => {
              setSelectedImage(null);
              setProgress('');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Upload Image</Text>
      
      {selectedImage ? (
        <View style={styles.imageContainer}>
          <Image source={{ uri: selectedImage.uri }} style={styles.image} />
          <Text style={styles.imageName}>{selectedImage.name}</Text>
        </View>
      ) : (
        <TouchableOpacity style={styles.uploadButton} onPress={pickImage}>
          <Text style={styles.uploadButtonText}>Select Image</Text>
        </TouchableOpacity>
      )}
      
      {progress ? (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="small" color="#007AFF" />
          <Text style={styles.progressText}>{progress}</Text>
        </View>
      ) : null}
      
      <TouchableOpacity
        style={[styles.button, !selectedImage && styles.buttonDisabled]}
        onPress={uploadImage}
        disabled={!selectedImage || processing}
      >
        {processing ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Process Image</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  uploadButton: {
    borderWidth: 2,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
    borderRadius: 10,
    padding: 40,
    alignItems: 'center',
    marginBottom: 20,
  },
  uploadButtonText: {
    color: '#007AFF',
    fontSize: 16,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 10,
    marginBottom: 10,
  },
  imageName: {
    fontSize: 14,
    color: '#666',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  progressText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#666',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default UploadScreen;
```

### 6. Update App.js

```javascript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import UploadScreen from './src/screens/UploadScreen';
import GalleryScreen from './src/screens/GalleryScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Stack.Navigator>
      {user ? (
        // Authenticated screens
        <>
          <Stack.Screen name="Upload" component={UploadScreen} />
          <Stack.Screen name="Gallery" component={GalleryScreen} />
        </>
      ) : (
        // Auth screens
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />
        </>
      )}
    </Stack.Navigator>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
};

export default App;
```

## 🔧 Configuration

### 1. Update Backend URL

In `src/services/api.js`, change the `BASE_URL` to match your backend:

```javascript
const BASE_URL = 'http://127.0.0.1:5000'; // For local development
// const BASE_URL = 'https://your-backend-domain.com'; // For production
```

### 2. Network Security (Android)

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<application
  android:usesCleartextTraffic="true"
  ...>
```

### 3. iOS Network Security

Add to `ios/YourApp/Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <true/>
</dict>
```

## 🚀 Testing the Integration

1. **Start your backend server**
2. **Run your React Native app**
3. **Test the authentication flow**
4. **Test image upload and processing**
5. **Check the gallery for results**

## 📱 Key Features

- ✅ **Authentication with JWT**
- ✅ **Image upload with progress**
- ✅ **Real-time 3D model status polling**
- ✅ **Error handling and user feedback**
- ✅ **Gallery view of processed images**
- ✅ **AR-ready 3D model integration**

## 🔍 Troubleshooting

### Common Issues:

1. **Network Error**: Check if backend URL is correct
2. **CORS Error**: Backend should allow requests from your app
3. **Authentication Error**: Check if JWT token is being sent correctly
4. **File Upload Error**: Ensure image format is supported

### Debug Tips:

- Use `console.log` to debug API calls
- Check network tab in React Native debugger
- Verify backend logs for incoming requests

## 📚 Next Steps

1. **Add AR View**: Integrate 3D model viewer
2. **Add Offline Support**: Cache processed images
3. **Add Push Notifications**: Notify when 3D model is ready
4. **Add Image Filters**: Pre-processing options
5. **Add Social Features**: Share processed images

Your React Native app is now ready to integrate with the Apex Backend! 🚀 