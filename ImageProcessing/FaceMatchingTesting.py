import os
import base64
import requests
import time
import argparse
import subprocess

def encode_image_to_base64(image_path):
    """Converts an image file to a base64-encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_post_request(url, img1_path, img2_path, uid):
    """Sends a POST request with base64-encoded images to the given URL."""
    # Convert images to base64
    img1_base64 = encode_image_to_base64(img1_path)
    img2_base64 = encode_image_to_base64(img2_path)

    # Create the payload
    payload = {
        'img1': img1_base64,
        'img2': img2_base64,
        'uid': uid
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    return response.json()

def show_image(image_path):
    """Display the image using 'feh'."""
    subprocess.run(['feh', image_path])

def main(persont):
    """Main function to run the image comparison."""
    print('Start')
    person = ['chippy', 'shaganan', 'jana']
    
    if persont < 0 or persont >= len(person):
        print("Invalid persont index. Exiting.")
        return

    knownImagePath = f"./TestImages/{person[persont]}.jpg"
    unknownImageDir = "./TestImages"
    uid = person[persont]  # Example UID; replace with the actual UID

    url = 'https://pleasing-javelin-absolutely.ngrok-free.app/FaceCompareBase64'

    # Iterate over each image in the directory and compare
    for filename in os.listdir(unknownImageDir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            unknownImagePath = os.path.join(unknownImageDir, filename)
            # show_image(unknownImagePath)
            # Send the POST request and print the results
            start_time = time.time()
            out = send_post_request(url, knownImagePath, unknownImagePath, uid)
            end_time = time.time()
            duration = end_time - start_time
            print(f"Duration: {duration:.4f} seconds - {knownImagePath} vs {filename} = {out['status']}")
            # Wait for user input before moving to the next image
            # time.sleep(0.5)
            print()

    print('End')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image comparison script")
    parser.add_argument('persont', type=int, help="Index of the person to compare")
    args = parser.parse_args()

    main(args.persont)
