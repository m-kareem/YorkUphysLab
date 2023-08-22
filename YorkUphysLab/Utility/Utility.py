import os
import csv

def write_data_to_csv(data, filename):
    header = ['Position', 'Weight']
    
    # Get the user's desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive - York University", "Desktop")
    
    # Create the full path for the CSV file on the desktop
    file_path = os.path.join(desktop_path, filename)
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)
            
            for position, weight in data:
                csv_writer.writerow([position, weight])
        print(f"Data written to '{file_path}' successfully!")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False