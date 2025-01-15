# Step 1: Use a lightweight Python base image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file to the container
COPY requirements.txt .

# Step 4: Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the project files into the container
COPY . .

# Step 6: Specify the command to run the ETL script
CMD ["python", "etl.py"]
