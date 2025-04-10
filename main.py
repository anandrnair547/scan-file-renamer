import os
import shutil
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Define the folder path
folder_path = "/Users/anandrnair/Downloads/Scans"

# Check if the folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder {folder_path} does not exist!")
    exit(1)

print(f"Folder exists: {folder_path}")


def compress_to_jpeg(booklet_path):
    try:
        # Create compressed directory
        compressed_path = os.path.join(booklet_path, "compressed")
        if not os.path.exists(compressed_path):
            os.makedirs(compressed_path)
            print(f"Created compressed directory at: {compressed_path}")

        # Get all PNG files and sort them
        files = [f for f in os.listdir(booklet_path) if f.endswith(".png")]
        files.sort(key=lambda x: int(x[5:-4]))  # Sort by page number

        # Compress each file
        for file in files:
            src = os.path.join(booklet_path, file)
            dst = os.path.join(compressed_path, file.replace(".png", ".jpg"))

            # Open and compress image
            with Image.open(src) as img:
                # Convert to RGB if necessary (in case of RGBA images)
                if img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                ):
                    img = img.convert("RGB")

                # Save as JPEG with quality=85
                img.save(dst, "JPEG", quality=85)
                print(f"Compressed {file} to JPEG")

    except Exception as e:
        print(f"Error compressing images: {str(e)}")


def create_pdf(booklet_path):
    try:
        # Get compressed directory path
        compressed_path = os.path.join(booklet_path, "compressed")

        # Create PDF path
        pdf_path = os.path.join(booklet_path, "booklet.pdf")

        # Get all JPEG files and sort them
        files = [
            f
            for f in os.listdir(compressed_path)
            if f.endswith(".jpg") or f.endswith(".png")
        ]
        files.sort(key=lambda x: int(x[5:-4]))  # Sort by page number

        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)

        for file in files:
            img_path = os.path.join(compressed_path, file)

            # Get image dimensions
            with Image.open(img_path) as img:
                img_width, img_height = img.size

                # Calculate scaling to fit page
                page_width, page_height = letter
                scale = min(page_width / img_width, page_height / img_height)

                # Calculate position to center image
                x = (page_width - img_width * scale) / 2
                y = (page_height - img_height * scale) / 2

                # Draw image
                c.drawImage(
                    img_path, x, y, width=img_width * scale, height=img_height * scale
                )

                # Add new page
                c.showPage()

                print(f"Added {file} to PDF")

        # Save PDF
        c.save()
        print(f"PDF created at: {pdf_path}")

    except Exception as e:
        print(f"Error creating PDF: {str(e)}")


def extract_number(filename):
    # Extract the number from filenames like "Scan 1.png" or "Scan.png"
    if filename == "Scan.png":
        return 0
    try:
        # Remove "Scan " prefix and ".png" suffix, then convert to int
        return int(filename[5:-4])
    except:
        return float("inf")  # Put invalid filenames at the end


def print_pairings(front_files, back_files):
    print("\nFile pairings:")
    for i in range(max(len(front_files), len(back_files))):
        pair_number = i + 1
        front_file = front_files[i] if i < len(front_files) else "No front file"
        back_file = back_files[-(i + 1)] if i < len(back_files) else "No back file"
        print(f"Pair {pair_number}:")
        print(f"  Front: {front_file} -> {pair_number}.png")
        print(f"  Back:  {back_file} -> {pair_number}b.png")


