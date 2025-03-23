# FloppyFetch

![image](https://github.com/user-attachments/assets/5782c65d-7fa0-460a-9260-cf0035f5f81e)


FloppyFetch is a Windows-based clone of Neofetch, crafted in Python. It allows you to customize the color of the ASCII art and border, and displays all your system statistics in a visually appealing manner, similar to Neofetch.

## Features

- Customizable ASCII art and border colors.
- Displays comprehensive system statistics.
- Easy to install and run on Windows.

## Installation

1. **Clone the Repository:**

   Open PowerShell and run the following command to clone the repository:

   ```powershell
   git clone https://github.com/prot1en/floppyfetch.git
   ```

2. **Navigate to the Project Directory:**

    ```powershell
    cd floppyfetch
    ```

3. **Install Dependencies:**

    Ensure you have Python installed on your system. Then, install the required dependencies using:

    ```powershell
    pip install -r requirements.txt
    ```

## Usage

1. **Run floppyfetch:**

     You can run FloppyFetch by executing the following command in PowerShell:

     ```powershell
     python floppyfetch.py
     ```

   **Simplify the Command:**

     If you want to make the command simpler, you can add an alias to your PowerShell profile. Open your PowerShell profile in Notepad by running:

     ```powershell
     notepad $PROFILE
     ```

     Add the following line to the file:

     ```powershell
     function floppyfetch {
        param(
           [string[]]$args = @()
          )

        # Check for help options
        if ($args -contains '-h' -or $args -contains '--help') {
           Write-Host "Usage: floppyfetch [--color COLOR]"
           Write-Host "Fetch system information with a custom border color."
           Write-Host ""
           Write-Host "Options:"
           Write-Host "  -h, --help    Show this help message and exit"
           Write-Host "  --color COLOR Border color for the panel"
           return
        }

        # Construct the command with any additional arguments, excluding the directory path for help options
        $directoryPath = (Get-Location).Path
        $commandArgs = $args -join " "
        $command = "python $HOME/Desktop/python/floppyfetch/floppyfetch.py $commandArgs"

        # Invoke the command
        Invoke-Expression $command
    }
     ```

   Replace the path to floppyfetch.py with the actual path to your floppyfetch.py file. After saving the file, you can run FloppyFetch using:

   ```powershell
   floppyfetch
   ```

3. **Customize Colors:**

   To customize the colors of the ASCII art and border, you can modify the configuration settings within the script or through command-line arguments (run floppyfetch -h or python floppyfetch.py -h for more info).

## Up Next

1. **Multiple ASCII Art Options**

   In the upcoming updates, we plan to introduce a feature that allows you to switch between multiple ASCII art designs for the display screen. Stay tuned for more customization options!




