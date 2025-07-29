# React Native Integration Guide

## 🚀 **Optimized Backend API for React Native**

### **Base URL:** `http://your-backend-url:5000`

---

## 📱 **React Native Implementation**

### **1. Authentication Flow**

```javascript
// api/auth.js
const API_BASE_URL = 'http://your-backend-url:5000';

export const authAPI = {
  // Signup
  signup: async (username, email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });
    return response.json();
  },

  // Verify Email
  verifyEmail: async (token) => {
    const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });
    return response.json();
  },

  // Login
  login: async (usernameOrEmail, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
    });
    return response.json();
  },
};
```

### **2. Image Processing Flow**

```javascript
// api/images.js
export const imageAPI = {
  // Upload image and get all results
  uploadImage: async (imageFile, token) => {
    const formData = new FormData();
    formData.append('file', {
      uri: imageFile.uri,
      type: 'image/jpeg', // or 'image/png'
      name: 'image.jpg',
    });

    const response = await fetch(`${API_BASE_URL}/image/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      body: formData,
    });
    return response.json();
  },

  // Check 3D model status
  check3DStatus: async (taskId, model3dId, token) => {
    const response = await fetch(`${API_BASE_URL}/image/3d/status`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ task_id: taskId, model3d_id: model3dId }),
    });
    return response.json();
  },

  // Get user's images
  getUserImages: async (token) => {
    const response = await fetch(`${API_BASE_URL}/image/user/images`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.json();
  },
};
```

---

## 📱 **React Native Screens Implementation**

### **1. Authentication Screens**

```javascript
// screens/SignupScreen.js
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import { authAPI } from '../api/auth';

