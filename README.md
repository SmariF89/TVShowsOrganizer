# TVShowsOrganizer
A script which filters out a messy download folder's TV shows and organizes them neatly in another folder.

This script should work fine with any unorganized downloads folder containing TV shows.
The repository contains one huge messy downloads folder to try out the script with, however. Don't worry, its files are 0 bytes and it is perfectly safe to download.

## Usage
  - If desired, unzip downloads.zip in the same location as clean.py.
  - Using your favorite shell, type in "./clean \<Downloads folder name\> \<Organized folder name\>"
  - Note: The quickest way to try this script is to have it located in the same folder as the downloads folder - that way avoiding having to type in lengthy folder paths.
  
The first argument is the name of the downloads folder, the second argument is the name of the folder which to the organized TV shows will be moved. The script will create the folder if it does not exist. 

The script will create a folder structure like this \<Organized folder name\>\/\<TV show name\>\/\<Season number #\>\/\<TV shows\>.
  
## Note
This script may not be perfect but it is quite near it. For example, for the provided downloads folder, it organizes it with 92% correctness.
