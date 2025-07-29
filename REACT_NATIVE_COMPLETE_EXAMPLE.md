# React Native - Complete Upload Example

## 🚀 **New Complete Upload Endpoint**

### **Backend Handles Everything - Frontend Gets Complete Results**

## 📱 **React Native Implementation**

### **1. Complete Upload API**

```javascript
// api/images.js
export const imageAPI = {
  // Upload image and wait for ALL processing to complete
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
};
```

### **2. Simple Upload Screen**

```javascript
// screens/SimpleUploadScreen.js
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Image, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { imageAPI } from '../api/images';

export default function SimpleUploadScreen({ navigation }) {
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
      
      // Show processing message
      Alert.alert(
        'Processing Image', 
        'This will take 2-5 minutes. Please wait...',
        [{ text: 'OK' }]
      );
      
      const result = await imageAPI.uploadImageComplete(selectedImage, token);
      
      if (result.success) {
        Alert.alert('Success', 'Image processing completed!');
        // Navigate to results with ALL data including 3D model
        navigation.navigate('CompleteResults', { 
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
      <Text style={styles.title}>Upload Image</Text>
      <Text style={styles.subtitle}>
        This will process everything and return complete results
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
          <Text style={styles.buttonText}>Process Image (2-5 min)</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}
```

### **3. Complete Results Screen**

```javascript
// screens/CompleteResultsScreen.js
import React from 'react';
import { View, Text, ScrollView, Image, TouchableOpacity } from 'react-native';

export default function CompleteResultsScreen({ route, navigation }) {
  const { imageData } = route.params;

  const openARView = () => {
    if (imageData.model3d_files && imageData.model3d_files.glb) {
      navigation.navigate('ARView', { 
        glbFilePath: imageData.model3d_files.glb,
        modelName: 'Generated 3D Model'
      });
    } else {
      Alert.alert('3D Model Not Available', '3D model generation failed.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Complete Results</Text>
      
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

      {/* 3D Model - Ready for AR! */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>3D Model</Text>
        <Text style={styles.statusText}>
          Status: {imageData.model3d_status}
        </Text>
        
        {imageData.model3d_files && (
          <View style={styles.modelFilesContainer}>
            <Text style={styles.filesTitle}>3D Model Files:</Text>
            <Text style={styles.filePath}>GLB: {imageData.model3d_files.glb}</Text>
            <Text style={styles.filePath}>Image: {imageData.model3d_files.no_background_image}</Text>
            <TouchableOpacity style={styles.arButton} onPress={openARView}>
              <Text style={styles.buttonText}>View in AR</Text>
            </TouchableOpacity>
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

### **✅ Simple Frontend:**
- Single API call
- No polling required
- No status checking
- Complete results in one response

### **✅ Complete Data:**
- All file paths included
- 3D model ready for AR
- No waiting or checking needed

### **✅ Better UX:**
- Clear processing time expectation
- No complex state management
- Simple loading indicator

## 📊 **Comparison**

| Approach | Frontend Complexity | User Experience | API Calls |
|----------|-------------------|-----------------|-----------|
| **Original** | Complex (polling) | Immediate + progressive | Multiple |
| **Complete** | Simple (single call) | Wait + complete | One |

## 🚀 **Usage**

### **For Simple Apps:**
- Use `/image/upload-complete`
- Wait for complete results
- Show everything at once

### **For Complex Apps:**
- Use `/image/upload` + polling
- Show progressive results
- Real-time updates

**Choose based on your app's needs!** 🎉 