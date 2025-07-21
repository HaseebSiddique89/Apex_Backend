# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://haseebsiddique825:Apex%2389@mycluster.ujqwmto.mongodb.net/"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

############################################################################

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
import os
from PIL import Image # For creating a dummy image
from bson.objectid import ObjectId # To work with GridFS file IDs

# --- 1. MongoDB Connection Details ---
# IMPORTANT: Replace <db_password> with your actual database user password
uri = "mongodb+srv://haseebsiddique825:Apex%2389@mycluster.ujqwmto.mongodb.net/"
DB_NAME = "Apex_db" # The database where GridFS will operate
IMAGE_FILENAME = "example_image_for_mongodb.jpg" # Name for the dummy image we create
RETRIEVED_FILENAME = "retrieved_example_image.jpg" # Name for the image we retrieve

# --- 2. Function to Create a Dummy Image ---
def create_dummy_image(filename=IMAGE_FILENAME, width=800, height=600, color='red'):
    """Creates a simple JPEG image for testing."""
    if not os.path.exists(filename):
        img = Image.new('RGB', (width, height), color=color)
        img.save(filename, quality=85) # Save as JPEG with good quality
        print(f"Created dummy image: '{filename}' (approx. {os.path.getsize(filename) / (1024*1024):.2f} MB)")
    else:
        print(f"Dummy image '{filename}' already exists.")


# --- 3. Function to Store Image using GridFS ---
def store_image_to_gridfs(client, file_path):
    db = client[DB_NAME]
    fs = GridFS(db)

    try:
        with open(file_path, "rb") as f:
            # fs.put() stores the file and returns its unique ID (ObjectId)
            file_id = fs.put(f, filename=os.path.basename(file_path), contentType="image/jpeg")
            print(f"Image '{os.path.basename(file_path)}' stored successfully in GridFS.")
            print(f"Assigned GridFS File ID: {file_id}")
            return file_id
    except FileNotFoundError:
        print(f"Error: Image file not found at '{file_path}'")
        return None
    except Exception as e:
        print(f"An error occurred while storing the image: {e}")
        return None

# --- 4. Function to Retrieve Image using GridFS ---
def retrieve_image_from_gridfs(client, file_id, output_path):
    db = client[DB_NAME]
    fs = GridFS(db)

    try:
        # Ensure file_id is an ObjectId, especially if passed as a string
        if not isinstance(file_id, ObjectId):
            file_id = ObjectId(file_id)

        # fs.get() retrieves the file content
        grid_out = fs.get(file_id)

        with open(output_path, "wb") as f:
            f.write(grid_out.read())
        print(f"Image successfully retrieved from GridFS and saved as '{output_path}'")
        print(f"Original filename (from GridFS metadata): {grid_out.filename}")
        print(f"Content type (from GridFS metadata): {grid_out.content_type}")
    except Exception as e:
        print(f"Error retrieving image with ID {file_id}: {e}")

# --- Main Execution Block ---
if __name__ == "__main__":
    # Create the dummy image if it doesn't exist
    create_dummy_image()

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        # Ping to confirm connection
        client.admin.command('ping')
        print("\nSuccessfully connected to MongoDB Atlas!")

        # --- Store the image ---
        print("\n--- Attempting to store image... ---")
        stored_image_id = store_image_to_gridfs(client, IMAGE_FILENAME)

        if stored_image_id:
            # --- Retrieve the image ---
            print("\n--- Attempting to retrieve image... ---")
            retrieve_image_from_gridfs(client, stored_image_id, RETRIEVED_FILENAME)
        else:
            print("Image storage failed, cannot proceed with retrieval.")

    except Exception as e:
        print(f"An error occurred during connection or main operations: {e}")
    finally:
        # Close the connection
        client.close()
        print("\nMongoDB connection closed.")