def process_folder(scan_folder_path):
    try:
        print(f"\nProcessing folder: {scan_folder_path}")

        # Process front folder
        front_path = os.path.join(scan_folder_path, "front")
        print(f"\nChecking front folder: {front_path}")

        front_files = []
        back_files = []

        if os.path.exists(front_path):
            print("Front folder exists")
            front_files = [f for f in os.listdir(front_path) if f.endswith(".png")]
            front_files.sort(key=extract_number)
            print("Front files:", front_files)
        else:
            print("Front folder does not exist")

        # Process back folder
        back_path = os.path.join(scan_folder_path, "back")
        print(f"\nChecking back folder: {back_path}")

        if os.path.exists(back_path):
            print("Back folder exists")
            back_files = [f for f in os.listdir(back_path) if f.endswith(".png")]
            back_files.sort(key=extract_number)
            print("Back files:", back_files)
        else:
            print("Back folder does not exist")

        # Show pairings
        print_pairings(front_files, back_files)

        # Create ordered_files directory
        ordered_files_path = os.path.join(scan_folder_path, "ordered_files")
        if not os.path.exists(ordered_files_path):
            os.makedirs(ordered_files_path)
            print(f"Created ordered_files directory at: {ordered_files_path}")

        # Process and copy files
        print("\nProcessing files:")
        for i in range(max(len(front_files), len(back_files))):
            pair_number = i + 1
            if i < len(front_files):
                front_src = os.path.join(front_path, front_files[i])
                front_dst = os.path.join(ordered_files_path, f"{pair_number}.png")
                shutil.copy2(front_src, front_dst)
                print(f"Copied {front_files[i]} to {pair_number}.png")

            if i < len(back_files):
                back_src = os.path.join(back_path, back_files[-(i + 1)])
                back_dst = os.path.join(ordered_files_path, f"{pair_number}b.png")
                shutil.copy2(back_src, back_dst)
                print(f"Copied {back_files[-(i + 1)]} to {pair_number}b.png")

    except Exception as e:
        print(f"Error processing folder {scan_folder_path}: {str(e)}")


def create_booklet(root_folder):
    try:
        # Create booklet directory
        booklet_path = os.path.join(root_folder, "booklet")
        if not os.path.exists(booklet_path):
            os.makedirs(booklet_path)
            print(f"Created booklet directory at: {booklet_path}")

        # Get all Set folders and sort them
        set_folders = [
            f
            for f in os.listdir(root_folder)
            if os.path.isdir(os.path.join(root_folder, f)) and f.startswith("Set ")
        ]
        set_folders.sort(key=lambda x: int(x[4:]))  # Sort by Set number

        current_page = 1
        for set_folder in set_folders:
            print(f"\nProcessing {set_folder} for booklet")
            ordered_files_path = os.path.join(root_folder, set_folder, "ordered_files")

            if not os.path.exists(ordered_files_path):
                print(f"No ordered_files found in {set_folder}")
                continue

            # Get all files in ordered_files and sort them
            files = [f for f in os.listdir(ordered_files_path) if f.endswith(".png")]
            files.sort(
                key=lambda x: (
                    int(x[:-4]) if not x.endswith("b.png") else int(x[:-5]),
                    x.endswith("b.png"),
                )
            )

            # Copy and rename files
            for file in files:
                src = os.path.join(ordered_files_path, file)
                dst = os.path.join(booklet_path, f"Page {current_page}.png")
                shutil.copy2(src, dst)
                print(f"Copied {file} to Page {current_page}.png")
                current_page += 1

    except Exception as e:
        print(f"Error creating booklet: {str(e)}")


# List items in the root folder
# root_items = os.listdir(folder_path)
# print(f"\nContents of root folder {folder_path}:")
# print(root_items)

# for item in root_items:
#     full_path = os.path.join(folder_path, item)
#     if os.path.isdir(full_path) and item.startswith("Set "):
#         print(f"\nFound Set folder: {item}")
#         process_folder(full_path)
#     else:
#         print(f"Skipping {item} (not a Set folder)")

# Create the booklet after processing all folders
# print("\nCreating booklet...")
# create_booklet(folder_path)

# Compress images to JPEG
# print("\nCompressing images to JPEG...")
booklet_path = os.path.join(folder_path, "booklet")
# compress_to_jpeg(booklet_path)

# Create PDF
print("\nCreating PDF...")
create_pdf(booklet_path)
