# Step 1: Use an official light-weight Python base image
FROM python:3.11-slim

# Step 2: Set the directory inside the container where our code will live
WORKDIR /app

# Step 3: Copy the requirements file from your computer into the container
COPY requirements.txt .

# Step 4: Run pip install inside the container to install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy all remaining project files from your computer into the container
COPY . .

# Step 6: Inform Docker that the container listens on port 5000 at runtime
EXPOSE 5000

# Step 7: Tell Docker exactly where the file is located now
CMD ["python", "backend_dir/app.py"]