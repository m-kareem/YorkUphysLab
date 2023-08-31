import os
import csv

def write_data_to_csv(data, path, filename):
    header = ['Position', 'Weight']
    
    # Create the full path for the CSV file on the desktop
    file_path = os.path.join(path, filename)
    
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