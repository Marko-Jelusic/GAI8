import os
import shutil
import subprocess
import tkinter as tk
from tkinter import Listbox, filedialog, messagebox

# Main Application
class GamessJobQueueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GAMESS Job Automation")

        # Path to GAMESS folder
        self.gamess_path_label = tk.Label(root, text="Path to GAMESS folder:")
        self.gamess_path_label.grid(row=0, column=0, padx=5, pady=5)
        self.gamess_path_entry = tk.Entry(root, width=50)
        self.gamess_path_entry.grid(row=0, column=1, padx=5, pady=5)

        # Version of GAMESS
        self.gamess_version_label = tk.Label(root, text="GAMESS Version (e.g., '2023.R1.intel'):")
        self.gamess_version_label.grid(row=1, column=0, padx=5, pady=5)
        self.gamess_version_entry = tk.Entry(root, width=50)
        self.gamess_version_entry.grid(row=1, column=1, padx=5, pady=5)

        # Number of cores
        self.num_cores_label = tk.Label(root, text="Number of Cores:")
        self.num_cores_label.grid(row=2, column=0, padx=5, pady=5)
        self.num_cores_entry = tk.Entry(root, width=50)
        self.num_cores_entry.grid(row=2, column=1, padx=5, pady=5)

        # Done Jobs List
        self.done_jobs_label = tk.Label(root, text="List of Done Jobs:")
        self.done_jobs_label.grid(row=3, column=0, padx=5, pady=5)
        self.done_jobs_list = Listbox(root, height=10, width=50)
        self.done_jobs_list.grid(row=4, column=0, padx=5, pady=5)

        # Clear Done Jobs Button
        self.clear_done_button = tk.Button(root, text="Clear List of Done Jobs", command=self.clear_done_jobs)
        self.clear_done_button.grid(row=5, column=0, padx=5, pady=5)

        # Input Queue
        self.input_queue_label = tk.Label(root, text="Input Queue (.inp files):")
        self.input_queue_label.grid(row=3, column=1, padx=5, pady=5)
        self.input_queue_list = Listbox(root, height=10, width=50)
        self.input_queue_list.grid(row=4, column=1, padx=5, pady=5)

        # Add Files Button
        self.add_files_button = tk.Button(root, text="Add .inp Files", command=self.add_to_queue)
        self.add_files_button.grid(row=5, column=1, padx=5, pady=5)

        # Submit Button
        self.submit_button = tk.Button(root, text="Submit Input", command=self.submit_input)
        self.submit_button.grid(row=6, column=1, padx=5, pady=5)

        # Job Queue
        self.job_queue = []

    def add_to_queue(self):
        # Add files to the input queue via file dialog
        files = filedialog.askopenfilenames(filetypes=[("GAMESS Input Files", "*.inp")])
        for file in files:
            if file.endswith('.inp'):
                self.job_queue.append(file)
                self.input_queue_list.insert(tk.END, file)  # Ensure it shows up in the GUI

    def submit_input(self):
        # Submit job if there's one in the queue
        if self.job_queue:
            inp_file = self.job_queue.pop(0)
            self.input_queue_list.delete(0)

            gamess_path = self.gamess_path_entry.get()
            gamess_version = self.gamess_version_entry.get()
            num_cores = self.num_cores_entry.get()

            if not gamess_path:
                messagebox.showerror("Error", "Please provide the GAMESS folder path.")
                return
            if not gamess_version:
                messagebox.showerror("Error", "Please provide the GAMESS version.")
                return
            if not num_cores.isdigit() or int(num_cores) <= 0:
                messagebox.showerror("Error", "Please provide a valid number of cores.")
                return

            # Copy the .inp file to the GAMESS directory
            try:
                shutil.copy(inp_file, gamess_path)
            except Exception as e:
                messagebox.showerror("Error", "Failed to copy input file to GAMESS directory: {0}".format(e))
                return

            # Prepare GAMESS command
            job_name = os.path.basename(inp_file)
            log_file = job_name.replace('.inp', '.log')

            try:
                # Change the working directory to the GAMESS folder
                os.chdir(gamess_path)

                # Construct the command to run GAMESS
                command = ["rungms.bat", job_name, gamess_version, num_cores, log_file]

                # Display the command for debugging purposes
                print("Running command:", ' '.join(command))

                # Run the GAMESS command
                subprocess.call(command, shell=True)

                # If the job completes successfully, add to the done jobs list
                self.done_jobs_list.insert(tk.END, job_name)
            except Exception as e:
                messagebox.showerror("Error", "Failed to run job {0}: {1}".format(job_name, e))

            # Schedule the next job
            if self.job_queue:
                self.root.after(1000, self.submit_input)

    def clear_done_jobs(self):
        # Clear the done jobs list
        self.done_jobs_list.delete(0, tk.END)

# Main Program Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = GamessJobQueueApp(root)
    root.mainloop()
