# Step 1: Base Image
FROM --platform=linux/amd64 ubuntu:20.04

# Step 2: Install Dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y wget
RUN apt-get install sox ffmpeg libcairo2 libcairo2-dev -y

# Step 3: Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh
RUN bash /miniconda.sh -b -p /miniconda
ENV PATH="/miniconda/bin:${PATH}"

# Step 4: Set Working Directory
WORKDIR /app

# Step 5: Copy Conda Environment File
COPY linux_environment.yml /app/linux_environment.yml

RUN uname -a
# Step 6: Create Conda Environment
RUN conda env create -f linux_environment.yml

# Step 7: Activate Conda Environment
# Replace 'py311' with the name of your Conda environment
SHELL ["conda", "run", "-n", "py311", "/bin/bash", "-c"]

# Step 8: Copy Application Code
COPY . /app

# Step 9: Expose Port
EXPOSE 8501

# Step 10: CMD to Run Streamlit
CMD ["conda", "run", "-n", "py311", "streamlit", "run", "your_app.py"]
