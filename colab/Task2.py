from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt

def complete_image(image_path, axis='vertical'):
   
    img = Image.open('/content/drive/MyDrive/GenSolve/isolated.svg')
    
    img_np = np.array(img)
    
    width, height = img.size
    
    if axis == 'vertical':
        half_img = img_np[:, :width//2]
        mirrored_half = np.fliplr(half_img)
        completed_img_np = np.concatenate((half_img, mirrored_half), axis=1)
    
    elif axis == 'horizontal':
        half_img = img_np[:height//2, :]
        mirrored_half = np.flipud(half_img)
        completed_img_np = np.concatenate((half_img, mirrored_half), axis=0)
    
    else:
        raise ValueError("Axis must be either 'vertical' or 'horizontal'.")
    completed_img = Image.fromarray(completed_img_np)
    
    return completed_img

def plot_images(original_image, completed_image, axis='vertical'):
    """Plot the original and completed images for comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    axes[0].imshow(original_image)
    axes[0].set_title(f"Original Half Image ({axis})")
    axes[0].axis('off')
    
    axes[1].imshow(completed_image)
    axes[1].set_title("Completed Image")
    axes[1].axis('off')
    
    plt.show()
image_path = "/content/crt.jpeg"  

completed_img = complete_image(image_path, axis='vertical')  

original_img = Image.open(image_path)

plot_images(original_img, completed_img, axis='vertical')

completed_img.save("crt.jpeg")