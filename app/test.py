import kagglehub

# Download latest version
path = kagglehub.dataset_download("parulpandey/indian-cities-database")

print("Path to dataset files:", path)