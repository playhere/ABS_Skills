from PIL import Image
import os

def resize_image(from_path,to_path, new_size=(50, 50)):
    # Create backup filename
    backup_path = from_path.replace('.png', '_bak.png')
    
    if not os.path.exists(from_path):
        print(f"File not found: {from_path}")
        return
    
    # Create backup
    if not os.path.exists(backup_path):
        os.rename(from_path, backup_path)
        print(f"Created backup: {backup_path}")
    else:
        print(f"Backup already exists: {backup_path}")
    
    # Open the backup image
    with Image.open(backup_path) as img:
        print(f"Original size of {os.path.basename(backup_path)}: {img.size}")
        # Resize image
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        # Save the resized image with original name
        resized_img.save(to_path)
        print(f"Resized image saved: {to_path}")
        print(f"New size: {resized_img.size}")

def main():
    # Ensure the images directory exists
    image_dir = "assets/images/src"
    image_dest = "assets/images"
    if not os.path.exists(image_dir):
        print(f"Directory {image_dir} does not exist!")
        return

    # Process each PNG file in the directory
    for filename in os.listdir(image_dir):
        if filename.endswith('.png') and not filename.endswith('_bak.png'):
            from_path = os.path.join(image_dir, filename)
            to_path = os.path.join(image_dest, filename)
            print(f"\nProcessing {filename}...")
            try:
                resize_image(from_path,to_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main() 