export default function SignupScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignup = async () => {
    try {
      const result = await authAPI.signup(username, email, password);
      if (result.message) {
        Alert.alert('Success', 'Please check your email to verify your account');
        navigation.navigate('Login');
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        style={styles.input}
      />
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        style={styles.input}
      />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
      />
      <TouchableOpacity onPress={handleSignup} style={styles.button}>
        <Text style={styles.buttonText}>Sign Up</Text>
      </TouchableOpacity>
    </View>
  );
}
```

### **2. Image Upload Screen**

```javascript
// screens/ImageUploadScreen.js
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Image, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { imageAPI } from '../api/images';

export default function ImageUploadScreen({ navigation }) {
  const [uploading, setUploading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0]);
    }
  };

  const uploadImage = async () => {
    if (!selectedImage) {
      Alert.alert('Error', 'Please select an image first');
      return;
    }

    setUploading(true);
    try {
      const token = await AsyncStorage.getItem('userToken'); // Get stored token
      const result = await imageAPI.uploadImage(selectedImage, token);
      
      if (result.success) {
        Alert.alert('Success', 'Image processed successfully!');
        // Navigate to results screen with all data
        navigation.navigate('Results', { 
          imageData: result.data,
          model3dTaskId: result.data.model3d_task_id 
        });
      } else {
        Alert.alert('Error', result.message);
      }
    } catch (error) {
      Alert.alert('Error', 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={pickImage} style={styles.pickButton}>
        <Text style={styles.buttonText}>Pick an Image</Text>
      </TouchableOpacity>
      
      {selectedImage && (
        <Image source={{ uri: selectedImage.uri }} style={styles.image} />
      )}
      
      <TouchableOpacity 
        onPress={uploadImage} 
        style={[styles.uploadButton, uploading && styles.disabledButton]}
        disabled={uploading}
      >
        {uploading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Process Image</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}
```

### **3. Results Screen with AR Support**

```javascript
// screens/ResultsScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Image, TouchableOpacity, Alert } from 'react-native';
import { imageAPI } from '../api/images';

export default function ResultsScreen({ route, navigation }) {
  const { imageData, model3dTaskId } = route.params;
  const [model3dStatus, setModel3dStatus] = useState('pending');
  const [model3dFiles, setModel3dFiles] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  // Poll for 3D model status every 5 seconds
  useEffect(() => {
    if (model3dTaskId && !isPolling) {
      setIsPolling(true);
      
      const checkStatus = async () => {
        try {
          const token = await AsyncStorage.getItem('userToken');
          const result = await imageAPI.check3DStatus(model3dTaskId, imageData.model3d_id, token);
          
          if (result.success) {
            setModel3dStatus(result.data.status);
            
            // If 3D model is completed, save the file paths
            if (result.data.status === 'completed' && result.data.model3d_files) {
              setModel3dFiles(result.data.model3d_files);
              setIsPolling(false); // Stop polling
              console.log('🎉 3D Model ready! GLB file:', result.data.model3d_files.glb);
            }
          }
        } catch (error) {
          console.error('Error checking 3D status:', error);
        }
      };

      // Check immediately
      checkStatus();
      
      // Then check every 5 seconds
      const interval = setInterval(checkStatus, 5000);
      
      // Cleanup interval when component unmounts or 3D model is ready
      return () => {
        clearInterval(interval);
        setIsPolling(false);
      };
    }
  }, [model3dTaskId, isPolling]);

  const openARView = () => {
    if (model3dFiles && model3dFiles.glb) {
      // Navigate to AR screen with 3D model path
      navigation.navigate('ARView', { 
        glbFilePath: model3dFiles.glb,
        modelName: 'Generated 3D Model'
      });
    } else {
      Alert.alert(
        '3D Model Not Ready', 
        'The 3D model is still being generated. Please wait a few minutes and try again.',
        [
          { text: 'OK' },
          { text: 'Check Status', onPress: () => {
            // Force a status check
            setIsPolling(false);
          }}
        ]
      );
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Processing Results</Text>
      
      {/* Original Image */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Original Image</Text>
        <Image source={{ uri: `file://${imageData.image_path}` }} style={styles.image} />
      </View>

      {/* Isometric Image */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Isometric View</Text>
        <Image source={{ uri: `file://${imageData.isometric_path}` }} style={styles.image} />
      </View>

      {/* 3D Model Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>3D Model</Text>
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>Status: {model3dStatus}</Text>
          {isPolling && (
            <View style={styles.pollingIndicator}>
              <ActivityIndicator size="small" color="#007AFF" />
              <Text style={styles.pollingText}>Checking status...</Text>
            </View>
          )}
        </View>
        
        {model3dFiles && (
          <View style={styles.modelFilesContainer}>
            <Text style={styles.filesTitle}>3D Model Files:</Text>
            <Text style={styles.filePath}>GLB: {model3dFiles.glb}</Text>
            <Text style={styles.filePath}>Image: {model3dFiles.no_background_image}</Text>
            <TouchableOpacity style={styles.arButton} onPress={openARView}>
              <Text style={styles.buttonText}>View in AR</Text>
            </TouchableOpacity>
          </View>
        )}
        
        {model3dStatus === 'pending' && !model3dFiles && (
          <View style={styles.waitingContainer}>
            <Text style={styles.waitingText}>
              ⏳ 3D model is being generated... This may take 2-5 minutes.
            </Text>
            <Text style={styles.waitingSubtext}>
              You can view other results while waiting.
            </Text>
          </View>
        )}
      </View>

      {/* Explanation */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Explanation</Text>
        <Text style={styles.explanationText}>
          {/* Read and display explanation file content */}
        </Text>
      </View>

      {/* Quiz */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quiz</Text>
        <TouchableOpacity style={styles.button}>
          <Text style={styles.buttonText}>Take Quiz</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  section: {
    marginBottom: 24,
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  image: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 12,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '500',
  },
  pollingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  pollingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  modelFilesContainer: {
    backgroundColor: '#e8f5e8',
    padding: 12,
    borderRadius: 6,
    marginTop: 8,
  },
  filesTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  filePath: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  arButton: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 6,
    marginTop: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  waitingContainer: {
    backgroundColor: '#fff3cd',
    padding: 12,
    borderRadius: 6,
    marginTop: 8,
  },
  waitingText: {
    fontSize: 14,
    color: '#856404',
    textAlign: 'center',
  },
  waitingSubtext: {
    fontSize: 12,
    color: '#856404',
    textAlign: 'center',
    marginTop: 4,
  },
  button: {
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
});
```

### **4. AR View Screen**

```javascript
// screens/ARViewScreen.js
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ARView } from 'react-native-arkit'; // or your preferred AR library

export default function ARViewScreen({ route }) {
  const { glbFilePath, modelName } = route.params;

  return (
    <View style={styles.container}>
      <ARView
        style={styles.arView}
        modelPath={glbFilePath}
        modelName={modelName}
        enablePlaneDetection={true}
        enableLightEstimation={true}
        onARKitError={(error) => console.error('AR Error:', error)}
        onModelLoaded={() => console.log('3D Model loaded successfully')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  arView: {
    flex: 1,
  },
});
```

---

## 🔄 **Complete 3D Model Workflow**

### **Step-by-Step Process:**

1. **User Uploads Image** → Get immediate response with pending 3D status
2. **Show Other Results** → Display isometric, explanation, quiz immediately
3. **Start Polling** → Check 3D status every 5 seconds
4. **Show Progress** → Display "generating..." with loading indicator
5. **3D Model Ready** → Update UI with GLB file path
6. **Enable AR Button** → User can now view in AR

### **Timeline:**
```
Upload → Immediate Response → Poll Status → 3D Ready → AR View
   ↓           ↓                ↓           ↓         ↓
2-3 sec     Pending         Every 5s   2-5 min    GLB File
```

### **User Experience:**
- ✅ **Immediate feedback** - User sees results right away
- ✅ **Progressive disclosure** - 3D model appears when ready
- ✅ **Clear status** - User knows what's happening
- ✅ **No blocking** - Can interact with other results while waiting

---

## 📱 **Complete App Flow**

### **1. User Journey:**
1. **Signup** → Enter username, email, password
2. **Verify Email** → Click link in email
3. **Login** → Enter credentials, get JWT token
4. **Upload Image** → Pick image from gallery/camera
5. **Processing** → Show loading screen
6. **Results** → Display all generated content
7. **3D Model** → Poll for completion status
8. **AR View** → Load .glb file in AR
9. **Quiz** → Take interactive quiz

### **2. Data Flow:**
```
User Upload → Backend Processing → All Results → Frontend Display → AR View
     ↓              ↓                    ↓              ↓              ↓
   Image      Isometric + 3D +      JSON Data    React Native    AR Scene
   File       Explanation + Quiz     Response     UI Components   with .glb
```

### **3. Error Handling:**
- Network errors → Retry mechanism
- Processing failures → Partial results
- Token expiration → Re-login
- File upload errors → User feedback
- AR loading errors → Fallback to 3D viewer

---

## 📦 **Required React Native Packages**

```bash
npm install expo-image-picker
npm install @react-native-async-storage/async-storage
npm install react-native-fs
npm install react-native-vector-icons
npm install react-native-arkit  # or expo-gl, expo-three, etc.
npm install expo-gl
npm install expo-three
```

---

## 🎯 **Key Benefits of This Architecture:**

✅ **Single Upload Call** → Get all results at once  
✅ **Automatic Processing** → No manual steps  
✅ **Real-time 3D Status** → Poll for completion  
✅ **AR Integration** → Direct .glb file loading  
✅ **Clean API Responses** → Only necessary data  
✅ **Error Handling** → Graceful failures  
✅ **Scalable** → Easy to add new features  

**Your React Native app can now upload an image, get everything processed, and view the 3D model in AR!** 🚀