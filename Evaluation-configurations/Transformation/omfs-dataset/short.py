import os
import csv


def shorten_csv_files(input_folder, output_folder, lines_to_keep=10000):
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            with open(input_file_path, mode='r', errors="ignore") as infile:
                reader = csv.reader(infile)
                lines = [next(reader) for _ in range(lines_to_keep)]

                with open(output_file_path, mode='w', errors="ignore") as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows(lines)

    print(f"Processed files are saved to {output_folder}")


# Example usage:
input_folder = 'data_long'
output_folder = 'data'
shorten_csv_files(input_folder, output_folder)
