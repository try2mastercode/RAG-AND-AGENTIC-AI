import os
from caption_pipeline import generate_image_caption

def caption_folder(folder_path,output_file="captions.txt"):
    """Generate captions for every image in a folder and save them to a text file."""
    results=[]
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg",".jpeg",".png")):
            image_path=os.path.join(folder_path,filename)
            caption=generate_image_caption(image_path)
            results.append(f"{filename}: {caption}")
            print(f"{filename}: {caption}")

    with open(output_file,"w") as f:
        f.write("\n".join(results))
    return results

if __name__=="__main__":
    caption_folder("images")
