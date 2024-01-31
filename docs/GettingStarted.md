
## Getting Started

The steps below will help you to have a fully set-up environment to explore and interact with the Jupyter notebooks. If you're new to Jupyter notebooks, you might want to [check out some resources](https://jupyter.org/) on how to use them effectively.

1. **Clone the Repository**

    Begin by cloning the repository to your local machine. Use the command below in your terminal or command prompt:
   ```bash
   git clone https://github.com/DaveCasson/ForecastFloodImpact.git
   ```
    This command will create a copy of the repository in your current directory.

2. **Set Up Virtual Environment (Optional)**  

    It's a good practice to use a virtual environment for Python projects. This isolates your project's dependencies from other projects. To create and activate a virtual environment, run:
   ```bash
   python -m venv forecastfloodimpact
   source forecastfloodimpact/bin/activate  # For Windows, use `env\Scripts\activate`
   ```
    This step creates a new virtual environment named `forecastfloodimpact` and activates it.

3. **Install Dependencies**  

    With your virtual environment activated, install the required Python packages using:

   ```bash
   pip install -r requirements.txt
   ```

    This command reads the requirements.txt file and installs all the necessary packages to run the notebooks.

4. **Navigate to the Notebooks Directory**  
   ```bash
   cd notebooks/
   ```

5. **Start Jupyter Notebook**  

    Finally, start the Jupyter Notebook server:
   ```bash
   jupyter notebook
   ```
    This command will open a new tab in your default web browser with the Jupyter Notebook interface, where you can open and run the notebooks.
