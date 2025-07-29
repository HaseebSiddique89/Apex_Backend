# React Native - Fast Upload with Separate 3D Polling

## 🚀 **New Fast Upload Approach**

### **Quick Response + Separate 3D Model Polling**

## 📱 **React Native Implementation**

### **1. Fast Upload API**

```javascript
// api/images.js
export const imageAPI = {
  // Upload image and get all results except GLB file
  uploadImageComplete: async (imageFile, token) => {
    const formData = new FormData();
    formData.append('file', {
      uri: imageFile.uri,
      type: 'image/jpeg',
      name: 'image.jpg',
    });

    const response = await fetch(`${API_BASE_URL}/image/upload-complete`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      body: formData,
    });
    return response.json();
  },

  // Poll for 3D model status
  check3DStatus: async (taskId, model3dId, token) => {
    const response = await fetch(`${API_BASE_URL}/image/3d/status`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task_id: taskId,
        model3d_id: model3dId
      }),
    });
    return response.json();
  },
};
```

### **2. Fast Upload Screen**

```javascript
// screens/FastUploadScreen.js
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Image, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { imageAPI } from '../api/images';

export default function FastUploadScreen({ navigation }) {
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
      const token = await AsyncStorage.getItem('userToken');
      
      const result = await imageAPI.uploadImageComplete(selectedImage, token);
      
      if (result.success) {
        Alert.alert('Success', 'Image processing completed! 3D model is being generated.');
        
        // Navigate to results with task_id for 3D polling
        navigation.navigate('FastResults', { 
          imageData: result.data
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
      <Text style={styles.title}>Fast Upload</Text>
      <Text style={styles.subtitle}>
        Get all results quickly, then poll for 3D model
      </Text>
      
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
          <View style={styles.loadingContainer}>
            <ActivityIndicator color="white" />
            <Text style={styles.loadingText}>Processing...</Text>
          </View>
        ) : (
          <Text style={styles.buttonText}>Process Image (30-60 sec)</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}
```

### **3. Fast Results Screen with 3D Polling**

```javascript
// screens/FastResultsScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Image, TouchableOpacity, Alert } from 'react-native';
import { imageAPI } from '../api/images';

export default function FastResultsScreen({ route, navigation }) {
  const { imageData } = route.params;
  const [model3dStatus, setModel3dStatus] = useState('pending');
  const [model3dFiles, setModel3dFiles] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  // Poll for 3D model status
  useEffect(() => {
    if (imageData.model3d_task_id && !isPolling) {
      setIsPolling(true);
      
      const checkStatus = async () => {
        try {
          const token = await AsyncStorage.getItem('userToken');
          const result = await imageAPI.check3DStatus(
            imageData.model3d_task_id, 
            imageData.model3d_id, 
            token
          );

          if (result.success) {
            setModel3dStatus(result.data.status);
            
            if (result.data.status === 'completed' && result.data.model3d_files) {
              setModel3dFiles(result.data.model3d_files);
              setIsPolling(false);
              Alert.alert('🎉 3D Model Ready!', 'GLB file is now available for AR view.');
            }
          }
        } catch (error) {
          console.error('Error polling 3D model status:', error);
        }
      };

      // Check immediately
      checkStatus();
      
      // Then check every 10 seconds
      const interval = setInterval(checkStatus, 10000);
      
      return () => {
        clearInterval(interval);
        setIsPolling(false);
      };
    }
  }, [imageData.model3d_task_id, imageData.model3d_id, isPolling]);

  const openARView = () => {
    if (model3dFiles && model3dFiles.glb) {
      navigation.navigate('ARView', { 
        glbFilePath: model3dFiles.glb,
        modelName: 'Generated 3D Model'
      });
    } else {
      Alert.alert('3D Model Not Ready', 'The 3D model is still being generated. Please wait.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Fast Results</Text>
      
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
        <Text style={styles.statusText}>
          Status: {model3dStatus}
        </Text>
        
        {isPolling && (
          <View style={styles.pollingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.pollingText}>Checking 3D model status...</Text>
          </View>
        )}
        
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
```

## 🎯 **Key Benefits**

### **✅ Fast Response:**
- All results in 30-60 seconds
- No waiting for 3D model
- Better user experience

### **✅ Progressive Updates:**
- Show results immediately
- Poll for 3D model separately
- Real-time status updates

### **✅ Better UX:**
- Users can view results while waiting
- Clear status indicators
- No timeout issues

## 📊 **Comparison**

| Approach | Response Time | User Experience | Complexity |
|----------|---------------|-----------------|------------|
| **Wait for Everything** | 2-5 minutes | Wait + complete | Simple |
| **Fast + Polling** | 30-60 seconds | Immediate + progressive | Moderate |

## 🚀 **Usage Flow**

1. **Upload Image** → Get all results in 30-60 seconds
2. **Show Results** → Display isometric, explanation, quiz
3. **Poll 3D Status** → Check every 10 seconds
4. **Get GLB File** → Download when ready
5. **AR View** → Load GLB file in AR

**Perfect for responsive mobile apps!** 🎉 