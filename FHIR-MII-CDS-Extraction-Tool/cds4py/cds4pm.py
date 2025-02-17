import customtkinter as ctk
from fhir.capabilities import get_fhir_capabilities
import threading
import time

class URLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Eingabe")
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"

        self.current_step = 0
        self.steps = [
            self.step_url_entry,
            self.step_show_capabilities
        ]

        self.url_entry = None
        self.progress_bar = None
        self.error_label = None
        self.setup_ui()

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.next_button = ctk.CTkButton(self.root, text="Next", command=self.next_step)
        self.next_button.pack(pady=20)

        self.steps[self.current_step]()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def step_url_entry(self):
        self.clear_frame()

        self.url_label = ctk.CTkLabel(self.frame, text="Please insert the base FHIR URL:", font=ctk.CTkFont(size=14))
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(self.frame, width=400, height=40)
        self.url_entry.pack(pady=5)

        # Set default value
        default_url = "http://localhost:8080/fhir"
        self.url_entry.insert(0, default_url)

        if self.error_label:
            self.error_label.pack_forget()
            self.error_label = None

    def step_show_capabilities(self):
        url = self.url_entry.get()  # Get the URL before clearing the frame

        self.clear_frame()

        capabilities_label = ctk.CTkLabel(self.frame, text="Loading FHIR Server Capabilities...", font=ctk.CTkFont(size=14))
        capabilities_label.pack(pady=10)

        # Add progress bar
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Start loading capabilities in a new thread
        thread = threading.Thread(target=self.load_capabilities, args=(url,))
        thread.start()

    def load_capabilities(self, url):
        try:
            # Simulate loading progress
            for i in range(10):
                self.progress_bar.set(i/10)
                time.sleep(0.1)

            # Attempt to get FHIR capabilities with a timeout
            capabilities = get_fhir_capabilities(url)

            # Update UI with capabilities
            self.display_capabilities(capabilities)
        except Exception as e:
            # Display error message
            self.display_error(str(e))

    def display_capabilities(self, capabilities):
        self.clear_frame()

        capabilities_label = ctk.CTkLabel(self.frame, text="FHIR Server Capabilities:", font=ctk.CTkFont(size=14))
        capabilities_label.pack(pady=10)

        # Create a CTkScrollableFrame
        scrollable_frame = ctk.CTkScrollableFrame(self.frame, width=400, height=200)
        scrollable_frame.pack(pady=10, fill="both", expand=True)

        # Add each capability to the scrollable frame
        for capability in capabilities:
            capability_label = ctk.CTkLabel(scrollable_frame, text=capability, font=ctk.CTkFont(size=12))
            capability_label.pack(anchor="w", padx=10, pady=2)

    def display_error(self, message):
        self.clear_frame()

        self.url_label = ctk.CTkLabel(self.frame, text="Please insert the base FHIR URL:", font=ctk.CTkFont(size=14))
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(self.frame, width=400, height=40)
        self.url_entry.pack(pady=5)

        # Set default value
        default_url = "http://localhost:8080/fhir"
        self.url_entry.insert(0, default_url)

        self.error_label = ctk.CTkLabel(self.frame, text=message, font=ctk.CTkFont(size=12), text_color="red")
        self.error_label.pack(pady=5)

    def next_step(self):
        if self.current_step == 0:
            url = self.url_entry.get()
            if not url:
                ctk.CTkMessagebox.show_warning("Warnung", "Bitte geben Sie eine URL ein.")
                return

        self.current_step += 1
        if self.current_step < len(self.steps):
            self.steps[self.current_step]()
        else:
            ctk.CTkMessagebox.show_info("Info", "Keine weiteren Schritte vorhanden.")
            self.root.quit()

if __name__ == "__main__":
    root = ctk.CTk()
    app = URLApp(root)
    root.mainloop()
